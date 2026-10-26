# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

酒仙网 v9.1.13 登录/预约链路 —— 本地 mock 服务端。

目的：课件里的接口本身没有签名（appKey/deviceIdentify 可去掉），风险点全在
"图形验证码 + 短信验证码 + token"。这里用本地服务端把这套链路完整复刻出来，
参数名、返回结构、错误码都对齐课件抓包内容，客户端脚本可以反复跑，不会碰真站。

启动：python mock_server.py [端口]
"""
import base64
import io
import json
import random
import socketserver
import string
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # 没装 Pillow 时退化成纯文本验证码
    Image = None

# 模拟手机号 -> 短信验证码
SMS_CODE = "1234"
# 模拟账号密码（本地假账号）
MOCK_USER = {"mobile": "15131255555", "password": "123456"}

CAPTCHA_STORE = {}   # (mobile, deviceIdentify) -> code
SMS_STORE = {}       # mobile -> code
TOKEN_STORE = {}     # token -> mobile
RESERVED = set()     # mobile 已预约

FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"


def make_captcha(code):
    """画一张带干扰线/噪点的 4 位数字验证码，返回 PNG 字节。"""
    if Image is None:
        return b""
    width, height = 120, 40
    img = Image.new("RGB", (width, height), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, 26)
    except Exception:
        font = ImageFont.load_default()
    for _ in range(4):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(random.randint(80, 200),) * 3, width=1)
    for i, ch in enumerate(code):
        draw.text((12 + i * 26, random.randint(2, 8)), ch, font=font,
                  fill=(random.randint(0, 90), random.randint(0, 90), random.randint(0, 90)))
    for _ in range(80):
        draw.point((random.randint(0, width), random.randint(0, height)),
                   fill=(random.randint(120, 220),) * 3)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class _Server(ThreadingHTTPServer):
    """跳过 getfqdn：中文 Windows 主机名下 HTTPServer 绑定会抛 UnicodeDecodeError。"""

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
        q = self._query()
        if path == "/messages/graphCode.htm":
            code = "".join(random.choice(string.digits) for _ in range(4))
            CAPTCHA_STORE[(q.get("mobile", ""), q.get("deviceIdentify", ""))] = code
            png = make_captcha(code)
            print("[mock] graphCode mobile=%s code=%s(仅服务端可见)" % (q.get("mobile"), code), flush=True)
            self._send({"result": {"imgCode": base64.b64encode(png).decode()},
                        "errCode": "", "success": "1", "errMsg": ""})
            return
        if path == "/messages/mobileCode.htm":
            key = (q.get("mobile", ""), q.get("deviceIdentify", ""))
            expect = CAPTCHA_STORE.get(key)
            if expect and q.get("code") == expect:
                SMS_STORE[q.get("mobile", "")] = SMS_CODE
                print("[mock] mobileCode ok mobile=%s 已下发短信验证码 %s" % (q.get("mobile"), SMS_CODE), flush=True)
                self._send({"result": "", "errCode": "", "success": "1", "errMsg": ""})
            else:
                self._send({"result": "", "errCode": "1200013", "success": "0", "errMsg": "验证码输入错误"})
            return
        if path == "/__mock/sms":
            mobile = q.get("mobile", "")
            code = SMS_STORE.get(mobile)
            print("[mock] 查询短信验证码 mobile=%s code=%s" % (mobile, code), flush=True)
            self._send({"result": {"code": code}, "errCode": "", "success": "1" if code else "0", "errMsg": ""})
            return
        if path == "/reservation/preReservation.htm":
            token = q.get("token", "")
            mobile = TOKEN_STORE.get(token)
            if not mobile:
                self._send({"result": {"verificationState": False}, "errCode": "1200001",
                            "success": "0", "errMsg": "登录已失效，请重新登录"})
                return
            if mobile in RESERVED:
                self._send({"result": {"verificationState": False}, "errCode": "1200601",
                            "success": "0", "errMsg": "您已预约成功，不需重复预约"})
                return
            RESERVED.add(mobile)
            self._send({"result": {"verificationState": True, "actId": q.get("actId"),
                                   "productId": q.get("productId")},
                        "errCode": "", "success": "1", "errMsg": ""})
            return
        self._send({"errCode": "404", "success": "0", "errMsg": "no such api"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        form = self._body()
        if path == "/user/loginMobileFast.htm":
            mobile, code = form.get("mobile", ""), form.get("verifyCode", "")
            if not SMS_STORE.get(mobile) or code != SMS_STORE[mobile]:
                self._send({"result": "", "errCode": "1200003", "success": "0",
                            "errMsg": "验证码错误或已过期，请重新输入"})
                return
            token = "%032x%09d" % (random.getrandbits(128), random.randint(0, 999999999))
            TOKEN_STORE[token] = mobile
            SMS_STORE.pop(mobile, None)
            print("[mock] 短信登录成功 mobile=%s token=%s" % (mobile, token), flush=True)
            self._send({"result": {"userInfo": {"mobile": mobile, "token": token,
                                                "uid": 210440860, "uname": "mock_user"}},
                        "errCode": "", "success": "1", "errMsg": ""})
            return
        if path == "/user/loginUserNamePassWd.htm":
            mobile, pwd = form.get("userName", ""), form.get("passWord", "")
            if mobile != MOCK_USER["mobile"] or pwd != MOCK_USER["password"]:
                self._send({"result": "", "errCode": "1200002", "success": "0", "errMsg": "用户名或密码错误"})
                return
            token = "%032x%09d" % (random.getrandbits(128), random.randint(0, 999999999))
            TOKEN_STORE[token] = mobile
            print("[mock] 密码登录成功 mobile=%s token=%s" % (mobile, token), flush=True)
            self._send({"result": {"userInfo": {"mobile": mobile, "token": token,
                                                "uid": 210440860, "uname": "mock_user"}},
                        "errCode": "", "success": "1", "errMsg": ""})
            return
        self._send({"errCode": "404", "success": "0", "errMsg": "no such api"}, 404)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8008
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
