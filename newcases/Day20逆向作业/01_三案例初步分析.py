# -*- coding: utf-8 -*-
"""三案例初步分析：抓取页面/JS 资源，定位加密线索"""
import os
import re

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
H = {"User-Agent": UA}
os.makedirs("分析素材", exist_ok=True)


def save(name, text):
    path = os.path.join("分析素材", name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("  已保存:", path, "(%d 字符)" % len(text))


# ===== 案例3 企名片 =====
print("### 案例3 企名片 - 首页")
r = requests.get("https://www.qimingpian.com/", headers=H, timeout=20)
r.encoding = "utf-8"
save("qmp_index.html", r.text)
print("HTTP", r.status_code, len(r.text))
srcs = re.findall(r'<script[^>]*?src="([^"]+)"', r.text)
print("JS 资源 %d 个:" % len(srcs))
for s in srcs:
    print("   ", s)

# ===== 案例1 建设库 =====
print()
print("### 案例1 建设库 - 搜索页 p3")
r = requests.get("https://www.jiansheku.com/search/enterprise/p3/",
                 headers=H, timeout=20)
r.encoding = "utf-8"
save("jsk_p3.html", r.text)
print("HTTP", r.status_code, len(r.text))
for kw in ("__NUXT__", "有限公司", "/api/", "encrypt", "sign"):
    print("  包含 %r: %d 次" % (kw, r.text.count(kw)))

# ===== 案例2 招标网 =====
print()
print("### 案例2 招标网 - 搜索页")
r = requests.get(
    "https://search.bidcenter.com.cn/search?keywords=%e6%9c%8d%e5%8a%a1%e5%99%a8",
    headers=H, timeout=20)
r.encoding = "utf-8"
save("bidcenter_search.html", r.text)
print("HTTP", r.status_code, len(r.text))
print("完整内容预览:")
print(r.text[:1500])
