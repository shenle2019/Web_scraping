# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""day05 反编译案例复刻 - 公共工具函数。

包含 MD5、IMEI 生成、AES/CBC/PKCS7 + Base64、带重试的低频 HTTP POST。
"""
import base64
import hashlib
import random
import time

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

requests.packages.urllib3.disable_warnings()


def md5(text):
    """32 位小写 hex MD5，等价于 Java 的 Md5.md5()。"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def generate_imei():
    """按课件 Luhn 规则生成 15 位 IMEI。

    课件后面还给了 15 位随机 hex 的简化版；服务端只把它当设备标识，
    两种都能用，这里保留可校验的 Luhn 版本。
    """
    tac = "".join(random.choices("0123456789", k=6))
    fac = "".join(random.choices("0123456789", k=2))
    snr = "".join(random.choices("0123456789", k=6))
    base = tac + fac + snr
    digits = [int(d) for d in base]
    check = sum(digits[::-2] + [sum(divmod(d * 2, 10)) for d in digits[-2::-2]]) % 10
    return base + str((10 - check) % 10)


def aes_cbc_pkcs7_base64(plain, key):
    """AES/CBC/PKCS7Padding + Base64。

    注意：Java 端是 md5(...).getBytes()，即把 32 位 hex 字符串本身当密钥，
    实际是 AES-256；不是把 hex 解码成 16 字节。IV 为 16 个字符 '0'。
    """
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, b"0000000000000000")
    return base64.b64encode(cipher.encrypt(pad(plain.encode("utf-8"), AES.block_size))).decode()


def now_ms():
    return str(int(time.time() * 1000))


def post(url, json_body=None, form_body=None, headers=None, timeout=15):
    """低频 POST，返回 (status_code, text)；失败间隔 3 秒重试，最多 3 次。"""
    last_exc = None
    for attempt in range(1, 4):
        try:
            resp = requests.post(
                url,
                json=json_body,
                data=form_body,
                headers=headers,
                timeout=timeout,
                verify=False,
            )
            return resp.status_code, resp.text
        except requests.RequestException as exc:
            last_exc = exc
            print("[网络异常] 第 %d 次失败：%s" % (attempt, exc))
            time.sleep(3)
    raise RuntimeError("请求失败：%s" % last_exc)
