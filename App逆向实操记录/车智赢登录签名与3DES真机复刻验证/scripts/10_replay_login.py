# -*- coding: utf-8 -*-
"""
纯 Python 还原车智赢登录三参数，并调本地复刻服务端验证。
仅限学习研究，目标是自己搭建的本地服务。
用法：python scripts/10_replay_login.py
"""
import base64
import hashlib
import json
import os
import random
import sys

import requests
from Crypto.Cipher import DES3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = "http://192.168.31.220:8000"
LOGIN_PATH = "/tradercloud/sealed/login/login.ashx"
RESULT_PATH = os.path.join(BASE, "replay_result.json")

KEY_FULL = "appapiche168comappapiche168comap"
DES_KEY = KEY_FULL[:24].encode("utf-8")   # DESede 只取前 24 字节
IV = b"appapich"                          # SecurityUtil 里的私有常量
SALT_V2 = "W@oC!AH_6Ew1f6%8"              # signType(1) 对应的盐


def md5_lower(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def des3_encrypt(plain):
    data = plain.encode("utf-8")
    pad = 8 - len(data) % 8
    data = data + bytes([pad]) * pad
    cipher = DES3.new(DES_KEY, DES3.MODE_CBC, IV)
    return base64.b64encode(cipher.encrypt(data)).decode("ascii")


def build_params(username, password, imei, device_id):
    nano_time = random.randint(51 * 10 ** 11, 71 * 10 ** 11)  # 课件口径：5.1e12 ~ 7.1e12
    udid_plain = "%s|%d|%s" % (imei, nano_time, device_id)

    params = {
        "_appid": "atc.android",
        "appversion": "3.56.0",
        "channelid": "csy",
        "pwd": md5_lower(password),
        "signkey": "",
        "type": "",
        "udid": des3_encrypt(udid_plain),
        "username": username,
    }
    raw = SALT_V2 + "".join(k + params[k] for k in sorted(params)) + SALT_V2
    params["_sign"] = md5_lower(raw).upper()
    return params, udid_plain, raw


def main():
    params, udid_plain, raw = build_params(
        username="13800138000",
        password="123456",
        imei="f58f2d53-1309-36e1-a690-a34c8f49691c",
        device_id="381632",
    )

    print("udid 明文 :", udid_plain)
    print("udid 密文 :", params["udid"])
    print("签名原串  :", raw)
    print("_sign     :", params["_sign"])

    resp = requests.post(SERVER + LOGIN_PATH, data=params, timeout=10)
    body = resp.json()
    print("HTTP", resp.status_code, json.dumps(body, ensure_ascii=False))

    with open(RESULT_PATH, "w", encoding="utf-8") as fp:
        json.dump({"request": params, "udid_plain": udid_plain, "response": body},
                  fp, ensure_ascii=False, indent=2)

    ok = body.get("code") == 0
    print("结论:", "服务端校验通过" if ok else "服务端校验失败")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
