# -*- coding: utf-8 -*-
"""
10：本地模拟站服务（Hook 演示站 · 模拟真实站点风控）
=========================================================
路由：
  GET /                      -> 商品列表页（server_assets/index.html）
  GET /static/main.js        -> 站点核心脚本（server_assets/main.js）
  GET /api/goods?page=&ts=   -> 数据接口（服务端双重风控校验）：
        ① Cookie access_token 必须 == sec_hash("atk|<UTC日期>|<SECRET_C>")
        ② 请求头 X-Sign       必须 == sec_hash("page=<page>&ts=<ts>|<SECRET_S>")
        任一不匹配 -> 403；全部通过 -> 200 + 商品 JSON

用法：
  python 10_local_server.py             # 前台启动，人工浏览 http://127.0.0.1:18888/
  python 10_local_server.py --selftest  # 自测：四种凭证组合验证双重风控（生成作业验证日志）
  爬虫脚本内：subprocess 启动本脚本，等待端口就绪后访问

合规声明：本地模拟站点，数据全部自造，无任何真实站点请求。
"""
import json
import os
import sys
import socketserver
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOST, PORT = "127.0.0.1", 18888
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "server_assets")

# 与 server_assets/main.js 中 eval 混淆段还原出的密钥一致
SECRET_C = "hk-demo-cookie-salt-2026"
SECRET_S = "hk-demo-sign-salt-2026"

GOODS = [
    {"id": 1001, "name": "机械键盘 87 键 茶轴", "price": 299},
    {"id": 1002, "name": "人体工学无线鼠标", "price": 199},
    {"id": 1003, "name": "27 英寸 2K 显示器", "price": 1099},
    {"id": 1004, "name": "降噪蓝牙耳机", "price": 649},
    {"id": 1005, "name": "升降办公桌 1.2m", "price": 899},
    {"id": 1006, "name": "人体工学椅 网布款", "price": 1299},
    {"id": 1007, "name": "USB-C 扩展坞 7 合 1", "price": 159},
    {"id": 1008, "name": "NVMe 固态硬盘 1TB", "price": 459},
    {"id": 1009, "name": "1080P 网络摄像头", "price": 219},
    {"id": 1010, "name": "桌面显示器支架臂", "price": 139},
    {"id": 1011, "name": "氮化镓充电器 65W", "price": 99},
    {"id": 1012, "name": "双肩电脑包 15.6 寸", "price": 189},
]


def sec_hash(s):
    """与页面 main.js 中 secHash 完全等价（djb2 变体双通道，输出 16 位 hex）

    已离线验证：Node 与 Python 两侧对同一样本输出一致
    """
    h1, h2 = 5381, 131
    for ch in s:
        c = ord(ch)
        h1 = (h1 * 33 + c) & 0xFFFFFFFF
        h2 = (h2 * 17 + c) & 0xFFFFFFFF
    return "%08x%08x" % (h1, h2)


def expected_token():
    """服务端期望的访问令牌（UTC 日期口径与页面 toISOString 一致）"""
    day = datetime.utcnow().strftime("%Y-%m-%d")
    return sec_hash("atk|" + day + "|" + SECRET_C)


def expected_sign(page, ts):
    """服务端期望的接口签名"""
    return sec_hash("page=%s&ts=%s|%s" % (page, ts, SECRET_S))


