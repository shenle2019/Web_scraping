# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

mitmproxy 抓包插件：把命中本地靶场的请求原样落到 capture.log（一行一个 JSON）。
只记录 192.168.31.220:8080 的流量，避免把手机其他 App 的数据一起写进来。

用法：
    mitmdump -q -p 8890 -s capture_dump.py --set confdir=./.mitm
手机端：settings put global http_proxy 192.168.31.220:8890
"""
import json
import os
import time

from mitmproxy import http

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capture.log")
TARGET = "192.168.31.220:8080"


def response(flow: http.HTTPFlow):
    if TARGET not in flow.request.pretty_url:
        return
    headers = {k: v for k, v in flow.request.headers.items()
               if k.lower() not in ("proxy-connection",)}
    rec = {
        "time": time.strftime("%H:%M:%S"),
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "headers": headers,
        "body": flow.request.get_text(strict=False),
        "status": flow.response.status_code if flow.response else None,
        "resp": (flow.response.get_text(strict=False)[:160] if flow.response else ""),
    }
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
