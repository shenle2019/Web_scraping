# -*- coding: utf-8 -*-
"""招标网数据接口直连测试：完全复刻前端 JS 的请求与解密逻辑
接口: POST https://interface.bidcenter.com.cn/search/GetSearchProHandler.ashx
解密: AES-CBC + ZeroPadding（key/iv 来自 searchv17.js variate 的 words 数组）
"""
import base64
import json
import time
import uuid
from urllib.parse import quote

import requests
from Crypto.Cipher import AES

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
API = "https://interface.bidcenter.com.cn/search/GetSearchProHandler.ashx"
REFERER = "https://search.bidcenter.com.cn/search?keywords=%E6%9C%8D%E5%8A%A1"


def words_to_bytes(words):
    """CryptoJS WordArray.words -> bytes（32bit 大端）"""
    return b"".join(w.to_bytes(4, "big") for w in words)


# 来自 searchv17.js 第 107-119 行 variate 定义
KEY = words_to_bytes([863652730, 2036741733, 1164342596, 1782662963])
IV = words_to_bytes([1719227713, 1314533489, 1397643880, 1749959510])
print("KEY hex:", KEY.hex())
print("IV  hex:", IV.hex())


def aes_decrypt(b64_text):
    """AES-CBC ZeroPadding 解密（复刻 searchv17.js AESDecrypt）"""
    ct = base64.b64decode(b64_text.strip())
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    pt = cipher.decrypt(ct)
    pt = pt.rstrip(b"\x00")          # ZeroPadding: 去掉尾部 0x00
    return pt.decode("utf-8")


cookies = {c["name"]: c["value"]
           for c in json.load(open("分析素材/bidcenter_cookies.json", encoding="utf-8"))}

print("\n=== 第 1 页（不加 page 参数）===")
form = {
    "from": "6137",
    "guid": str(uuid.uuid4()),
    "location": "6138",
    "token": "",
    "deftag": "1",
    "keywords": quote("服务"),       # 字面 "%e6%9c%8d%e5%8a%a1"，requests 会再编码 %25
    "mod": "0",
    "vtime": str(int(time.time() * 1000)),
}
headers = {
    "user-agent": UA,
    "referer": REFERER,
    "origin": "https://search.bidcenter.com.cn",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}
r = requests.post(API, data=form, headers=headers, cookies=cookies, timeout=20)
print("状态码:", r.status_code, "| 长度:", len(r.text))
print("响应前 100 字符:", r.text[:100])

try:
    plain = aes_decrypt(r.text)
    print("\n解密成功! 明文长度:", len(plain))
    data = json.loads(plain)
    print("JSON 顶层键:", list(data.keys()) if isinstance(data, dict) else type(data))
    if isinstance(data, dict):
        for k, v in data.items():
            vs = json.dumps(v, ensure_ascii=False)
            print("  %-20s = %s" % (k, vs[:150]))
except Exception as e:
    print("\n解密失败:", type(e).__name__, e)
    print("前 200 字符:", r.text[:200])

print("\n=== 第 2 页（page=2）===")
form["page"] = "2"
form["guid"] = str(uuid.uuid4())
form["vtime"] = str(int(time.time() * 1000))
r2 = requests.post(API, data=form, headers=headers, cookies=cookies, timeout=20)
try:
    plain2 = aes_decrypt(r2.text)
    data2 = json.loads(plain2)
    print("第 2 页解密成功, 顶层键:", list(data2.keys()) if isinstance(data2, dict) else "?")
    # 尝试找列表
    for k, v in data2.items():
        if isinstance(v, list):
            print("  列表字段 %s: %d 项" % (k, len(v)))
            if v:
                print("  第一项键:", list(v[0].keys())[:24])
except Exception as e:
    print("第 2 页解密失败:", type(e).__name__, e)
