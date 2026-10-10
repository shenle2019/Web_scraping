# -*- coding: utf-8 -*-
"""
Day21 练习案例 1/4 —— 新东方搜课 souke.xdf.cn「请求头 sign 签名」逆向（MD5）
============================================================================
【练习来源】Day21 课件「练习案例」base64 目标1：
    aHR0cHM6Ly9zb3VrZS54ZGYuY24vc2VhcmNoP2NpdHlDb2RlPTExMDEwMCZrdz0lRTglOEIlQjElRTglQUYlQUQ=
    = https://souke.xdf.cn/search?cityCode=110100&kw=英语

【逆向结论】（关键字搜索 + 定位 pages/search chunk 所得）
    接口:  GET https://dsapi.xdf.cn/product/v2/class/search?{params}
    签名:  sign = MD5(params + "750F82C2-D8F6-49F6-878C-1E7EBEBC8DA2")   (小写hex)
    参数:  params = "appId=5053&t=<毫秒时间戳>" + 逐个追加 "&k=v"（跳过假值）
    头部:  {"Content-Type": "application/json", "sign": sign}
    来源:  ot()/DTmv(a=5053, b=密钥, d=//dsapi.xdf.cn)/aCH8(crypto-js md5.hex)

【合规声明】匿名、低频（每次运行仅 1~2 个请求）、仅用于学习验证签名算法，
           不批量采集、不绕过任何登录/风控，输出数据仅本地留存。
"""
import hashlib
import json
import os
import time
import urllib.parse

import requests

API_BASE = "https://dsapi.xdf.cn"
APP_ID = "5053"
SIGN_KEY = "750F82C2-D8F6-49F6-878C-1E7EBEBC8DA2"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def build_params(extra: dict):
    """复刻 ot()：appId + t 打头，其余键按传入顺序追加（跳过假值）"""
    ts = str(int(time.time() * 1000))
    parts = ["appId=%s" % APP_ID, "t=%s" % ts]
    for k, v in extra.items():
        if v is None:
            continue
        sv = str(v)
        if sv in ("", "undefined", "null"):
            continue
        parts.append("%s=%s" % (k, sv))
    return "&".join(parts), ts


def make_sign(param_str: str) -> str:
    """复刻 Je = crypto-js MD5（默认 bytesToHex 小写）"""
    return hashlib.md5((param_str + SIGN_KEY).encode("utf-8")).hexdigest()


def request_search(params: str, sign: str, timeout=15):
    url = "%s/product/v2/class/search?%s" % (API_BASE, params)
    headers = {
        "User-Agent": UA,
        "Referer": "https://souke.xdf.cn/",
        "Origin": "https://souke.xdf.cn",
        "Content-Type": "application/json",
        "sign": sign,
    }
    return requests.get(url, headers=headers, timeout=timeout)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    keyword = urllib.parse.quote("英语")           # 对应页面 kw=%E8%8B%B1%E8%AF%AD
    extra = {"cityCode": "110100", "pageIndex": 1, "pageSize": 12, "keyword": keyword}
    params, ts = build_params(extra)
    sign = make_sign(params)

    print("=" * 72)
    print("[1] 复刻签名")
    print("    params :", params)
    print("    sign   :", sign)

    # ---- 对照组：同参数 + 错误 sign（验证服务端确实校验签名）----
    bad = request_search(params, "0" * 32)
    print("\n[2] 对照组（错误 sign）HTTP %s -> %s" % (bad.status_code, bad.text[:180]))

    # ---- 正确 sign 请求 ----
    time.sleep(1.2)
    resp = request_search(params, sign)
    print("\n[3] 正确 sign 请求 HTTP %s" % resp.status_code)
    try:
        data = resp.json()
        ok = (data.get("status") == 1 and str(data.get("code")) == "200"
              and isinstance(data.get("data", {}).get("classList"), list))
        print("    应答 code=%s status=%s totalRecords=%s classList=%d 条 -> %s"
              % (data.get("code"), data.get("status"),
                 data.get("data", {}).get("totalRecords"),
                 len(data.get("data", {}).get("classList") or []),
                 "签名验证通过" if ok else "应答结构不符"))
    except ValueError:
        data = None
        ok = False
        print("    非 JSON 响应：", resp.text[:200])

    result = {
        "target": "souke.xdf.cn / dsapi.xdf.cn class/search",
        "params": params,
        "sign": sign,
        "http_status": resp.status_code,
        "verified": bool(ok),
        "sample": (data or {}).get("data", {}).get("classList", [])[:3],
    }
    fp = os.path.join(OUT_DIR, "souke_sign_result.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n[4] 验证结果已保存: %s" % fp)


if __name__ == "__main__":
    main()
