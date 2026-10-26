# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

司小宝（cmt.chinaway.com.lite）driverLogin 链路 —— 本地 mock 服务端。

课件结论（day24）：
  * 请求 https://g7s.ucenter.huoyunren.com/inside.php，method=POST
  * sign = quote_plus(base64(HMAC-SHA1("1KMrg0dfufc0wpnXEJacEQX1YEUYA0Ja",
                                      "POST\\n{ts}\\n/inside.php")))
  * mobile / password = hex_upper(base64(RSA/ECB/PKCS1Padding(明文)))
  * referer 固定 d507c00281c733bd693e5049ea33ad7e

线上服务端的 RSA 私钥拿不到，所以这里生成一对本地 1024 位密钥，
只用来验证"客户端加密方式是否正确"，签名密钥保持课件原值不动。

启动：python mock_server.py [端口]
"""
import base64
import hashlib
import hmac
import json
import os
import socketserver
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote_plus, urlparse

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

SIGN_KEY = b"1KMrg0dfufc0wpnXEJacEQX1YEUYA0Ja"
REFERER = "d507c00281c733bd693e5049ea33ad7e"
MOCK_USER = {"mobile": "18953675221", "password": "lqz12345"}
TS_WINDOW = 300  # 秒

HERE = os.path.dirname(os.path.abspath(__file__))
PRIV_PATH = os.path.join(HERE, "mock_rsa_private.pem")
PUB_PATH = os.path.join(HERE, "mock_rsa_public.pem")


def ensure_keypair():
    """本地没有密钥就生成一对 1024 位 RSA（与课件公钥位数一致）。"""
    if not (os.path.exists(PRIV_PATH) and os.path.exists(PUB_PATH)):
        key = RSA.generate(1024)
        with open(PRIV_PATH, "wb") as f:
            f.write(key.export_key())
        with open(PUB_PATH, "wb") as f:
            f.write(key.publickey().export_key())
        print("[mock] 已生成本地 RSA 密钥对", flush=True)
    with open(PRIV_PATH, "rb") as f:
        return RSA.import_key(f.read())


PRIV_KEY = None


def calc_sign(ts):
    msg = ("POST\n%s\n/inside.php" % ts).encode("utf-8")
    return quote_plus(base64.b64encode(hmac.new(SIGN_KEY, msg, hashlib.sha1).digest()).decode())


def decrypt_field(hex_text):
    """hex_upper(base64(RSA_PKCS1v15(明文))) -> 明文；格式不对抛 ValueError。"""
    if not hex_text or len(hex_text) % 2:
        raise ValueError("hex 长度非法")
    raw = bytes.fromhex(hex_text)
    b64 = raw.decode("ascii")
    data = base64.b64decode(b64)
    sentinel = b"\x00" * 32
    plain = PKCS1_v1_5.new(PRIV_KEY).decrypt(data, sentinel)
    if plain == sentinel:
        raise ValueError("RSA 解密失败")
    return plain.decode("utf-8")


class _Server(ThreadingHTTPServer):
    """跳过 getfqdn：中文 Windows 主机名下 server_bind 会抛 UnicodeDecodeError。"""

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        self.server_name = "127.0.0.1"
        self.server_port = self.server_address[1]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stdout.write("[mock] %s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _query(self):
        return {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        return {k: v[0] for k, v in parse_qs(raw).items()}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/__mock/pubkey":
            with open(PUB_PATH, "r", encoding="utf-8") as f:
                self._send({"code": 0, "msg": "ok", "data": {"pubkey": f.read()}})
            return
        self._send({"code": 404, "msg": "no such api"}, 404)

    def do_POST(self):
        if urlparse(self.path).path != "/inside.php":
            self._send({"code": 404, "msg": "no such api"}, 404)
            return
        q = self._query()
        form = self._body()
        ts = q.get("g7timestamp", "")
        sign = q.get("sign", "")
        print("[mock] 收到登录请求 ts=%s sign=%s" % (ts, sign), flush=True)

        if q.get("m") != "mobileinfo" or q.get("f") != "driverLogin":
            self._send({"code": 1004, "msg": "参数缺失"})
            return
        expect = calc_sign(ts)
        if sign != expect:
            print("[mock] 签名不匹配 期望=%s" % expect, flush=True)
            self._send({"code": 1002, "msg": "签名错误"})
            return
        try:
            if abs(time.time() - int(ts) / 1000.0) > TS_WINDOW:
                self._send({"code": 1003, "msg": "时间戳过期"})
                return
        except ValueError:
            self._send({"code": 1004, "msg": "时间戳非法"})
            return
        if q.get("referer") != REFERER:
            self._send({"code": 1004, "msg": "referer 非法"})
            return
        try:
            mobile = decrypt_field(form.get("mobile", ""))
            password = decrypt_field(form.get("password", ""))
        except Exception as exc:
            print("[mock] 解密失败: %r" % exc, flush=True)
            self._send({"code": 1005, "msg": "密文解析失败"})
            return
        if mobile != MOCK_USER["mobile"] or password != MOCK_USER["password"]:
            print("[mock] 账号或密码错误 mobile=%s" % mobile, flush=True)
            self._send({"code": 1001, "msg": "用户名或密码错误"})
            return
        token = base64.b16encode(os.urandom(20)).decode().lower()
        print("[mock] 登录成功 mobile=%s token=%s" % (mobile, token), flush=True)
        self._send({"code": 0, "msg": "ok",
                    "data": {"token": token, "uid": 10086, "mobile": mobile,
                             "equipment": form.get("equipment", "")}})


def main():
    global PRIV_KEY
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8018
    PRIV_KEY = ensure_keypair()
    srv = _Server(("127.0.0.1", port), Handler)
    print("[mock] 监听 http://127.0.0.1:%d" % port, flush=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
