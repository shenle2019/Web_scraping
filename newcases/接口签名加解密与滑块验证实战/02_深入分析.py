# -*- coding: utf-8 -*-
"""深入分析：企名片 JS 关键词定位 + 建设库页面结构 + 招标网 Cookie 重试"""
import os
import re

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
H = {"User-Agent": UA}
SAVE = "分析素材"

# ===== 1. 企名片：下载主 JS 并统计关键词 =====
print("### 企名片 entry.js 分析")
r = requests.get("https://www.qimingpian.com/_nuxt/entry.0efbab5b.js",
                 headers=H, timeout=30)
r.encoding = "utf-8"
print("HTTP", r.status_code, len(r.text), "字符")
with open(os.path.join(SAVE, "qmp_entry.js"), "w", encoding="utf-8") as f:
    f.write(r.text)
for kw in ("encrypt_data", "decrypt", "CryptoJS", "AES", "aes", "sign",
           "recommendInfo", "secret", "iv", "key"):
    print("  含 %r: %d 次" % (kw, r.text.count(kw)))

# ===== 2. 建设库：分析已保存页面的结构线索 =====
print()
print("### 建设库 p3 页面分析")
html = open(os.path.join(SAVE, "jsk_p3.html"), encoding="utf-8").read()
srcs = re.findall(r'<script[^>]*?src="([^"]+)"', html)
print("JS 资源 %d 个:" % len(srcs))
for s in srcs[:20]:
    print("   ", s[:130])
links = re.findall(r'<link[^>]*?href="([^"]+\.js[^"]*)"', html)
print("预加载 JS:", links[:10])
for kw in ("nuxt", "企业", "搜索", "data-server-rendered", "window."):
    print("  含 %r: %d 次" % (kw, html.count(kw)))

# ===== 3. 招标网：先访问首页拿 Cookie 再搜索 =====
print()
print("### 招标网 Cookie 重试")
s = requests.Session()
r0 = s.get("https://www.bidcenter.com.cn/", headers=H, timeout=20)
print("首页: HTTP %s, %d 字节, cookies=%s"
      % (r0.status_code, len(r0.content), dict(s.cookies)))
r1 = s.get("https://search.bidcenter.com.cn/search?"
           "keywords=%e6%9c%8d%e5%8a%a1%e5%99%a8", headers=H, timeout=20)
r1.encoding = "utf-8"
print("搜索: HTTP %s, %d 字节" % (r1.status_code, len(r1.text)))
print("  预览:", r1.text[:200].replace("\n", " "))
