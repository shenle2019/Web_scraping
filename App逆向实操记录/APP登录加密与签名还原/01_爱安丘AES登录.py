# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""爱安丘 1.0.5 登录：AES/CBC/PKCS7 + Base64 还原。

算法来源（jadx 反编译 + Frida hook 双向确认）：
    EncryptUtil.aesPassword(pwd) =
        Base64(AES/CBC/PKCS7,
               key = md5(PRIVATE_KEY + getSecret() + orgid) 的 hex 字符串字节,
               iv  = "0000000000000000")
    PRIVATE_KEY = "c058579161250b37"
    getSecret() = <R.string.secret_key> + "APP" = "48dce77cf43eb6c3APP"
    orgid       = "137"

实测 hook：md5("c058579161250b3748dce77cf43eb6c3APP137")
           = 6d6656a37cdb7977c10f6d83cab168e9
"""
import argparse
import json
import sys

from common import aes_cbc_pkcs7_base64, generate_imei, md5, post

PRIVATE_KEY = "c058579161250b37"
SECRET_KEY = "48dce77cf43eb6c3"  # APK 资源 R.string.secret_key
ORG_ID = "137"
VERSION = "1.0.5"  # 固定用课件版本，不升级 APP
URL = "https://app-auth.iqilu.com/member/login?e=1"


def build_key(secret, orgid):
    """getMD5(PRIVATE_KEY + getSecret() + BaseApp.orgid)。"""
    return md5(PRIVATE_KEY + secret + "APP" + orgid)


def main():
    parser = argparse.ArgumentParser(description="爱安丘登录复刻（仅限学习研究）")
    parser.add_argument("--phone", default="18953675222")
    parser.add_argument("--password", default="lqz123456")
    parser.add_argument("--secret", default=SECRET_KEY)
    parser.add_argument("--orgid", default=ORG_ID)
    parser.add_argument("--no-request", action="store_true", help="只本地复算，不发请求")
    args = parser.parse_args()

    key = build_key(args.secret, args.orgid)
    cipher_pwd = aes_cbc_pkcs7_base64(args.password, key)
    headers = {
        "encrypt": "1",
        "version": VERSION,
        "orgid": args.orgid,
        "User-Agent": "null chuangqi.o.%s.com.iqilu.app137/%s" % (args.orgid, VERSION),
        "platform": "android",
        "imei": generate_imei(),
        "Content-Type": "application/json; charset=UTF-8",
    }
    body = {
        "codeKey": "",
        "password": cipher_pwd,
        "code": "",
        "phone": args.phone,
        "key": "",
    }

    print("[1] 运行时 AES key = %s" % key)
    print("[2] 密码密文       = %s" % cipher_pwd)
    print("[3] 请求体         = %s" % json.dumps(body, ensure_ascii=False))
    print("[4] imei           = %s" % headers["imei"])
    if args.no_request:
        return 0

    print("[5] POST %s" % URL)
    status, text = post(URL, json_body=body, headers=headers)
    print("[6] HTTP %s" % status)
    print("[7] 响应 = %s" % text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
