# -*- coding: utf-8 -*-
"""案例1 建设库：会话+Referer 抓取真实数据页 p1/p2/p3，分析结构与企业列表"""
import re
import time

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
BASE_H = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

s = requests.Session()
print("=== 1. 先访问首页建立会话 ===")
r0 = s.get("https://www.jiansheku.com/", headers=BASE_H, timeout=20)
r0.encoding = "utf-8"
print("首页 HTTP", r0.status_code, len(r0.text), "| Cookies:", list(s.cookies.keys()))

H2 = dict(BASE_H)
H2["Referer"] = "https://www.jiansheku.com/"

for pg in (1, 2, 3):
    url = "https://www.jiansheku.com/search/enterprise/p%d/" % pg
    r = s.get(url, headers=H2, timeout=20)
    r.encoding = "utf-8"
    title = re.search(r"<title>(.*?)</title>", r.text, re.S)
    n_com = r.text.count("有限公司")
    print("\n=== 2. %s ===" % url)
    print("HTTP %s | %d 字节 | 标题: %s | '有限公司'出现: %d 次"
          % (r.status_code, len(r.text), (title.group(1).strip() if title else "-"), n_com))
    if pg == 3:
        with open("分析素材/jsk_p3_data.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        print("已保存 分析素材/jsk_p3_data.html")
        # 分页信息
        for pat in [r"共\s*[\d,]+", r"[\d,]+\s*条", r"total[^,}\n]{0,40}",
                    r"/search/enterprise/p(\d+)/", r"page[s]?[\"':= ]{1,3}(\d+)"]:
            hits = re.findall(pat, r.text, re.I)
            print("  分页线索 %r -> %s %s" % (pat, len(hits), hits[:8]))
        # 企业链接
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>\s*([^<]*?有限公司[^<]*?)\s*</a>',
                           r.text, re.S)
        print("  企业名+链接数:", len(links))
        for h, t in links[:6]:
            print("    %s -> %s" % (t.strip()[:36], h))
        # 唯一企业名去重
        names = re.findall(r"([\u4e00-\u9fa5（）()A-Za-z0-9]{4,40}有限公司)", r.text)
        uniq = list(dict.fromkeys(n.strip() for n in names))
        print("  页面内唯一企业名: %d 个" % len(uniq))
        for n in uniq[:10]:
            print("    -", n)
    time.sleep(1)
