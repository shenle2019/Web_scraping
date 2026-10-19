# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""金树林接口本地 Mock 服务（仅用于学习，不连接真实业务）。

背景：课件目标站点 miappshop.jshulin.com 在 2026-10 已无法访问（域名可解析、
443 拒绝连接，外网同样如此），真实链路无法跑通。本服务按课件中已确认的
请求契约复刻 4 个接口，用于验证客户端脚本的完整链路逻辑：

  GET  /memberLogin/phoneCode      ?phone=&serviceType=5|6
  POST /memberLogin/memberRegister {phone, fid, password, phoneCode}
  POST /memberLogin/login          {username, password} -> JWT token
  POST /pro/searchByPage           Header: Mobile-Token -> 商品分页

响应字段（token/tokenLong/userInfo 结构、code/message 包裹）参照课件 8-登录.py
里保留的真实响应样例；服务端内部校验逻辑为自写，仅供链路演示。
"""
import base64
import hashlib
import hmac
import json
import socketserver
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOST, PORT = "127.0.0.1", 18080
SECRET = b"mock-secret-only-for-course"
FIXED_CODE = "123456"  # 真实环境由短信下发，Mock 直接返回便于自动化

USERS = {}       # phone -> password
CODES = {}       # phone -> code
SESSIONS = {}    # token -> username

PRODUCTS = [
    {"id": 1001, "name": "法国进口红酒 干红葡萄酒 750ml", "price": 199.0, "stock": 120},
    {"id": 1002, "name": "智利赤霞珠红酒 整箱6支装", "price": 268.0, "stock": 66},
    {"id": 1003, "name": "澳洲西拉子红酒 单支装", "price": 158.0, "stock": 88},
    {"id": 1004, "name": "西班牙丹魄红酒 礼盒装", "price": 328.0, "stock": 40},
    {"id": 1005, "name": "白酒 浓香型 52度 500ml", "price": 129.0, "stock": 200},
    {"id": 1006, "name": "干白葡萄酒 霞多丽 750ml", "price": 118.0, "stock": 75},
]


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_jwt(username, member_id, ttl):
    now = int(time.time())
    header = {"typ": "JWT", "alg": "HS256"}
    payload = {"aud": member_id, "exp": now + ttl, "iat": now,
               "userId": member_id, "username": username}
    seg = (b64url(json.dumps(header, separators=(",", ":")).encode())
           + "." + b64url(json.dumps(payload, separators=(",", ":")).encode()))
    sig = hmac.new(SECRET, seg.encode(), hashlib.sha256).digest()
    return seg + "." + b64url(sig)


def check_jwt(token):
    try:
        seg, sig = token.rsplit(".", 1)
        expect = b64url(hmac.new(SECRET, seg.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expect):
            return None
        payload_b64 = seg.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        if payload["exp"] < time.time():
            return None
        return payload
    except Exception:
        return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json;charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        print("[RESP] %s -> %s" % (self.path.split("?")[0], body[:160].decode("utf-8", "ignore")), flush=True)

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        print("[REQ ] GET %s params=%s" % (parsed.path, query), flush=True)

        if parsed.path == "/memberLogin/phoneCode":
            phone = query.get("phone", [""])[0]
            service_type = query.get("serviceType", [""])[0]
            if not phone or service_type not in ("5", "6"):
                self.send_json({"code": 20001, "message": "参数错误", "data": None})
                return
            CODES[phone] = FIXED_CODE
            self.send_json({
                "code": 10000,
                "message": "成功(本地 Mock)",
                "data": {"phoneCode": FIXED_CODE,
                         "serviceType": service_type,
                         "note": "真实环境验证码经短信下发，Mock 直接返回"},
            })
            return

        self.send_json({"code": 40400, "message": "not found", "data": None}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            self.send_json({"code": 20002, "message": "JSON 解析失败", "data": None})
            return
        print("[REQ ] POST %s body=%s" % (parsed.path, json.dumps(data, ensure_ascii=False)), flush=True)

        if parsed.path == "/memberLogin/memberRegister":
            phone = data.get("phone", "")
            code = data.get("phoneCode", "")
            pwd = data.get("password", "")
            if CODES.get(phone) != code:
                self.send_json({"code": 20003, "message": "验证码错误", "data": None})
                return
            USERS[phone] = pwd
            self.send_json({"code": 10000, "message": "注册成功(本地 Mock)", "data": None})
            return

        if parsed.path == "/memberLogin/login":
            username = data.get("username", "")
            if USERS.get(username) != data.get("password", ""):
                self.send_json({"code": 20004, "message": "用户名或密码错误", "data": None})
                return
            member_id = "18063294870547%05d" % (len(USERS) + 1)
            token = make_jwt(username, member_id, 600)
            token_long = make_jwt(username, member_id, 14400)
            SESSIONS[token] = username
            self.send_json({
                "code": 10000, "message": "成功",
                "data": {
                    "token": token, "tokenLong": token_long, "tokenOne": None,
                    "userInfo": {"nickName": username, "avatar": None,
                                 "memberId": member_id, "memberLevel": None,
                                 "agentId": None, "agentName": None, "agentLv": None,
                                 "phone": username, "cusId": None, "customerSeat": None},
                    "curCityName": None, "curCityNo": None, "phone": None,
                    "isNewMember": "0", "isReceive": "0", "isRiskAccount": "0",
                    "isFullPromoter": None,
                },
            })
            return

        if parsed.path == "/pro/searchByPage":
            token = self.headers.get("Mobile-Token", "")
            payload = check_jwt(token)
            if not payload or token not in SESSIONS:
                self.send_json({"code": 40100, "message": "token 无效或已过期", "data": None}, 401)
                return
            keyword = data.get("keyword", "")
            limit = int(data.get("limit") or 10)
            page = int(data.get("page") or 1)
            matched = [p for p in PRODUCTS if keyword in p["name"]]
            start = (page - 1) * limit
            self.send_json({
                "code": 10000, "message": "成功",
                "data": {"list": matched[start:start + limit],
                         "total": len(matched), "page": page, "limit": limit},
            })
            return

        self.send_json({"code": 40400, "message": "not found", "data": None}, 404)


class MockServer(ThreadingHTTPServer):
    """本机主机名含非 UTF-8 字节时，HTTPServer 默认的 server_bind -> getfqdn
    会在 Python 3.8 抛 UnicodeDecodeError，这里跳过 getfqdn 直接绑定。"""

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        self.server_name = HOST
        self.server_port = self.server_address[1]


if __name__ == "__main__":
    server = MockServer((HOST, PORT), Handler)
    print("[MOCK] listening on http://%s:%s" % (HOST, PORT), flush=True)
    server.serve_forever()
