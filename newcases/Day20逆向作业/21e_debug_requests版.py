# -*- coding: utf-8 -*-
"""debug: requests 版搜索页 HTML 里到底有没有结果数据？"""
import json
from urllib.parse import quote

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
cookies = {c["name"]: c["value"]
           for c in json.load(open("分析素材/bidcenter_cookies.json", encoding="utf-8"))}
print("cookies:", list(cookies.keys()))

url = "https://search.bidcenter.com.cn/search?keywords=%s" % quote("服务")

for name, hdr in [
    ("基础UA", {"user-agent": UA}),
    ("完整浏览器头", {
        "user-agent": UA,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "zh-CN,zh;q=0.9",
        "referer": "https://www.bidcenter.com.cn/",
        "upgrade-insecure-requests": "1",
    }),
]:
    r = requests.get(url, headers=hdr, cookies=cookies, timeout=20)
    t = r.text
    print("\n=== [%s] 状态=%d 长度=%d ===" % (name, r.status_code, len(t)))
    for kw in ("ssjg-list_cell", "result_count", "人机验证", "news-", "ssjg-title",
               "window.__", "INITIAL", "dataList", "搜索结果"):
        print("  %-18s x%d" % (kw, t.count(kw)))
    open("分析素材/bidcenter_req_%s.html" % ("base" if name == "基础UA" else "full"),
         "w", encoding="utf-8").write(t)
    # 打印含 news- 的片段（如有）
    idx = t.find('news-')
    if idx > 0:
        print("  news- 片段:", t[max(0, idx - 120):idx + 120].replace("\n", " ")[:240])
