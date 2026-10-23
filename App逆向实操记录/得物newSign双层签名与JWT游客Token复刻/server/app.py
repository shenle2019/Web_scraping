# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
# 仿真得物 4.74.5：newSign 签名校验 + X-Auth-Token 游客 token + 首页推荐流
# 只服务本机自建 App 与本地复刻脚本，不连接任何真实站点

import base64
import hashlib
import hmac
import json
import time

from flask import Flask, jsonify, make_response, request
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

AES_KEY = b"d245a0ba8d678a61"
JWT_SECRET = b"dewu-repl-secret"
LATEST_VERSION = "4.84.0"
APP_VERSION = "4.74.5"

app = Flask(__name__)

# 简单计数，用来复现"同一条件第 N 次触发"的现象
COUNTER = {"token": 0, "feed": 0}


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def aes_encrypt(text):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.encrypt(pad(text.encode("utf-8"), 16))


def sign_of(params):
    """newSign = md5(base64(aes_ecb(sorted(key+value) joined)))"""
    plain = "".join("%s%s" % (k, params[k]) for k in sorted(params) if k != "newSign")
    b64 = base64.b64encode(aes_encrypt(plain)).decode()
    return hashlib.md5(b64.encode()).hexdigest(), plain, b64


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def make_jwt(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url(json.dumps(header, separators=(",", ":")).encode())
    p = b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(JWT_SECRET, ("%s.%s" % (h, p)).encode(), hashlib.sha256).digest()
    return "%s.%s.%s" % (h, p, b64url(sig))


def parse_jwt(token):
    if not token:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    h, p, s = parts
    expect = b64url(hmac.new(JWT_SECRET, ("%s.%s" % (h, p)).encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(expect, s):
        return None
    payload = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
    if payload.get("exp", 0) < int(time.time()):
        return None
    return payload


def client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)


@app.get("/app/version")
def version():
    log("GET /app/version ip=%s ua=%s" % (client_ip(), request.headers.get("User-Agent", "")))
    log("    -> 版本检查，强制更新到 %s" % LATEST_VERSION)
    return jsonify({
        "code": 0,
        "data": {
            "force": True,
            "latest": LATEST_VERSION,
            "note": "本地复刻用：强制更新弹窗，验证断网启动/Hook 绕过",
        },
    })


@app.get("/app/ping")
def ping():
    log("GET /app/ping ip=%s ua=%s" % (client_ip(), request.headers.get("User-Agent", "")))
    return jsonify({"code": 0, "msg": "pong", "ip": client_ip()})


@app.post("/app/reset")
def reset():
    COUNTER["token"] = 0
    COUNTER["feed"] = 0
    log("POST /app/reset 计数清零")
    return jsonify({"code": 0})


@app.post("/api/v1/app/user_core/users/getVisitorUserId")
def visitor_token():
    body = request.get_json(force=True, silent=True) or {}
    uid = body.get("uuid", "")
    expect, plain, b64 = sign_of(body)
    got = body.get("newSign", "")
    log("POST /getVisitorUserId ip=%s uuid=%s" % (client_ip(), uid))
    log("    StringToSign = %s" % plain)
    log("    AES+Base64   = %s" % b64)
    log("    newSign 期望=%s 收到=%s" % (expect, got))

    if got != expect:
        return jsonify({"code": 456, "msg": "newSign 校验失败"}), 200

    COUNTER["token"] += 1
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 365 * 24 * 3600,
        "iss": uid,
        "sub": uid,
        "uuid": uid,
        "userId": 90000000 + COUNTER["token"],
        "userName": "得物er-%s" % uid[:8].upper(),
        "isGuest": True,
    }
    token = make_jwt(payload)
    resp = make_response(jsonify({
        "code": 0,
        "msg": "ok",
        "data": {"userId": payload["userId"], "isGuest": True},
    }))
    resp.headers["X-Auth-Token"] = token
    log("    -> 校验通过，签发 X-Auth-Token（JWT, isGuest=true）")
    return resp


FEED_TITLES = [
    ("球鞋", "Air Force 1 低帮 纯白", 699),
    ("球鞋", "Dunk Low 复古低帮", 899),
    ("潮服", "宽松落肩连帽卫衣", 329),
    ("配件", "尼龙单肩斜挎包", 259),
    ("球鞋", "复古慢跑鞋 灰白", 459),
    ("潮服", "水洗直筒牛仔裤", 389),
    ("配件", "棒球帽 刺绣小标", 129),
    ("球鞋", "板鞋 黑白熊猫配色", 799),
]


@app.get("/sns-rec/v1/recommend/all/feed")
def feed():
    payload = parse_jwt(request.headers.get("X-Auth-Token"))
    log("GET /feed ip=%s ua=%s params=%s" % (
        client_ip(), request.headers.get("User-Agent", ""), dict(request.args)))
    if not payload:
        log("    -> 401 X-Auth-Token 缺失或无效")
        return jsonify({"code": 401, "msg": "X-Auth-Token 无效"}), 401

    args = request.args
    sign_ok = None
    if args.get("newSign"):
        expect, plain, b64 = sign_of(dict(args))
        sign_ok = (expect == args.get("newSign"))
        log("    newSign 校验=%s（该接口允许不带，带了就顺带验一下）" % sign_ok)

    last_id = int(args.get("lastId", "0") or "0")
    limit = min(int(args.get("limit", "20") or "20"), 20)
    items = []
    for i in range(limit):
        idx = (last_id + i) % len(FEED_TITLES)
        cat, title, price = FEED_TITLES[idx]
        items.append({
            "id": "mock-%04d" % (last_id + i + 1),
            "category": cat,
            "title": title,
            "price": price,
            "isMock": True,
        })
    COUNTER["feed"] += 1
    log("    -> 200 返回 %d 条（uuid=%s, isGuest=%s）" % (len(items), payload.get("uuid"), payload.get("isGuest")))
    return jsonify({
        "code": 0,
        "msg": "ok",
        "data": {"items": items, "lastId": last_id + limit, "hasMore": True},
    })


if __name__ == "__main__":
    log("AES key=%s，JWT secret=%s" % (AES_KEY.decode(), JWT_SECRET.decode()))
    log("服务启动：0.0.0.0:8000（仅本地复刻，禁止商用）")
    app.run(host="0.0.0.0", port=8000, threaded=True)
