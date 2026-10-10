# -*- coding: utf-8 -*-
"""案例3 企名片：下载全部 JS 到本地并搜索加解密关键词"""
import os
import re

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
H = {"User-Agent": UA}
SAVE = "分析素材/qmp_js"
os.makedirs(SAVE, exist_ok=True)

urls = []
for fn in ("分析素材/qmp_js_urls.txt", "分析素材/qmp_js_urls2.txt"):
    if os.path.exists(fn):
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if line and line not in urls:
                urls.append(line)

print("待下载 JS:", len(urls))
KEYWORDS = ["encrypt_data", "encryptdata", "decrypt", "encrypt", "CryptoJS",
            "AES", "aes", "CBC", "Pkcs7", "secret", "recommendInfo"]

hit_files = {}
for u in urls:
    name = u.split("?")[0].split("/")[-1] or "index.js"
    # 防重名
    prefix = ""
    if "chat.qmpoa.com" in u:
        prefix = "qmpoa_"
    elif "qimingpian.com" in u:
        prefix = "qmp_"
    path = os.path.join(SAVE, prefix + name)
    if not os.path.exists(path):
        try:
            r = requests.get(u, headers=H, timeout=30)
            text = r.text
            with open(path, "w", encoding="utf-8", errors="replace") as f:
                f.write(text)
        except Exception as e:
            print("  下载失败:", u[:90], type(e).__name__)
            continue
    else:
        text = open(path, encoding="utf-8", errors="replace").read()

    hits = {kw: text.count(kw) for kw in KEYWORDS if kw in text}
    if hits:
        hit_files[prefix + name] = hits
        print("%-46s %s" % (prefix + name, hits))

print("\n=== 命中文件汇总: %d ===" % len(hit_files))

# 对每个命中文件输出关键词上下文
print("\n=== 关键词上下文 ===")
for fn, hits in hit_files.items():
    text = open(os.path.join(SAVE, fn), encoding="utf-8", errors="replace").read()
    for kw in ("encrypt_data", "decrypt"):
        if kw in hits:
            print("\n----- %s 关键词 %r -----" % (fn, kw))
            for m in list(re.finditer(re.escape(kw), text))[:3]:
                s = max(0, m.start() - 150)
                print("  ...", text[s:m.end() + 250].replace("\n", " ")[:420], "...")
