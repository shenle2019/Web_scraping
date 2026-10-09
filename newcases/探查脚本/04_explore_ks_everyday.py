# -*- coding: utf-8 -*-
"""勘察【每日一练】列表页 /practice/listEveryday?sign=jz1 的结构"""
import os
import re
import sys
import time

import requests
from lxml import etree

# 脚本位于子目录：把上级目录（newcases）加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proxy_pool import get_proxies

BASE = "https://ks.wangxiao.cn"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    ),
    "Referer": "https://ks.wangxiao.cn/TestPaper/list?sign=jz1",
}


def fetch(url, retry=6, timeout=15):
    for i in range(retry):
        try:
            resp = requests.get(url, headers=HEADERS,
                                proxies=get_proxies(), timeout=timeout)
            print("[try %d] %s -> HTTP %s, %d bytes" % (
                i + 1, url, resp.status_code, len(resp.text)))
            if resp.status_code == 200 and len(resp.text) > 500:
                return resp
        except requests.RequestException as exc:
            print("[try %d] 异常: %s" % (i + 1, exc))
        time.sleep(1)
    return None


def main():
    url = BASE + "/practice/listEveryday?sign=jz1"
    resp = fetch(url)
    if resp is None:
        return
    html = resp.text
    with open("ks_everyday_jz1.html", "w", encoding="utf-8") as f:
        f.write(html)

    tree = etree.HTML(html)
    print("\n--- 页面中所有带 data_sign / data_subsign / data_top 属性的元素 ---")
    for el in tree.xpath("//*[@data_sign or @data_subsign or @data_top]"):
        tag = el.tag
        attrs = {k: v for k, v in el.attrib.items()
                 if k in ("data_sign", "data_subsign", "data_top", "data_sign2",
                          "class", "id")}
        text = "".join(el.xpath(".//text()")).strip()[:60]
        print("<%s> %s | %s" % (tag, attrs, text))
        print("-" * 50)

    print("\n--- 所有 a[href] 中包含 Everyday / practice 的链接 ---")
    seen = set()
    for a in tree.xpath("//a[@href]"):
        href = a.xpath("./@href")[0]
        if any(k in href for k in ("Everyday", "practice", "listQuestions")):
            text = "".join(a.xpath(".//text()")).strip()
            if (text, href) not in seen:
                seen.add((text, href))
                print("%-24s %s" % (text, href))

    print("\n--- JS 中的接口地址片段 ---")
    for m in re.finditer(r"url\s*[:=]\s*['\"]([^'\"]+)['\"]", html):
        u = m.group(1)
        if len(u) > 8:
            print(u)


if __name__ == "__main__":
    main()
