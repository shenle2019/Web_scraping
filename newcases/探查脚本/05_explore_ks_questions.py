# -*- coding: utf-8 -*-
"""勘察答题页 /practice/getQuestion?...&day=... 内部调用的题目接口"""
import os
import re
import sys
import time

import requests

# 脚本位于子目录：把上级目录（newcases）加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proxy_pool import get_proxies

BASE = "https://ks.wangxiao.cn"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    ),
    "Referer": "https://ks.wangxiao.cn/practice/listEveryday?sign=jz1",
}


def fetch(url, retry=6, timeout=15, method="GET", json_body=None, extra_headers=None):
    headers = dict(HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    for i in range(retry):
        try:
            if method == "POST":
                resp = requests.post(url, headers=headers, json=json_body,
                                     proxies=get_proxies(), timeout=timeout)
            else:
                resp = requests.get(url, headers=headers,
                                    proxies=get_proxies(), timeout=timeout)
            print("[try %d] %s %s -> HTTP %s, %d bytes" % (
                i + 1, method, url, resp.status_code, len(resp.text)))
            if resp.status_code == 200 and len(resp.text) > 100:
                return resp
        except requests.RequestException as exc:
            print("[try %d] 异常: %s" % (i + 1, exc))
        time.sleep(1)
    return None


def main():
    # 1. 抓答题页，找内部接口
    page_url = (BASE + "/practice/getQuestion?practiceType=1&sign=jz1"
                "&subsign=22c51d8d3ccb4e309a60&day=20261009")
    resp = fetch(page_url)
    if resp is None:
        return
    html = resp.text
    with open("ks_getquestion_jz1.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\n--- HTML 中出现的接口路径 ---")
    for m in re.finditer(r"['\"](/[a-zA-Z0-9_/]*(?:Questions|question|Question)[a-zA-Z0-9_/]*)['\"]", html):
        print(m.group(1))
    for m in re.finditer(r"(listQuestions|getQuestions|questionList)", html):
        print("包含关键词:", m.group(1))

    print("\n--- 页面中的 sign/subsign/day/practiceType 变量 ---")
    for m in re.finditer(r"(var\s+\w+\s*=\s*[^;\n]{0,120})", html):
        s = m.group(1)
        if any(k in s for k in ("sign", "subsign", "day", "practiceType", "top")):
            print(s.strip())

    print("\n--- 直接探测 listQuestions 接口(POST) ---")
    api = BASE + "/practice/listQuestions"
    body = {
        "examPointType": "",
        "practiceType": "1",
        "questionType": "",
        "sign": "jz1",
        "subsign": "22c51d8d3ccb4e309a60",
        "top": "20",
        "day": "20261009",
    }
    r2 = fetch(api, method="POST", json_body=body,
               extra_headers={"Content-Type": "application/json; charset=UTF-8"})
    if r2 is not None:
        text = r2.text[:600]
        print("响应片段:", text)
        try:
            data = r2.json()
            print("JSON 顶层键:", list(data.keys()))
            d = data.get("Data")
            if isinstance(d, list):
                print("Data 条数:", len(d))
                if d:
                    print("第一条键:", list(d[0].keys())[:15])
        except Exception as exc:
            print("非JSON:", exc)


if __name__ == "__main__":
    main()
