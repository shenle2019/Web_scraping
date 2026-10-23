# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
# Python 端独立复刻 newSign，并与本地服务端联调：
#   1) 正确 newSign -> 拿 X-Auth-Token
#   2) 错误 newSign -> 456
#   3) 带 token 拉 feed -> 200
#   4) 不带 token 拉 feed -> 401
# 只访问本机 127.0.0.1:8000，不连接任何真实站点

import base64
import hashlib
import json
import random
import time

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

BASE = "http://127.0.0.1:8000"
KEY = b"d245a0ba8d678a61"


def new_sign(params):
    plain = "".join("%s%s" % (k, params[k]) for k in sorted(params) if k != "newSign")
    raw = AES.new(KEY, AES.MODE_ECB).encrypt(pad(plain.encode("utf-8"), 16))
    b64 = base64.b64encode(raw).decode()
    return hashlib.md5(b64.encode()).hexdigest(), plain, b64


def main():
    uid = "%016x" % random.getrandbits(64)
    ts = str(int(time.time() * 1000))
    body = {
        "loginToken": "",
        "platform": "android",
        "timestamp": ts,
        "uuid": uid,
        "v": "4.74.5",
    }
    sign, plain, b64 = new_sign(body)
    body["newSign"] = sign
    print("[1] StringToSign =", plain)
    print("[1] Base64(AES)  =", b64)
    print("[1] newSign      =", sign)

    headers = {
        "duuuid": uid,
        "duplatform": "android",
        "appId": "duapp",
        "duv": "4.74.5",
        "User-Agent": "duapp/4.74.5(android;11)",
    }
    resp = requests.post(BASE + "/api/v1/app/user_core/users/getVisitorUserId",
                         json=body, headers=headers, timeout=10)
    token = resp.headers.get("X-Auth-Token", "")
    print("[2] token HTTP =", resp.status_code, "body =", resp.text[:160])
    print("[2] X-Auth-Token =", token[:48] + "..." if token else "(空)")

    bad = dict(body)
    bad["newSign"] = "0" * 32
    bad_resp = requests.post(BASE + "/api/v1/app/user_core/users/getVisitorUserId",
                             json=bad, headers=headers, timeout=10)
    print("[3] 错误 newSign HTTP =", bad_resp.status_code, "body =", bad_resp.text[:120])

    ts2 = str(int(time.time() * 1000))
    params = {
        "lastId": "1",
        "limit": "20",
        "loginToken": "",
        "platform": "android",
        "timestamp": ts2,
        "uuid": uid,
        "v": "4.74.5",
    }
    sign2, plain2, _ = new_sign(params)
    params["newSign"] = sign2
    print("[4] feed StringToSign =", plain2)

    feed_resp = requests.get(BASE + "/sns-rec/v1/recommend/all/feed",
                             params=params,
                             headers={"X-Auth-Token": token, "User-Agent": "duapp/4.74.5(android;11)"},
                             timeout=10)
    print("[5] feed HTTP =", feed_resp.status_code, "body =", feed_resp.text[:240])

    no_token = requests.get(BASE + "/sns-rec/v1/recommend/all/feed",
                            params=params, timeout=10)
    print("[6] 无 token HTTP =", no_token.status_code, "body =", no_token.text[:120])

    result = {
        "uuid": uid,
        "newSign": sign,
        "token_http": resp.status_code,
        "token_prefix": token[:32],
        "bad_sign": {"http": bad_resp.status_code, "body": bad_resp.text},
        "feed_http": feed_resp.status_code,
        "feed_head": feed_resp.text[:300],
        "no_token": {"http": no_token.status_code, "body": no_token.text},
    }
    with open("repl_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("[7] 结果写入 repl_result.json（含 token 前缀，不入库）")


if __name__ == "__main__":
    main()
