# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

司小宝 driverLogin 加密链路复刻（本地 mock 版，不碰真站）。

复刻课件里的三件事：
  1) sign = quote_plus(base64(HMAC-SHA1(key, "POST\\n{ts}\\n/inside.php")))
     用课件 hook 出来的真值做自检：ts=1694450485059 -> 5VnGRNih2xWwXIF3QeuAYdD7j%2F4%3D
  2) mobile / password = hex_upper(base64(RSA/ECB/PKCS1Padding(明文)))
  3) 把两组密文塞进 form、sign 塞进 query，POST /inside.php

再跑四组用例：正常登录 / 密码错误 / 篡改签名 / 过期时间戳。

用法：python 01_sign_login.py [--base http://127.0.0.1:8018] [--out 结果日志]
"""
import argparse
import base64
import hashlib
import hmac
import io
import os
import sys
import time
from urllib.parse import quote_plus

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

SIGN_KEY = b"1KMrg0dfufc0wpnXEJacEQX1YEUYA0Ja"
REFERER = "d507c00281c733bd693e5049ea33ad7e"
COURSE_VECTOR = ("1694450485059", "5VnGRNih2xWwXIF3QeuAYdD7j%2F4%3D")


def sign(ts):
    msg = ("POST\n%s\n/inside.php" % ts).encode("utf-8")
    return quote_plus(base64.b64encode(hmac.new(SIGN_KEY, msg, hashlib.sha1).digest()).decode())


def hex_upper(text):
    """课件里的 c()：把字符串逐字节转成大写 hex。"""
    table = "0123456789ABCDEF"
    return "".join(table[(b & 0xF0) >> 4] + table[b & 0x0F] for b in text.encode("utf-8"))


def encrypt(text, pubkey):
    cipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
    b64 = base64.b64encode(cipher.encrypt(text.encode("utf-8"))).decode()
    return hex_upper(b64)


def build(ts, mobile, password, pubkey, sign_override=None):
    params = {
        "t": "json",
        "m": "mobileinfo",
        "f": "driverLogin",
        "g7timestamp": ts,
        "app": "1",
        "ua": "android",
        "appclientversion": "4.0.9",
        "referer": REFERER,
        "sign": sign_override if sign_override is not None else sign(ts),
    }
    form = {"mobile": encrypt(mobile, pubkey), "password": encrypt(password, pubkey),
            "equipment": "google"}
    return params, form


def post(base, params, form):
    res = requests.post(base + "/inside.php", params=params, data=form, timeout=5)
    return res.status_code, res.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8018")
    ap.add_argument("--mobile", default="18953675221")
    ap.add_argument("--password", default="lqz12345")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    logs = []

    def log(line):
        line = line if isinstance(line, str) else str(line)
        print(line)
        logs.append(line)

    log("== 1. 签名算法自检（对齐课件 hook 真值）==")
    ts0, expect = COURSE_VECTOR
    got = sign(ts0)
    log("ts=%s 期望=%s 计算=%s -> %s" % (ts0, expect, got, "一致" if got == expect else "不一致"))
    if got != expect:
        raise SystemExit("签名算法与课件不一致，终止")

    log("== 2. 取本地 mock 公钥并加密手机号/密码 ==")
    pubkey = requests.get(args.base + "/__mock/pubkey", timeout=5).json()["data"]["pubkey"]
    log("密钥位数=%d" % RSA.importKey(pubkey).size_in_bits())
    ts = str(int(time.time() * 1000))
    params, form = build(ts, args.mobile, args.password, pubkey)
    log("mobile 密文长度=%d（hex）  password 密文长度=%d" % (len(form["mobile"]), len(form["password"])))
    log("sign=%s" % params["sign"])

    log("== 3. 用例：正常登录 ==")
    code, body = post(args.base, params, form)
    log("HTTP %d %s" % (code, body))
    ok = body.get("code") == 0

    log("== 4. 用例：密码错误 ==")
    p2, f2 = build(str(int(time.time() * 1000)), args.mobile, "wrong-pass", pubkey)
    _, body2 = post(args.base, p2, f2)
    log(body2)
    ok = ok and body2.get("code") == 1001

    log("== 5. 用例：篡改签名 ==")
    p3, f3 = build(str(int(time.time() * 1000)), args.mobile, args.password, pubkey,
                   sign_override="AAAA" + params["sign"][4:])
    _, body3 = post(args.base, p3, f3)
    log(body3)
    ok = ok and body3.get("code") == 1002

    log("== 6. 用例：过期时间戳（10 分钟前）==")
    old_ts = str(int(time.time() * 1000) - 600 * 1000)
    p4, f4 = build(old_ts, args.mobile, args.password, pubkey)
    _, body4 = post(args.base, p4, f4)
    log(body4)
    ok = ok and body4.get("code") == 1003

    log("结论：%s" % ("PASS 四组用例全部符合预期" if ok else "FAIL 有用例不符合预期"))
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(logs) + "\n")
        print("已写入 %s" % os.path.abspath(args.out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
