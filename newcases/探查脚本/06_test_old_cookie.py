# -*- coding: utf-8 -*-
"""测试 ks_config_local.py 中的登录 Cookie 是否还能调用 listQuestions 接口"""
import os
import sys
import time

import requests

# 脚本位于子目录：把上级目录（newcases）加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ks_config_local import COOKIE
except ImportError:
    sys.exit("请先复制 ks_config_example.py 为 ks_config_local.py 并填写 Cookie")

from proxy_pool import get_proxies

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    ),
    "Referer": "https://ks.wangxiao.cn/practice/listEveryday?sign=jz1",
    "Content-Type": "application/json; charset=UTF-8",
    "Cookie": COOKIE,
}


def main():
    url = "https://ks.wangxiao.cn/practice/listQuestions"
    body = {
        "practiceType": "1",
        "sign": "jz1",
        "subsign": "22c51d8d3ccb4e309a60",
        "day": "20261009",
    }
    for i in range(5):
        try:
            resp = requests.post(url, headers=HEADERS, json=body,
                                 proxies=get_proxies(), timeout=20)
            print("[try %d] HTTP %s, %d bytes" % (i + 1, resp.status_code, len(resp.text)))
            text = resp.text
            if "登录" in text[:2000] or "<!DOCTYPE" in text[:100]:
                print("=> 返回的是 HTML（可能是登录页），Cookie 已失效")
                print("片段:", text[:150])
                return
            data = resp.json()
            print("JSON 顶层键:", list(data.keys()))
            d = data.get("Data")
            if isinstance(d, list):
                print("Data 分段数:", len(d))
                for idx, seg in enumerate(d):
                    qs = seg.get("questions")
                    ms = seg.get("materials")
                    rule = seg.get("paperRule") or {}
                    print("  段%d: 题型=%s, questions=%s, materials=%s" % (
                        idx, rule.get("title"), len(qs) if qs else None,
                        len(ms) if ms else None))
                    if qs:
                        q0 = qs[0]
                        print("    首题键:", list(q0.keys()))
                        print("    content:", str(q0.get("content"))[:80])
                        opts = q0.get("options") or []
                        print("    options:", [(o.get("name"), str(o.get("content"))[:20], o.get("isRight")) for o in opts])
                        print("    textAnalysis:", str(q0.get("textAnalysis"))[:80])
            print("\n=== Cookie 有效！===")
            return
        except requests.RequestException as exc:
            print("[try %d] 异常: %s" % (i + 1, exc))
        except ValueError:
            print("非 JSON 响应，前100字符:", resp.text[:100])
            return
        time.sleep(1)


if __name__ == "__main__":
    main()
