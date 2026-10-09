# -*- coding: utf-8 -*-
"""分析 bidcenter 搜索结果页 DOM 结构：定位结果列表重复容器与字段"""
import re
from collections import Counter

from lxml import etree

html = open("分析素材/bidcenter_result.html", encoding="utf-8").read()
print("HTML 长度:", len(html))

tree = etree.HTML(html)

# 1. 找重复的候选列表容器（同 class 出现 >=5 次的 li/dl/div）
cands = Counter()
for el in tree.iter():
    if el.tag in ("li", "dl", "div", "tr") and el.get("class"):
        cands[(el.tag, el.get("class"))] += 1
print("\n=== 重复容器 top15（li/dl/div/tr）===")
for (tag, cls), n in cands.most_common(15):
    print("  %-5s class=%-40s x%d" % (tag, cls[:40], n))

# 2. 找标题链接（a 中有 href 且文本较长）
print("\n=== 长文本链接样本 ===")
cnt = 0
for a in tree.iter("a"):
    txt = (a.text or "").strip()
    href = a.get("href") or ""
    if len(txt) > 12 and href and cnt < 15:
        print("  [%s] %s" % (txt[:40], href[:80]))
        cnt += 1

# 3. 定位可能的结果列表
print("\n=== 含'中标'或'招标'的 class 名 ===")
seen = set()
for el in tree.iter():
    c = el.get("class") or ""
    if ("list" in c.lower() or "result" in c.lower() or "item" in c.lower()) and c not in seen:
        seen.add(c)
        print("  ", el.tag, "|", c[:80])

# 4. 保存一个可能的列表项片段
print("\n=== 候选列表项 HTML 片段（class 含 list/item 的 ul 下第一个 li）===")
for ul in tree.iter("ul"):
    cls = ul.get("class") or ""
    if "list" in cls.lower():
        lis = ul.findall("li")
        if lis:
            frag = etree.tostring(lis[0], encoding="unicode")
            print("UL class:", cls, "| li 数:", len(lis))
            print(frag[:1500])
            print("-----")
            break
