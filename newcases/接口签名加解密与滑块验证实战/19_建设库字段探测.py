# -*- coding: utf-8 -*-
"""建设库 API 字段探测：打印单条记录的完整键值，供正式爬虫设计字段映射"""
import json
import time

import requests

from jsk_sign_util import get_sign

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

s = requests.Session()
s.get("https://www.jiansheku.com/", headers={"user-agent": UA}, timeout=20)

json_data = {
    "eid": "",
    "achievementQueryType": "and",
    "achievementQueryDto": [],
    "personnelQueryDto": {"queryType": "and"},
    "aptitudeQueryDto": {
        "queryType": "and", "nameStr": "", "aptitudeQueryType": "and",
        "businessScopeQueryType": "or", "filePlaceType": "1",
        "aptitudeDtoList": [{"codeStr": "", "queryType": "and", "aptitudeType": "qualification"}],
        "aptitudeSource": "new",
    },
    "page": {"page": 1, "limit": 20, "field": "", "order": ""},
}
timer = int(time.time() * 1000)
sign = get_sign(json_data, timer)

headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json;charset=UTF-8",
    "devicetype": "PC",
    "origin": "https://www.jiansheku.com",
    "page": "search-enterprise",
    "referer": "https://www.jiansheku.com/",
    "sign": sign,
    "timestamp": str(timer),
    "user-agent": UA,
}
resp = s.post("https://capi.jiansheku.com/nationzj/enterprice/page",
              headers=headers, json=json_data, timeout=20)
data = resp.json()
lst = data["data"]["list"]
print("本页条数:", len(lst))
rec = lst[0]
print("\n=== 第一条记录全部键值 ===")
for k, v in rec.items():
    vs = json.dumps(v, ensure_ascii=False)
    print("%-28s = %s" % (k, vs[:120]))

print("\n=== 第 1 条企业名/ID ===")
print("id:", rec.get("id"))
for k in ("companyName", "name", "entName", "enterpriseName", "title"):
    if k in rec:
        print(k, ":", rec[k])

print("\n=== 第 2-5 条企业名预览 ===")
for r2 in lst[1:5]:
    nm = None
    for k in ("companyName", "name", "entName", "enterpriseName"):
        if r2.get(k):
            nm = r2[k]
            break
    print(r2.get("id"), "|", nm)

# 保存一条完整记录样本供后续参考
with open("分析素材/jsk_api_record_sample.json", "w", encoding="utf-8") as f:
    json.dump(rec, f, ensure_ascii=False, indent=1)
print("\n已保存 分析素材/jsk_api_record_sample.json")
