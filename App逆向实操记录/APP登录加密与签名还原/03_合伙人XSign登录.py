# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""合伙人 1.4 登录：密码 MD5 + X-Sign 还原。

jadx 反编译：
    LoginPresenter.submitLogin -> setPwd(Md5.md5(明文密码))
    RequestParamsWrapper.sign(body) =
        md5(token + reqTime + noncestr[2:] + body).toLowerCase()
    body 是 FormBody 按字段顺序拼出的 "phone=...&password=..."
    X-Noncestr 固定 "123456"，X-Token 未登录时为空串。

实测 hook：
    md5("123456") = e10adc3949ba59abbe56e057f20f883e
    X-Req-Time=1792406196986 时
    X-Sign = 8c0dc9169e6f24e096e9531e5d070bb5
"""
import argparse
import sys

from common import md5, now_ms, post

URL = "https://chinayltx.com/app/api/v1/partnerLogin/login"
NONCESTR = "123456"


def build_x_sign(token, req_time, body_string, noncestr=NONCESTR):
    """token + 毫秒时间戳 + noncestr[2:] + 原始 body（顺序必须一致）。"""
    return md5("%s%s%s%s" % (token, req_time, noncestr[2:], body_string))


def main():
    parser = argparse.ArgumentParser(description="合伙人登录复刻（仅限学习研究）")
    parser.add_argument("--phone", default="18953675221")
    parser.add_argument("--password", default="123456")
    parser.add_argument("--req-time", default=None, help="毫秒时间戳，默认取当前时间")
    parser.add_argument("--token", default="", help="登录接口为空；其他接口需带真实 token")
    parser.add_argument("--no-request", action="store_true", help="只本地复算，不发请求")
    args = parser.parse_args()

    req_time = args.req_time or now_ms()
    md5_pwd = md5(args.password)
    body_string = "phone=%s&password=%s" % (args.phone, md5_pwd)
    x_sign = build_x_sign(args.token, req_time, body_string)

    headers = {
        "X-App": "native",
        "X-Noncestr": NONCESTR,
        "X-OS": "partnerApp_android",
        "X-Req-Time": req_time,
        "X-Sign": x_sign,
        "X-Token": args.token,
        "X-UserID": "",
        "User-Agent": "okhttp/3.10.0",
    }
    body = {"phone": args.phone, "password": md5_pwd}

    print("[1] 密码 MD5  = %s" % md5_pwd)
    print("[2] 签名原文  = %s" % ("%s%s%s%s" % (args.token, req_time, NONCESTR[2:], body_string)))
    print("[3] X-Sign    = %s" % x_sign)
    print("[4] 请求头    = %s" % headers)
    if args.no_request:
        return 0

    print("[5] POST %s" % URL)
    status, text = post(URL, form_body=body, headers=headers)
    print("[6] HTTP %s" % status)
    print("[7] 响应 = %s" % text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
