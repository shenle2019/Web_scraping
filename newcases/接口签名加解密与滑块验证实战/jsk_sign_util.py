# -*- coding: utf-8 -*-
"""建设库 sign 算法工具模块（Python 复刻自 jianzhushe.js）
   算法: sign = MD5( mid + K3 + ts )，其中 mid = MD5( inner + K2 + ts )，inner = MD5( 序列化参数 + K1 + ts )
"""
import hashlib
import json
import re

K1 = "ZuSj0gwgsKXP4fTEz55oAG2q2p1SVGKK"
K2 = "mwMlWOdyM7OXbjzQPulT1ndRZIAjShDB"
K3 = "ghaepVf6IhcHmgnk4NCTXLApxQkBcvh1"


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def ku(t):
    """JS ku 复刻：数组清理 null 后序列化并剥离首尾引号/空白；对象序列化；其他原样"""
    if isinstance(t, list):
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
    """参数序列化: key 排序后拼 key=value&（空值跳过）"""
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
    """MD5(data + key + time)（与 JS n = t + e + time 一致）"""
    return md5(str(data) + key + str(ts))


def get_sign(param, ts):
    t = cu(param)
    inner = su(K1, t, ts)
    mid = su(K2, inner, ts)
    return su(K3, mid, ts)
