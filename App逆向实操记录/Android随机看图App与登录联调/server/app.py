# -*- coding: utf-8 -*-
"""day09 登录案例后端（Flask）。

与课件保持一致：App 用 application/x-www-form-urlencoded 提交 username/password，
服务端校验成功返回 token，失败返回错误码。
课件原版成功/失败都返回 code=100，这里把失败改为 101，便于客户端区分。

运行：python app.py
监听：0.0.0.0:8080（真机可用局域网 IP，或 adb reverse 后走 127.0.0.1）
仅用于本地联调学习。
"""
import io
import secrets
import socket

from flask import Flask, jsonify, request, send_file

# 中文 Windows 主机名下 socket.getfqdn 会按 GBK 解码失败（UnicodeDecodeError），
# 这里做一层兜底，避免开发服务器启动即崩。
_raw_getfqdn = socket.getfqdn


def _safe_getfqdn(name=""):
    try:
        return _raw_getfqdn(name)
    except Exception:
        return "localhost"


socket.getfqdn = _safe_getfqdn

app = Flask(__name__)
TOKEN = secrets.token_hex(16)


@app.post("/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    print("[login] username=%r password=%r from=%r ua=%r" % (
        username, password, request.headers.get("X-From"),
        request.headers.get("User-Agent")), flush=True)
    if username == "justin" and password == "123":
        return jsonify({"code": 100, "msg": "登录成功", "token": TOKEN})
    return jsonify({"code": 101, "msg": "用户名或密码错误"})


@app.get("/photo")
def photo():
    """网络图片联调接口：动态生成一张渐变图，避免依赖任何外部素材。"""
    try:
        from PIL import Image, ImageDraw

        width, height = 720, 960
        img = Image.new("RGB", (width, height), "#FFF9F6")
        draw = ImageDraw.Draw(img)
        for y in range(height):
            ratio = y / float(height)
            r = int(255 - 20 * ratio)
            g = int(240 - 70 * ratio)
            b = int(238 - 66 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        draw.ellipse([width // 2 - 150, 250, width // 2 + 150, 550],
                     outline="#FFFFFF", width=6)
        draw.text((width // 2 - 118, 640), "NETWORK IMAGE OK", fill="#FFFFFF")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        print("[photo] served %dx%d png" % (width, height), flush=True)
        return send_file(buf, mimetype="image/png")
    except Exception as exc:  # PIL 缺失时退化为一像素 PNG，保证链路可测
        print("[photo] fallback:", exc, flush=True)
        png = bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
            "0000000d49444154789c6360000000020001e221bc330000000049454e44ae426082")
        return send_file(io.BytesIO(png), mimetype="image/png")


@app.get("/ping")
def ping():
    return "pong"


if __name__ == "__main__":
    print("token:", TOKEN, flush=True)
    app.run(host="0.0.0.0", port=8080, debug=False)
