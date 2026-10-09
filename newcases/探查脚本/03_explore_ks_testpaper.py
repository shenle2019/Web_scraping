# -*- coding: utf-8 -*-
"""勘察二级标题页面（TestPaper/list?sign=jz1），找【每日一练】入口与其栏目结构"""
import os
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
    "Referer": "https://ks.wangxiao.cn/",
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
    url = BASE + "/TestPaper/list?sign=jz1"
    resp = fetch(url)
    if resp is None:
        return
    html = resp.text
    with open("ks_testpaper_jz1.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\n--- 含'每日一练'的行片段 ---")
    for m in __import__("re").finditer("每日一练", html):
        s = max(0, m.start() - 200)
        print(repr(html[s:m.end() + 200]))
        print("-" * 60)
        break

    print("\n--- 所有指向 practice / daily / exampoint 的 href ---")
    tree = etree.HTML(html)
    seen = set()
    for a in tree.xpath("//a[@href]"):
        href = a.xpath("./@href")[0]
        if any(k in href for k in ("practice", "daily", "exampoint", "listQuestions")):
            text = "".join(a.xpath(".//text()")).strip()
            key = (text, href)
            if key not in seen:
                seen.add(key)
                print("%-20s %s" % (text, href))


if __name__ == "__main__":
    main()
