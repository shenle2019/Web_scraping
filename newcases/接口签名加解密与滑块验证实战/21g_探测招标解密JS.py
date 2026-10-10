# -*- coding: utf-8 -*-
"""快速探测招标网前端 JS 解密逻辑：提取 script src，下载并在其中搜索解密线索"""
import os
import re
from urllib.parse import urljoin

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
html = open("分析素材/bidcenter_result.html", encoding="utf-8").read()

srcs = re.findall(r'<script[^>]+src="([^"]+)"', html)
print("script 数量:", len(srcs))
for s in srcs:
    print("  ", s)

# 关键 JS（search 相关优先）
os.makedirs("分析素材/bc_js", exist_ok=True)
targets = [s for s in srcs if ("search" in s.lower() or "common" in s.lower()
                               or "base" in s.lower() or "main" in s.lower())]
if not targets:
    targets = srcs[:12]

PAT = re.compile(r"(GetSearchProHandler|decrypt|decode|CryptoJS|AES|des|base64|"
                 r"unescape|escape|eval\()", re.I)

for s in targets:
    url = urljoin("https://search.bidcenter.com.cn/", s)
    name = re.sub(r'[^\w.\-]', "_", url.split("/")[-1].split("?")[0]) or "x.js"
    path = os.path.join("分析素材/bc_js", name)
    try:
        r = requests.get(url, headers={"user-agent": UA,
                                       "referer": "https://search.bidcenter.com.cn/"},
                         timeout=20)
        open(path, "w", encoding="utf-8", errors="replace").write(r.text)
        hits = {}
        for m in PAT.finditer(r.text):
            k = m.group(1).lower()
            hits[k] = hits.get(k, 0) + 1
        if hits:
            print("\n[命中] %s (%d 字符): %s" % (name, len(r.text), hits))
            # 打印含 decrypt/decode 的上下文
            for kw in ("decrypt", "decode(", "GetSearchProHandler"):
                for m in list(re.finditer(kw, r.text))[:2]:
                    st = max(0, m.start() - 150)
                    print("   ...%s..." % r.text[st:m.start() + 250].replace("\n", " ")[:360])
    except Exception as e:
        print("[失败]", url[:100], type(e).__name__, e)