def parse_cookies(cookie_header):
    out = {}
    for part in (cookie_header or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


class DemoSiteServer(ThreadingHTTPServer):
    """修复：Windows 中文主机名下 HTTPServer.server_bind 里的 socket.getfqdn
    会抛 UnicodeDecodeError，这里跳过 FQDN 解析、直接使用监听地址。"""

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = host
        self.server_port = port


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stdout.write("[server] " + (fmt % args) + "\n")
        sys.stdout.flush()

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _serve_file(self, fp, ctype):
        if not os.path.isfile(fp):
            self._send_json(404, {"code": 404, "msg": "asset missing"})
            return
        with open(fp, "rb") as f:
            self._send(200, f.read(), ctype)

    def do_GET(self):
        u = urlparse(self.path)
        path = u.path
        if path in ("/", "/index.html"):
            self._serve_file(os.path.join(ASSETS_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/static/main.js":
            self._serve_file(os.path.join(ASSETS_DIR, "main.js"), "application/javascript; charset=utf-8")
        elif path == "/api/goods":
            self._api_goods(parse_qs(u.query))
        else:
            self._send_json(404, {"code": 404, "msg": "not found"})

    def _api_goods(self, q):
        page = (q.get("page") or ["1"])[0]
        ts = (q.get("ts") or [""])[0]

        # ① Cookie 令牌校验（模拟"登录态"风控）
        token = parse_cookies(self.headers.get("Cookie")).get("access_token", "")
        exp_token = expected_token()
        if token != exp_token:
            print("[server] 403 令牌校验失败 got=%s exp=%s" % (token[:16] or "(空)", exp_token))
            self._send_json(403, {"code": 403, "msg": "缺少有效访问令牌", "need": "access_token"})
            return

        # ② X-Sign 签名校验（模拟"参数防篡改"风控）
        sign = self.headers.get("X-Sign", "")
        exp_sign = expected_sign(page, ts)
        if sign != exp_sign:
            print("[server] 403 签名校验失败 got=%s exp=%s" % (sign or "(空)", exp_sign))
            self._send_json(403, {"code": 403, "msg": "签名验证失败"})
            return

        print("[server] 200 校验通过 page=%s ts=%s" % (page, ts))
        self._send_json(200, {"code": 0, "page": int(page), "total": len(GOODS), "items": GOODS})


def selftest():
    """--selftest：后台线程启动服务，用四种凭证组合请求接口，打印风控校验结果

    预期：无凭证 403 / 错误令牌 403 / 少签名 403 / 全对 200
    """
    import threading
    import time as _time
    import urllib.request
    import urllib.error

    srv = DemoSiteServer((HOST, PORT), Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    print("[selftest] 服务已启动: http://%s:%d/" % (HOST, PORT))

    good_token = expected_token()
    ts = str(int(_time.time() * 1000))
    good_sign = expected_sign("1", ts)
    url = "http://%s:%d/api/goods?page=1&ts=%s" % (HOST, PORT, ts)

    def request(cookies=None, sign=None):
        req = urllib.request.Request(url)
        if cookies:
            req.add_header("Cookie", cookies)
        if sign:
            req.add_header("X-Sign", sign)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    print("\n----- 服务端双重风控校验（四种凭证组合） -----")
    s1, b1 = request()
    print("  [1] 无任何凭证        -> HTTP %s %s" % (s1, b1.get("msg")))
    s2, b2 = request(cookies="access_token=wrong-token")
    print("  [2] 错误令牌          -> HTTP %s %s" % (s2, b2.get("msg")))
    s3, b3 = request(cookies="access_token=" + good_token)
    print("  [3] 正确令牌+无签名   -> HTTP %s %s" % (s3, b3.get("msg")))
    s4, b4 = request(cookies="access_token=" + good_token, sign=good_sign)
    print("  [4] 正确令牌+正确签名 -> HTTP %s total=%s" % (s4, b4.get("total")))

    ok = (s1 == 403 and s2 == 403 and s3 == 403
          and s4 == 200 and b4.get("total") == len(GOODS))
    print("\n  [%s] 双重风控行为符合预期（403/403/403/200）" % ("PASS" if ok else "FAIL"))
    print("\n[selftest] 结论: " + ("全部通过 —— 令牌与签名缺一不可" if ok else "存在失败项"))

    srv.shutdown()
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()

    srv = DemoSiteServer((HOST, PORT), Handler)
    print("[server] Hook 演示站已启动: http://%s:%d/  (Ctrl+C 退出)" % (HOST, PORT))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
