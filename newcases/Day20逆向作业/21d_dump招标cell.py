# -*- coding: utf-8 -*-
"""dump 招标结果第一条 ssjg-list_cell 完整 HTML，确定字段选择器"""
from lxml import etree

html = open("分析素材/bidcenter_result.html", encoding="utf-8").read()
tree = etree.HTML(html)

# 结果计数
cnt = tree.xpath('//span[contains(@class,"result_count")]/text()')
print("结果计数:", cnt[:3])

cells = tree.xpath('//div[contains(@class,"ssjg-list_cell")]')
print("cell 数量:", len(cells))
print("\n===== 第一条 cell 完整 HTML =====")
print(etree.tostring(cells[0], encoding="unicode", pretty_print=True)[:4000])

print("\n===== 第二条 cell 完整 HTML =====")
print(etree.tostring(cells[1], encoding="unicode", pretty_print=True)[:3000])
