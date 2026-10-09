# -*- coding: utf-8 -*-
"""建设库 API 直连测试（Day21 课件 04 jianzhushe.py 的复刻验证）
链路: Session 访问首页建立会话(拿 WAF cookie) -> 计算 sign(三层MD5) -> POST capi 接口
"""
import json
import time

import requests

from jsk_sign_util import get_sign

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

s = requests.Session()
base_h = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "user-agent": UA,
}

# 第一步：访问首页和搜索页，建立会话（拿华为 WAF 会话 cookie）
r0 = s.get("https://www.jiansheku.com/", headers=base_h, timeout=20)
print("首页:", r0.status_code, "| cookies:", list(s.cookies.keys()))
r1 = s.get("https://www.jiansheku.com/search/enterprise/", headers=base_h, timeout=20)
print("搜索页:", r1.status_code, "| 标题:", r1.text[r1.text.find("<title>") + 7: r1.text.find("</title>")][:60])

# 第二步：构造请求体（与课件一致）并计算 sign
json_data = {
    "eid": "",
    "achievementQueryType": "and",
    "achievementQueryDto": [],
    "personnelQueryDto": {"queryType": "and"},
    "aptitudeQueryDto": {
        "queryType": "and",
        "nameStr": "",
        "aptitudeQueryType": "and",
        "businessScopeQueryType": "or",
        "filePlaceType": "1",
        "aptitudeDtoList": [
            {"codeStr": "", "queryType": "and", "aptitudeType": "qualification"},
        ],
        "aptitudeSource": "new",
    },
    "page": {"page": 1, "limit": 20, "field": "", "order": ""},
}

timer = int(time.time() * 1000)
sign = get_sign(json_data, timer)
print("\nsign =", sign, "\ntimestamp =", timer)

# 第三步：带 sign 请求 API
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "devicetype": "PC",
    "origin": "https://www.jiansheku.com",
    "page": "search-enterprise",
    "pragma": "no-cache",
    "referer": "https://www.jiansheku.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sign": sign,
    "timestamp": str(timer),
    "user-agent": UA,
}

resp = s.post("https://capi.jiansheku.com/nationzj/enterprice/page",
              headers=headers, json=json_data, timeout=20)
print("\nAPI 状态码:", resp.status_code)
print("响应前 500 字符:\n", resp.text[:500])

# 第四步：解析响应
try:
    data = resp.json()
    print("\nJSON 键:", list(data.keys()))
    inner = data.get("data") or {}
    if isinstance(inner, dict):
        print("data 子键:", list(inner.keys()))
        lst = inner.get("list") or []
        print("本页条数:", len(lst), "| 总数:", inner.get("total"))
        if lst:
            print("\n第一条示例:")
            print(json.dumps(lst[0], ensure_ascii=False, indent=1)[:800])
except Exception as e:
    print("\n解析 JSON 失败:", type(e).__name__, e)
