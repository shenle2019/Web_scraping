# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""金树林公开课案例链路复现：取码 -> 注册 -> 登录拿 JWT -> 带 Mobile-Token 搜索商品。

课件原始脚本（6-发送短信 / 7-注册 / 8-登录 / 9-搜索商品）是四段手工操作，
这里整合为一条可参数化的链路：
  * --base-url 默认指向课件真实域名；站点已下线时天然失败（脚本会如实打印）
  * --base-url http://127.0.0.1:18080 指向本地 Mock 服务，验证链路逻辑

低频学习用途：请求之间间隔 >= 1 秒，仅单线程。
"""
import argparse
import base64
import json
import time

import requests
import urllib3

urllib3.disable_warnings()

UA = ("Mozilla/5.0 (Linux; Android 11; Pixel 2 XL Build/RP1A.201005.004.A1; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 "
      "Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/28.0)")
INTERVAL = 1.0


def mask(text, keep=24):
    """凭证类字段不完整落日志。"""
    return text if len(text) <= keep else text[:keep] + "..."


def decode_jwt(token):
    """不校验签名，仅解出 payload 观察 aud/exp/iat/userId/username。"""
    body = token.split(".")[1]
    body += "=" * (-len(body) % 4)
    return json.loads(base64.urlsafe_b64decode(body))


def post_json(session, url, payload, headers=None):
    return session.post(url, json=payload, headers=headers or {}, timeout=15, verify=False)


def main():
    ap = argparse.ArgumentParser(description="金树林案例链路复现（学习用途）")
    ap.add_argument("--base-url", default="https://miappshop.jshulin.com",
                    help="接口根地址；本地验证填 http://127.0.0.1:18080")
    ap.add_argument("--phone", default="13800000000", help="测试手机号（占位号码）")
    ap.add_argument("--password", default="Test123456")
    ap.add_argument("--code", default=None, help="短信验证码；不填则尝试从取码响应读取")
    ap.add_argument("--keyword", default="红酒")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    session = requests.Session()
    session.headers.update({"user-agent": UA})

    print("==> 目标接口: %s" % base)

    # 步骤 1：取注册验证码（serviceType=5 为注册用码；6 为登录用码，见课件）
    print("\n[1/4] GET /memberLogin/phoneCode (serviceType=5)")
    try:
        res = session.get(base + "/memberLogin/phoneCode",
                          params={"phone": args.phone, "serviceType": 5},
                          timeout=15, verify=False)
        print("HTTP", res.status_code, "|", res.text[:300])
    except Exception as exc:
        print("[链路中断] 取码接口不可达: %s" % exc)
        print("提示：真实站点已下线时属于预期失败；可改用 --base-url http://127.0.0.1:18080 验证链路。")
        return 1

    code = args.code
    if not code:
        try:
            code = res.json()["data"]["phoneCode"]
        except Exception:
            print("[链路中断] 无法从响应中取得验证码，请人工查看短信后用 --code 传入。")
            return 1
    time.sleep(INTERVAL)

    # 步骤 2：注册
    print("\n[2/4] POST /memberLogin/memberRegister")
    res = post_json(session, base + "/memberLogin/memberRegister",
                    {"phone": args.phone, "fid": "", "password": args.password, "phoneCode": code})
    print("HTTP", res.status_code, "|", res.text[:300])
    try:
        if res.json().get("code") != 10000:
            print("[链路中断] 注册未成功，后续登录可能失败。")
    except Exception:
        pass
    time.sleep(INTERVAL)

    # 步骤 3：登录，拿 JWT
    print("\n[3/4] POST /memberLogin/login")
    res = post_json(session, base + "/memberLogin/login",
                    {"password": args.password, "username": args.phone})
    print("HTTP", res.status_code, "|", mask(res.text, 200))
    try:
        data = res.json()["data"]
        token = data["token"]
    except Exception as exc:
        print("[链路中断] 登录响应中没有 token: %s" % exc)
        return 1
    print("token:", mask(token))
    print("JWT payload:", json.dumps(decode_jwt(token), ensure_ascii=False))
    time.sleep(INTERVAL)

    # 步骤 4：带 Mobile-Token 搜索商品
    print("\n[4/4] POST /pro/searchByPage (Header: Mobile-Token)")
    res = post_json(session, base + "/pro/searchByPage",
                    {"cityNo": "", "keyword": args.keyword, "limit": 10,
                     "orderByContent": "", "page": 1, "enabled": 1},
                    headers={"Mobile-Token": token})
    print("HTTP", res.status_code, "|", mask(res.text, 400))
    try:
        result = res.json()
        if result.get("code") == 10000:
            items = result["data"]["list"]
            print("\n搜索结果: total=%s" % result["data"]["total"])
            for item in items[:3]:
                print("  - %s  ¥%s" % (item["name"], item["price"]))
    except Exception:
        pass
    print("\n[完成] 链路结束。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
