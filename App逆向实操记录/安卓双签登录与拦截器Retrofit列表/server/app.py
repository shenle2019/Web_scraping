# -*- coding: utf-8 -*-
"""本地靶场（仅限学习研究，禁止商用）。

复刻 day10 课件的登录加签链路，并在此基础上升级为两级签名：
  1) 请求头：ctime + hsign = md5(ctime + SALT)，服务端校验 ±300s 防重放
  2) 请求体：sign = md5(t1 + user + md5(pwd))，服务端按同口径复算
  3) /films 需要 Authorization: Bearer <token>
所有校验失败都会写日志，便于和抓包结果逐条对照。

启动：python app.py        # 0.0.0.0:8080
"""
import hashlib
import json
import os
import socket
import time
import uuid

from flask import Flask, jsonify, request, send_from_directory

import make_covers

# Windows 中文主机名下 socket.getfqdn() 会抛 UnicodeDecodeError（本机 Python 3.8 实测），
# werkzeug 启动时会调用它，这里固定成本地回环名绕过系统主机名解析。
socket.getfqdn = lambda name="": "localhost"

app = Flask(__name__)

HERE = os.path.dirname(os.path.abspath(__file__))
COVER_DIR = make_covers.ensure_covers()
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "access.log")

SALT = "SJH_2026_APP"
SKEW_SECONDS = 300          # 时间戳允许的偏差
USERS = {
    "justin": hashlib.md5(b"123456").hexdigest(),
    "alice": hashlib.md5(b"888888").hexdigest(),
}
TOKENS = {}                 # token -> user，进程内存即可，重启后失效


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def log(line):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("[%s] %s\n" % (stamp, line))


@app.before_request
def check_header_sign():
    """一级校验：请求头时间戳 + 盐值签名，任何业务接口都要过。"""
    if request.path.startswith("/cover/") or request.path == "/":
        return None

    ctime = request.headers.get("ctime", "")
    hsign = request.headers.get("hsign", "")
    ua = request.headers.get("X-Client", "")

    if not ctime.isdigit():
        log("[REJECT-HEADER] path=%s 缺少或非法 ctime=%r client=%r" % (request.path, ctime, ua))
        return jsonify(code=103, msg="缺少或非法 ctime 请求头"), 400

    drift = abs(time.time() - int(ctime))
    if drift > SKEW_SECONDS:
        log("[REJECT-HEADER] path=%s ctime=%s 偏差 %.0fs 超限" % (request.path, ctime, drift))
        return jsonify(code=103, msg="ctime 过期，判定为重放", drift=int(drift)), 400

    expect = md5(ctime + SALT)
    if hsign != expect:
        log("[REJECT-HEADER] path=%s ctime=%s hsign=%s 期望=%s" % (request.path, ctime, hsign, expect))
        return jsonify(code=103, msg="hsign 校验失败", expect=expect), 400

    log("[HEADER-OK] path=%s ctime=%s hsign=%s client=%r" % (request.path, ctime, hsign, ua))
    return None


@app.after_request
def add_server_time(resp):
    resp.headers["X-Server-Time"] = str(int(time.time()))
    return resp


@app.route("/")
def index():
    return jsonify(code=100, msg="netapp local lab", endpoints=["/login", "/films", "/cover/<id>.png"])


@app.route("/login", methods=["POST"])
def login():
    """二级校验：业务体签名 sign = md5(t1 + user + md5(pwd))。"""
    user = request.form.get("user", "")
    pwd = request.form.get("pwd", "")        # 客户端已 md5 过的密码
    t1 = request.form.get("t1", "")
    sign = request.form.get("sign", "")
    expect = md5(t1 + user + pwd)

    log("[LOGIN] user=%r pwd=%s t1=%s sign=%s expect=%s" % (user, pwd, t1, sign, expect))

    if not t1.isdigit() or abs(time.time() - int(t1)) > SKEW_SECONDS:
        log("[LOGIN-FAIL] t1 无效或过期: %r" % t1)
        return jsonify(code=102, msg="t1 无效或已过期")

    if sign != expect:
        log("[LOGIN-FAIL] body sign 不匹配 收到=%s 期望=%s" % (sign, expect))
        return jsonify(code=102, msg="body sign 校验失败", expect=expect)

    real_pwd = USERS.get(user)
    if real_pwd is None:
        log("[LOGIN-FAIL] 用户不存在: %r" % user)
        return jsonify(code=101, msg="用户不存在")

    if pwd != real_pwd:
        log("[LOGIN-FAIL] 密码错误 user=%r 收到=%s 期望=%s" % (user, pwd, real_pwd))
        return jsonify(code=101, msg="密码错误")

    token = uuid.uuid4().hex
    TOKENS[token] = user
    log("[LOGIN-OK] user=%s token=%s" % (user, token))
    return jsonify(code=100, msg="登录成功", token=token, user=user)


@app.route("/films")
def films():
    """三级校验：token 鉴权，token 由登录接口下发。"""
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.startswith("Bearer ") else ""
    if token not in TOKENS:
        log("[FILMS-401] token=%r 无效或未登录" % token)
        return jsonify(code=401, msg="token 无效或已过期"), 401

    with open(os.path.join(HERE, "films.json"), encoding="utf-8") as f:
        rows = json.load(f)

    host = request.host_url.rstrip("/")
    for row in rows:                       # 相对路径补成绝对地址，Glide 才能直接加载
        row["cover"] = host + row["cover"]

    log("[FILMS-OK] user=%s count=%d" % (TOKENS[token], len(rows)))
    return jsonify(code=100, msg="ok", data=rows)


@app.route("/cover/<path:name>")
def cover(name):
    return send_from_directory(COVER_DIR, name, mimetype="image/png")


if __name__ == "__main__":
    log("===== server start =====")
    print("netapp lab listening on 0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)
