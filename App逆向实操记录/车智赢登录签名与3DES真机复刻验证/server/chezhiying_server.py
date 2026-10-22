# -*- coding: utf-8 -*-
"""
车智赢登录接口复刻服务端（仅限学习研究，禁止商用）。

复刻 day14 抓包结论里的三个加密点：
  1. pwd  = md5(明文) 小写
  2. udid = Base64( 3DES-CBC/PKCS5( imei|nanoTime|deviceId ) )，key 取 24 字节，iv=appapich
  3. _sign = md5( KEY_V2 + 按 key 排序的 k+v 拼接 + KEY_V2 ) 大写

服务端独立重算这三个值，App 与 Python 脚本谁能通过，就说明谁的实现与课件口径一致。
"""
import base64
import hashlib
import json
import os
import time
from datetime import datetime

from Crypto.Cipher import DES3
from flask import Flask, jsonify, request

KEY_FULL = "appapiche168comappapiche168comap"
DES_KEY = KEY_FULL[:24].encode("utf-8")
IV = b"appapich"
SALT_V2 = "W@oC!AH_6Ew1f6%8"

USERS = {"13800138000": "123456"}
REQUIRED = ("_appid", "appversion", "channelid", "udid", "pwd", "_sign")

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "request_log.jsonl")


def md5_lower(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def des3_encrypt(plain):
    data = plain.encode("utf-8")
    pad = 8 - len(data) % 8
    data = data + bytes([pad]) * pad
    cipher = DES3.new(DES_KEY, DES3.MODE_CBC, IV)
    return base64.b64encode(cipher.encrypt(data)).decode("ascii")


def des3_decrypt(cipher_text):
    raw = base64.b64decode(cipher_text)
    cipher = DES3.new(DES_KEY, DES3.MODE_CBC, IV)
    data = cipher.decrypt(raw)
    pad = data[-1]
    return data[:-pad].decode("utf-8", "replace")


def calc_sign(params):
    raw = SALT_V2 + "".join(k + params[k] for k in sorted(params) if k != "_sign") + SALT_V2
    return md5_lower(raw).upper()


def write_log(record):
    with open(LOG_PATH, "a", encoding="utf-8") as fp:
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.route("/health")
def health():
    return jsonify(code=0, msg="ok", service="chezhiying-login-repl")


@app.route("/tradercloud/sealed/login/login.ashx", methods=["POST"])
def login():
    params = {k: v for k, v in request.form.items()}
    errors = []

    for key in REQUIRED:
        if key not in params:
            errors.append("缺少字段 %s" % key)

    username = params.get("username", "")
    if username not in USERS:
        errors.append("账号不存在：%s" % username)
    elif params.get("pwd") != md5_lower(USERS[username]):
        errors.append("pwd 与 md5(明文) 不符")

    udid_plain = ""
    if params.get("udid"):
        try:
            udid_plain = des3_decrypt(params["udid"])
            if len(udid_plain.split("|")) != 3:
                errors.append("udid 明文不是三段：%r" % udid_plain)
        except Exception as exc:
            errors.append("udid 解密失败：%s" % exc)

    if params.get("_sign") and params.get("_sign") != calc_sign(params):
        errors.append("_sign 校验不通过")

    token = md5_lower(username + str(time.time()))[:32]
    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "client": request.remote_addr,
        "params": params,
        "udid_plain": udid_plain,
        "expect_sign": calc_sign(params) if params.get("_sign") else "",
        "ok": not errors,
        "errors": errors,
    }
    write_log(record)

    if errors:
        print("[FAIL] %s -> %s" % (username, "；".join(errors)))
        return jsonify(code=1001, msg="；".join(errors), data=record)

    print("[OK] %s sign=%s udid_plain=%s" % (username, params["_sign"], udid_plain))
    return jsonify(code=0, msg="登录成功", data={
        "token": token,
        "udid_plain": udid_plain,
        "sign": params["_sign"],
    })


if __name__ == "__main__":
    print("listen 0.0.0.0:8000, log -> %s" % LOG_PATH)
    app.run(host="0.0.0.0", port=8000, threaded=True)
