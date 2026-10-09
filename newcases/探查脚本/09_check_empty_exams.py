# -*- coding: utf-8 -*-
"""抽查：验证几个「暂无每日一练」的考试页面是否确实没有题目列表"""
import os
import sys

import requests
from lxml import etree

# 脚本位于子目录：把上级目录（newcases）加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proxy_pool import get_proxies

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    ),
}

for sign in ("sifa", "ncre3", "bec", "wxy", "yxkc", "jz1"):
    url = "https://ks.wangxiao.cn/practice/listEveryday?sign=%s" % sign
    try:
        r = requests.get(url, headers=HEADERS, proxies=get_proxies(), timeout=20)
    except requests.RequestException as exc:
        print(sign, "请求异常:", exc)
        continue
    t = etree.HTML(r.text)
    items = t.xpath('//ul[@class="test-item"]')
    subj = t.xpath('//div[contains(@class,"filter-item")]'
                   '/a[contains(@class,"filter-name")]')
    tip = t.xpath('//div[contains(@class,"test-panel")]//text()')
    tip_text = [s.strip() for s in tip if s.strip() and len(s.strip()) > 4][:2]
    print("%-6s HTTP %s | 日期行:%d | 科目数:%d | 面板文字:%s"
          % (sign, r.status_code, len(items), len(subj), tip_text))
