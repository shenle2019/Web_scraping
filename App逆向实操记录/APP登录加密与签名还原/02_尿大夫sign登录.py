# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""尿大夫 4.1.11 登录：MD5 截取拼接签名还原。

jadx 反编译 SafeUtils.getSign(long)：
    sign = md5("niaodaifu" + 秒时间戳)[12:30]
         + md5("android"   + 秒时间戳)[12:26]
请求体里 password 是明文，真正的门槛是 sign。

实测 hook：getSign(1792405472) = acf37901198f906cefab3e4001d0b92a
"""
import argparse
import random
import sys
import time

from common import md5, post

URL = "https://api.niaodaifu.cn/v4/site/loginnew"
CHANNEL = "android"


def get_sign(ts, channel=CHANNEL):
    first = md5("niaodaifu%d" % ts)[12:30]
    second = md5("%s%d" % (channel, ts))[12:26]
    return first + second


def main():
    parser = argparse.ArgumentParser(description="尿大夫登录复刻（仅限学习研究）")
    parser.add_argument("--phone", default="18953675221")
    parser.add_argument("--password", default="1234567")
    parser.add_argument("--ts", type=int, default=None, help="秒时间戳，默认取当前时间")
    parser.add_argument("--devisetoken", default=None, help="设备标识，默认随机 20 位 hex")
    parser.add_argument("--no-request", action="store_true", help="只本地复算，不发请求")
    args = parser.parse_args()

    ts = args.ts or int(time.time())
    devisetoken = args.devisetoken or "".join(random.choices("0123456789abcdef", k=20))
    sign = get_sign(ts)

    body = {
        "devisetoken": devisetoken,
        "password": args.password,
        "mobile": args.phone,
        "channel": CHANNEL,
        "sign": sign,
        "time": str(ts),
        "mechanism": "0",
        "platform": "1",
    }

    print("[1] 时间戳    = %s" % ts)
    print("[2] sign      = %s" % sign)
    print("[3] 请求体    = %s" % body)
    if args.no_request:
        return 0

    print("[4] POST %s" % URL)
    status, text = post(URL, form_body=body)
    print("[5] HTTP %s" % status)
    print("[6] 响应 = %s" % text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
