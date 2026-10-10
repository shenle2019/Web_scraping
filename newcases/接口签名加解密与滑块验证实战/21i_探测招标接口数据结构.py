# -*- coding: utf-8 -*-
"""探测招标接口解密后的完整数据结构，找到数据列表字段"""
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

KEY = b"".join(w.to_bytes(4, "big") for w in [863652730, 2036741733, 1164342596, 1782662963])
IV = b"".join(w.to_bytes(4, "big") for w in [1719227713, 1314533489, 1397643880, 1749959510])


def aes_decrypt(b64_text):
    ct = base64.b64decode(b64_text.strip())
    pt = AES.new(KEY, AES.MODE_CBC, IV).decrypt(ct)
    return pt.rstrip(b"\x00").decode("utf-8")


cookies = {c["name"]: c["value"]
           for c in json.load(open("分析素材/bidcenter_cookies.json", encoding="utf-8"))}

form = {
    "from": "6137",
    "guid": str(uuid.uuid4()),
    "location": "6138",
    "token": "",
    "deftag": "1",
    "keywords": quote("服务"),
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
data = json.loads(aes_decrypt(r.text))

# 保存完整解密结果
with open("分析素材/bidcenter_api_decrypted.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("完整解密结果已保存: 分析素材/bidcenter_api_decrypted.json")

# 递归打印结构（键名 + 类型 + 长度/预览）
def walk(obj, prefix="", depth=0):
    if depth > 4:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list):
                print("%s%s: list[%d]" % (prefix, k, len(v)))
                if v and depth < 3:
                    walk(v[0], prefix + "  [0].", depth + 1)
            elif isinstance(v, dict):
                print("%s%s: dict{%s}" % (prefix, k, ",".join(list(v.keys())[:8])))
                walk(v, prefix + "  ", depth + 1)
            else:
                s = str(v).replace("\n", " ")[:80]
                print("%s%s = %s" % (prefix, k, s))


walk(data)

# 重点查看 other2（含分页/列表信息）
o2 = data.get("other2")
if isinstance(o2, str):
    try:
        o2 = json.loads(o2)
        print("\n=== other2 解析后结构 ===")
        walk(o2)
    except Exception as e:
        print("\nother2 不是 JSON:", e)
