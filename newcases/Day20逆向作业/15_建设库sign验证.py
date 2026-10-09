# -*- coding: utf-8 -*-
"""建设库 sign 算法 Python 复刻 + 实际请求 API 测试
算法来源: Day21 课件 05 jianzhushe.js（三层 MD5 套娃 + 参数序列化）
"""
import hashlib
import json
import re
import time

import requests

K1 = "ZuSj0gwgsKXP4fTEz55oAG2q2p1SVGKK"
K2 = "mwMlWOdyM7OXbjzQPulT1ndRZIAjShDB"
K3 = "ghaepVf6IhcHmgnk4NCTXLApxQkBcvh1"


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def ku(t):
    """JS ku 的 Python 复刻：数组清理 null 后序列化并剥离首尾引号/空白；对象序列化；其他原样"""
    if isinstance(t, list):
        # 清理数组内对象的 null 字段
        for item in t:
            if isinstance(item, dict):
                for k in [k for k, v in item.items() if v is None]:
                    del item[k]
                for k, v in item.items():
                    if isinstance(v, list):
                        ku(v)
        s = json.dumps(t, ensure_ascii=False, separators=(",", ":"))
        return re.sub(r'^(\s|")+|(\s|")+$', "", s)
    if isinstance(t, dict):
        return json.dumps(t, ensure_ascii=False, separators=(",", ":"))
    return t


def cu(param):
    """参数序列化: key 排序后拼 key=value&"""
    parts = []
    for k in sorted(param.keys()):
        r = ku(param[k])
        if r is None:
            continue
        rs = str(r)
        if rs == "":
            continue
        parts.append("%s=%s&" % (k, rs))
    return "".join(parts)


def su(key, data, ts):
    """MD5(data + key + time)（与 JS 的 n = t + e + time 一致）"""
    return md5(str(data) + key + str(ts))


def get_sign(param, ts):
    t = cu(param)
    inner = su(K1, t, ts)
    mid = su(K2, inner, ts)
    return su(K3, mid, ts)


PARAM_P3 = {
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
            {"codeStr": "", "queryType": "and", "aptitudeType": "qualification"}
        ],
        "aptitudeSource": "new",
    },
    "page": {"page": 3, "limit": 20, "field": "", "order": ""},
}

# 1. 与课件历史值对照
T = 1713265415045
sign = get_sign(dict(PARAM_P3), T)
print("=== 1. 算法复刻验证 ===")
print("序列化串:", cu(PARAM_P3))
print("复刻 sign:", sign)
print("课件历史值: 8d57e9c98a0c4e753cc08475d8016099")
print("一致:", sign == "8d57e9c98a0c4e753cc08475d8016099")

# 2. 实际请求测试（2026 年当前接口是否有效）
print("\n=== 2. 实际请求 capi.jiansheku.com ===")
now_ms = int(time.time() * 1000)
live_param = dict(PARAM_P3)
live_param["page"] = {"page": 1, "limit": 20, "field": "", "order": ""}
live_sign = get_sign(live_param, now_ms)

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.jiansheku.com",
    "referer": "https://www.jiansheku.com/",
    "devicetype": "PC",
    "page": "search-enterprise",
    "sign": live_sign,
    "timestamp": str(now_ms),
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
}

try:
    r = requests.post("https://capi.jiansheku.com/nationzj/enterprice/page",
                      headers=headers, json=live_param, timeout=20)
    print("HTTP", r.status_code, "| 响应长度:", len(r.text))
    print("响应前 600 字符:")
    print(r.text[:600])
    if r.status_code == 200:
        try:
            data = r.json()
            print("\nJSON 解析成功, 顶层键:", list(data.keys()))
            if "data" in data and isinstance(data["data"], dict):
                print("data 键:", list(data["data"].keys())[:10])
        except Exception as e:
            print("JSON 解析失败:", e)
except Exception as e:
    print("请求异常:", type(e).__name__, e)
