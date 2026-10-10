# -*- coding: utf-8 -*-
"""案例1 建设库：dump 一个完整的企业卡片 HTML"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from lxml import etree

doc = etree.HTML(open("分析素材/jsk_p3_data.html", encoding="utf-8").read())
cards = doc.xpath('//div[contains(@class,"info-list-right")]')
print("卡片数:", len(cards))
c = cards[0]
p = c.getparent()
print("--- 父容器:", p.tag, p.get("class"), "| 祖父:", p.getparent().tag, p.getparent().get("class"))
html = etree.tostring(p, encoding="unicode")
print(html[:2600])
print("\n\n=== 第二张卡片（检查字段差异）===")
if len(cards) > 1:
    print(etree.tostring(cards[1].getparent(), encoding="unicode")[:1800])
