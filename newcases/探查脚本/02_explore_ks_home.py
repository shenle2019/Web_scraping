# -*- coding: utf-8 -*-
"""ks.wangxiao.cn 结构勘察脚本（走巨量IP代理）

目的：
  1. 抓首页 HTML 并保存到 ks_home.html
  2. 统计关键结构关键词出现次数
  3. 提取一级标题（分类）/ 二级标题（考试）/ sign 参数样本
  4. 探测【每日一练】板块对应的 URL 规律
"""
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch(url, retry=6, timeout=15):
    """带重试的抓取，每次重试换一个代理"""
    for i in range(retry):
        try:
            proxies = get_proxies()
            resp = requests.get(url, headers=HEADERS, proxies=proxies, timeout=timeout)
            print("[try %d] %s -> HTTP %s, %d bytes" % (
                i + 1, url, resp.status_code, len(resp.text)))
            if resp.status_code == 200 and len(resp.text) > 500:
                return resp
        except requests.RequestException as exc:
            print("[try %d] 异常: %s" % (i + 1, exc))
        time.sleep(1)
    return None


def main():
    print("=" * 70)
    print("步骤 1：抓取首页")
    print("=" * 70)
    resp = fetch(BASE + "/")
    if resp is None:
        print("首页多次重试均失败，退出")
        return
    html = resp.text
    with open("ks_home.html", "w", encoding="utf-8") as f:
        f.write(html)

    print()
    print("=" * 70)
    print("步骤 2：关键词统计")
    print("=" * 70)
    for kw in ["first-title", "second-title", "third-title", "TestPaper",
               "exampoint", "daily", "每日一练", "listQuestions", "sign=",
               "chapter-item", "section-item"]:
        print("%-14s : %d 次" % (kw, html.count(kw)))

    print()
    print("=" * 70)
    print("步骤 3：解析一级/二级标题")
    print("=" * 70)
    tree = etree.HTML(html)
    first_uls = tree.xpath('//ul[contains(@class,"first-title")]')
    print("含 first-title 的 ul 数量：%d" % len(first_uls))
    for ul in first_uls:
        lis = ul.xpath('./li')
        for li in lis:
            cat = li.xpath('string(./p//text())').strip()
            links = li.xpath('.//a')
            items = []
            for a in links:
                name = "".join(a.xpath('.//text()')).strip()
                href = a.xpath('./@href')
                items.append((name, href[0] if href else ""))
            if items:
                print("\n【一级标题】%s （%d 个二级标题）" % (cat, len(items)))
                for name, href in items[:6]:
                    print("    %-16s %s" % (name, href))
                if len(items) > 6:
                    print("    ... 其余 %d 个省略" % (len(items) - 6))

    print()
    print("=" * 70)
    print("步骤 4：探测【每日一练】URL")
    print("=" * 70)
    probe_urls = [
        BASE + "/daily/list?sign=jz1",
        BASE + "/practice/list?sign=jz1",
        BASE + "/TestPaper/list?sign=jz1",
    ]
    for url in probe_urls:
        r = fetch(url, retry=3, timeout=12)
        if r is not None:
            has_daily = "每日一练" in r.text
            has_practice = "practice" in r.text.lower()
            print("    -> 含'每日一练': %s, 含'practice': %s" % (has_daily, has_practice))
        time.sleep(0.5)
    print("勘察完成，页面已保存到 ks_home.html")


if __name__ == "__main__":
    main()
