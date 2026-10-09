# -*- coding: utf-8 -*-
"""案例3 企名片：拉取 vipapi recommendInfo 真实响应，保存样本供解密验证"""
import json

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
H = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Origin": "https://www.qimingpian.com",
    "Referer": "https://www.qimingpian.com/",
}

URL = "https://vipapi.qimingpian.cn/HomePage/recommendInfo"

print("=== 1. GET 无参 ===")
try:
    r = requests.get(URL, headers=H, timeout=20)
    print("HTTP", r.status_code, "|", r.text[:300])
    data = r.json()
except Exception as e:
    print("失败:", type(e).__name__, e)
    data = None
    r = None

if (not data or "encrypt" not in r.text) and True:
    print("\n=== 2. POST form 重试 ===")
    try:
        r2 = requests.post(URL, headers=H, data={"page": "1", "num": "10"}, timeout=20)
        print("HTTP", r2.status_code, "|", r2.text[:300])
        if "encrypt" in r2.text:
            r = r2
            data = r2.json()
    except Exception as e:
        print("失败:", type(e).__name__, e)

# 递归找加密字段
def find_enc(obj, path=""):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and ("encrypt" in k.lower() or (len(v) > 100 and "encrypt" in obj)):
                found.append((path + "/" + k, v))
            found += find_enc(v, path + "/" + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):
            found += find_enc(v, "%s[%d]" % (path, i))
    return found

if data:
    enc_fields = find_enc(data)
    print("\n加密字段:", [(p, len(v)) for p, v in enc_fields])
    with open("分析素材/vipapi_sample.json", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("样本已保存 分析素材/vipapi_sample.json (%d 字节)" % len(r.text))
    with open("分析素材/vipapi_encrypt_field.txt", "w", encoding="utf-8") as f:
        if enc_fields:
            f.write(enc_fields[0][1])
            print("加密串已单独保存 分析素材/vipapi_encrypt_field.txt")
else:
    print("未拿到有效样本")
