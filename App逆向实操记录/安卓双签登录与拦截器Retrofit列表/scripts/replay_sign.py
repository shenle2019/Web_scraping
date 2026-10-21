# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

用 Python 复刻 App 端的两级签名，和本地 Flask 靶场（day10 复刻工程）对话：
  1) 请求头：ctime + hsign = md5(ctime + SALT)        -> 服务端 before_request 校验
  2) 请求体：sign = md5(t1 + user + md5(pwd))          -> /login 校验
  3) /films：Authorization: Bearer <token>              -> token 来自 /login

脚本同时跑 6 个负向用例，验证服务端每一道校验都真的生效（不是摆设）。
请求为单线程、间隔 >= 1 秒，符合低频学习场景。

运行：
    python replay_sign.py                      # 默认 http://192.168.31.220:8080
    python replay_sign.py --base http://127.0.0.1:8080
"""
import argparse
import hashlib
import json
import sys
import time

import requests

SALT = "SJH_2026_APP"
DEFAULT_BASE = "http://192.168.31.220:8080"
GAP = 1.2          # 请求间隔，低频


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def signed_headers():
    ctime = str(int(time.time()))
    return {
        "ctime": ctime,
        "hsign": md5(ctime + SALT),
        "X-Client": "python-replay/1.0",
    }


def login(base, user="justin", raw_pwd="123456", override_sign=None, t1=None):
    t1 = t1 or str(int(time.time()))
    pwd = md5(raw_pwd)
    sign = override_sign if override_sign is not None else md5(t1 + user + pwd)
    data = {"user": user, "pwd": pwd, "sign": sign, "t1": t1}
    r = requests.post(base + "/login", data=data, headers=signed_headers(), timeout=8)
    return r, data


def show(tag, resp):
    try:
        body = resp.json()
    except ValueError:
        body = resp.text
    print("[%-22s] HTTP %s  %s" % (tag, resp.status_code, json.dumps(body, ensure_ascii=False)))
    return body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=DEFAULT_BASE)
    args = parser.parse_args()
    base = args.base.rstrip("/")
    ok = 0
    fail = 0

    print("=" * 78)
    print("靶场:", base)
    print("口径: body sign = md5(t1 + user + md5(pwd)); header hsign = md5(ctime + salt)")
    print("=" * 78)

    # ---------- 正向 1：登录 ----------
    resp, data = login(base)
    body = show("正向-登录", resp)
    if body.get("code") == 100:
        ok += 1
        token = body["token"]
        print("        t1=%s pwd=%s sign=%s" % (data["t1"], data["pwd"], data["sign"]))
        print("        token=%s..." % token[:12])
    else:
        print("!! 登录失败，后续用例终止")
        return 1
    time.sleep(GAP)

    # ---------- 正向 2：带 token 取列表 ----------
    headers = signed_headers()
    headers["Authorization"] = "Bearer " + token
    r = requests.get(base + "/films", headers=headers, timeout=8)
    body = show("正向-列表", r)
    if body.get("code") == 100 and len(body.get("data", [])) == 10:
        ok += 1
        print("        首条: %s / %s 封面 %s" % (
            body["data"][0]["title"], body["data"][0]["score"], body["data"][0]["cover"]))
    else:
        fail += 1
    time.sleep(GAP)

    # ---------- 负向 1：篡改 body sign ----------
    r, _ = login(base, override_sign="0" * 32)
    body = show("负向-篡改sign", r)
    ok += 1 if body.get("code") == 102 else 0
    fail += 1 if body.get("code") != 102 else 0
    time.sleep(GAP)

    # ---------- 负向 2：密码错误（sign 用错误密码重算，签名本身合法）----------
    r, _ = login(base, raw_pwd="654321")
    body = show("负向-密码错误", r)
    ok += 1 if body.get("code") == 101 else 0
    fail += 1 if body.get("code") != 101 else 0
    time.sleep(GAP)

    # ---------- 负向 3：缺少 ctime 头 ----------
    r = requests.post(base + "/login", data={"user": "justin"}, timeout=8)
    body = show("负向-无ctime头", r)
    ok += 1 if body.get("code") == 103 else 0
    fail += 1 if body.get("code") != 103 else 0
    time.sleep(GAP)

    # ---------- 负向 4：ctime 过期（拿 1 小时前的签名重放）----------
    old = str(int(time.time()) - 3600)
    r = requests.post(base + "/login", data={"user": "justin"},
                      headers={"ctime": old, "hsign": md5(old + SALT), "X-Client": "replay/1.0"},
                      timeout=8)
    body = show("负向-ctime过期", r)
    ok += 1 if body.get("code") == 103 else 0
    fail += 1 if body.get("code") != 103 else 0
    time.sleep(GAP)

    # ---------- 负向 5：hsign 算错 ----------
    h = signed_headers()
    h["hsign"] = "f" * 32
    r = requests.post(base + "/login", data={"user": "justin"}, headers=h, timeout=8)
    body = show("负向-hsign错误", r)
    ok += 1 if body.get("code") == 103 else 0
    fail += 1 if body.get("code") != 103 else 0
    time.sleep(GAP)

    # ---------- 负向 6：无 token / 伪造 token 取列表 ----------
    r = requests.get(base + "/films", headers=signed_headers(), timeout=8)
    show("负向-无token", r)
    ok += 1 if r.status_code == 401 else 0
    fail += 1 if r.status_code != 401 else 0
    time.sleep(GAP)

    h = signed_headers()
    h["Authorization"] = "Bearer deadbeefdeadbeefdeadbeefdeadbeef"
    r = requests.get(base + "/films", headers=h, timeout=8)
    show("负向-伪造token", r)
    ok += 1 if r.status_code == 401 else 0
    fail += 1 if r.status_code != 401 else 0

    print("-" * 78)
    print("通过 %d 项 / 失败 %d 项" % (ok, fail))
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
