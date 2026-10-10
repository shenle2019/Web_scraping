# -*- coding: utf-8 -*-
"""案例1 建设库：离线分析已保存的 p3 页面结构（企业列表位置 / 总数 / 分页规律）"""
import re

html = open("分析素材/jsk_p3.html", encoding="utf-8").read()
print("页面长度:", len(html))

print("\n--- 1. 分页/总数线索 ---")
for pat in [r"共\s*<[^>]*>[\d,]+", r"共[\d,]+条", r"total[^,}\n]{0,40}", r"/search/enterprise/p\d+/"]:
    hits = re.findall(pat, html, re.I)
    print(repr(pat), "->", len(hits), hits[:5])

print("\n--- 2. 企业名出现次数 ---")
print("有限公司:", html.count("有限公司"))

print("\n--- 3. 企业列表所在容器（截取 有限公司 附近片段）---")
idx = html.find("有限公司")
if idx > 0:
    seg = html[max(0, idx - 800): idx + 200]
    print(seg[-1000:])

print("\n--- 4. 检查页面关键提示（登录/验证）---")
for kw in ["登录", "注册", "验证", "安全", "滑动", "captcha", "中转"]:
    c = html.count(kw)
    if c:
        print(kw, c)

print("\n--- 5. <a> 标签中企业详情链接样例 ---")
links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{2,40})</a>', html)
com = [(h, t) for h, t in links if "有限公司" in t]
print("企业链接数:", len(com))
for h, t in com[:8]:
    print("  ", t.strip()[:30], "->", h)

print("\n--- 6. 结构分块（top-level div id/class）---")
for m in re.finditer(r'<(?:div|section|ul)[^>]+(?:id|class)="([^"]{3,60})"', html):
    pass
# 找企业列表容器：包含多个企业链接的父级
m2 = re.search(r'<[^>]+class="([^"]*(?:list|result|company|enterprise)[^"]*)"', html, re.I)
print("疑似列表类名:", re.findall(r'class="([^"]*(?:list|result|company|enterprise)[^"]*)"', html, re.I)[:10])
