# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""day05 三个案例的算法离线自检。

样本全部来自本机 Frida 实时 hook（见 capture/），这里只做本地复算，
不联网，用于证明 Python 实现与 APK 运行时输出逐字节一致。
"""
import sys

from common import aes_cbc_pkcs7_base64, md5
from importlib import import_module

aiqiu = import_module("01_爱安丘AES登录")
niaodaifu = import_module("02_尿大夫sign登录")
partner = import_module("03_合伙人XSign登录")

CASES = []


def add(name, got, expect):
    CASES.append((name, got, expect))


# 1. 爱安丘：hook 到 getMD5 输入与输出
add(
    "爱安丘 AES key (getMD5)",
    aiqiu.build_key("48dce77cf43eb6c3", "137"),
    "6d6656a37cdb7977c10f6d83cab168e9",
)
add(
    "爱安丘 AES 密码密文",
    aes_cbc_pkcs7_base64("lqz123456", "6d6656a37cdb7977c10f6d83cab168e9"),
    "0FwYho4FQoTYvYu2eioWDw==",
)

# 2. 尿大夫：hook 到 getSign(long)，两组不同时间戳
add(
    "尿大夫 sign (ts=1792405472)",
    niaodaifu.get_sign(1792405472),
    "acf37901198f906cefab3e4001d0b92a",
)
add(
    "尿大夫 sign (ts=1792408334)",
    niaodaifu.get_sign(1792408334),
    "2d61ee52da5d9bf900df35c761994f73",
)

# 3. 合伙人：hook 到 Md5.md5 与 RequestParamsWrapper.sign
add(
    "合伙人 密码 MD5",
    md5("123456"),
    "e10adc3949ba59abbe56e057f20f883e",
)
add(
    "合伙人 X-Sign (reqTime=1792406196986)",
    partner.build_x_sign(
        "",
        "1792406196986",
        "phone=18953675221&password=e10adc3949ba59abbe56e057f20f883e",
    ),
    "8c0dc9169e6f24e096e9531e5d070bb5",
)
add(
    "合伙人 X-Sign (reqTime=1792408299226)",
    partner.build_x_sign(
        "",
        "1792408299226",
        "phone=18953675221&password=e10adc3949ba59abbe56e057f20f883e",
    ),
    "e06815789f099bcfefbe2a68b942555b",
)


def main():
    print("=" * 76)
    print("day05 算法自检（样本来自 Frida 实时 hook，本地复算）")
    print("=" * 76)
    failed = 0
    for name, got, expect in CASES:
        ok = got == expect
        failed += 0 if ok else 1
        print("[%s] %s" % ("PASS" if ok else "FAIL", name))
        print("       复算 = %s" % got)
        print("       hook = %s" % expect)
    print("-" * 76)
    print("合计 %d 项，通过 %d 项，失败 %d 项" % (len(CASES), len(CASES) - failed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
