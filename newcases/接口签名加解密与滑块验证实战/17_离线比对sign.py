# -*- coding: utf-8 -*-
"""建设库：用真实抓包的 body+timestamp 离线复算 sign，验证算法是否仍有效"""
import json

from jsk_sign_util import cu, get_sign

captured = json.load(open("分析素材/jsk_live_request.json", encoding="utf-8"))
print("捕获请求数:", len(captured))
for i, c in enumerate(captured):
    h = c["headers"]
    ts = h.get("timestamp")
    real = h.get("sign")
    print("\n--- 请求 %d ---" % i)
    print("URL:", c["url"])
    print("timestamp:", ts, "| 真实 sign:", real)
    print("关键头 page=%s devicetype=%s" % (h.get("page"), h.get("devicetype")))
    if c.get("post_data"):
        try:
            body = json.loads(c["post_data"])
            print("body 键:", list(body.keys()))
            print("序列化串:", cu(body)[:300], "...")
            mine = get_sign(body, int(ts))
            print("复算 sign:", mine)
            print(">>> 一致:", mine == real)
        except Exception as e:
            print("body 处理失败:", e)
    # 只在第 1 个上详细做
    if i >= 1:
        break
