# -*- coding: utf-8 -*-
"""案例1 建设库 企业搜索数据爬虫（Day20 逆向作业 · 正式交付版）

目标站点: https://www.jiansheku.com/search/enterprise/   （建设库 - 企业搜索）
数据接口: POST https://capi.jiansheku.com/nationzj/enterprice/page

逆向要点（结合 Day21 课件 04/05 jianzhushe 案例）:
  1. 接口请求头需携带 sign + timestamp 两个签名参数，缺失/过期会被拒绝；
  2. sign = 三层 MD5 套娃：
       factor1 = MD5(参数序列化串 + K1 + timestamp)
       factor2 = MD5(factor1 + K2 + timestamp)
       sign    = MD5(factor2 + K3 + timestamp)
     其中参数序列化 = 参数按 key 排序后拼 "key=value&"（数组/对象 JSON 化，
     空值跳过；数组元素中的 null 字段先清理）；
  3. 需先用 Session 访问一次主页建立会话再请求接口。

输出: 作业结果/案例1_建设库_企业数据.json / .csv（仅本地保留，结果数据不入公开仓库）

合规声明: 本脚本仅用于个人学习研究（逆向技术练习），禁止用于商业用途或规模化抓取；
         保持低频访问（页间隔 1 秒），仅采集匿名公开数据，不绕过登录/付费限制。
"""
import csv
import hashlib
import json
import os
import re
import time

import requests

# ==================== 参数配置 ====================
PAGES = 3                  # 抓取页数，每页 20 条
OUT_DIR = "作业结果"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
API = "https://capi.jiansheku.com/nationzj/enterprice/page"
# ==================================================


# ---------- sign 算法（Python 复刻自 Day21 课件 05 jianzhushe.js） ----------
K1 = "ZuSj0gwgsKXP4fTEz55oAG2q2p1SVGKK"
K2 = "mwMlWOdyM7OXbjzQPulT1ndRZIAjShDB"
K3 = "ghaepVf6IhcHmgnk4NCTXLApxQkBcvh1"


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def ku(t):
    """JS ku 函数复刻：数组清理 null 字段后 JSON 序列化并剥掉首尾引号/空白；
    对象 JSON 序列化；其他类型原样返回"""
    if isinstance(t, list):
        for item in t:
            if isinstance(item, dict):
                for key in [k for k, v in item.items() if v is None]:
                    del item[key]
                for v in item.values():
                    if isinstance(v, list):
                        ku(v)
        s = json.dumps(t, ensure_ascii=False, separators=(",", ":"))
        return re.sub(r'^(\s|")+|(\s|")+$', "", s)
    if isinstance(t, dict):
        return json.dumps(t, ensure_ascii=False, separators=(",", ":"))
    return t


def cu(param):
    """JS Cu 函数复刻：参数按 key 排序后拼成 key=value& 串（空值跳过）"""
    parts = []
    for k in sorted(param.keys()):
        r = ku(param[k])
        if r is None or str(r) == "":
            continue
        parts.append("%s=%s&" % (k, r))
    return "".join(parts)


def su(key, data, ts):
    """JS Su 函数复刻：MD5(data + key + timestamp)"""
    return md5(str(data) + key + str(ts))


def get_sign(param, ts):
    """三层 MD5 套娃签名"""
    return su(K3, su(K2, su(K1, cu(param), ts), ts), ts)
# --------------------------------------------------------------------------


def build_body(page):
    """构造接口请求体（搜索页默认条件，仅页码变化）"""
    return {
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
        "page": {"page": page, "limit": 20, "field": "", "order": ""},
    }


def fetch_page(session, page):
    """请求一页数据，返回 data 字典（含 total / list）"""
    body = build_body(page)
    ts = int(time.time() * 1000)
    sign = get_sign(body, ts)
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "devicetype": "PC",
        "origin": "https://www.jiansheku.com",
        "page": "search-enterprise",
        "referer": "https://www.jiansheku.com/",
        "sign": sign,
        "timestamp": str(ts),
        "user-agent": UA,
    }
    resp = session.post(API, headers=headers, json=body, timeout=20)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 200:
        raise RuntimeError("接口返回异常: %s" % result.get("msg"))
    return result.get("data") or {}


def collect_labels(labels):
    """递归收集标签名（labels -> labelName，含 children）"""
    names = []

    def walk(arr):
        for it in arr or []:
            if it.get("labelName"):
                names.append(it["labelName"])
            walk(it.get("children"))

    walk(labels)
    return "|".join(names)


def parse_record(rec):
    """把接口返回的单条记录映射为交付字段"""
    return {
        "企业ID": rec.get("id"),
        "企业名称": rec.get("name"),
        "简称": rec.get("nameSimple"),
        "经营状态": rec.get("businessStatus"),
        "法定代表人": rec.get("legalPerson"),
        "注册资本(万元)": rec.get("registeredCapitalStr") or rec.get("registeredCapital"),
        "成立日期": rec.get("registeredDate"),
        "统一社会信用代码": rec.get("creditCode"),
        "注册地址": rec.get("businessAddress"),
        "归属地": rec.get("domicile"),
        "企业资质数": rec.get("aptitudeCountNew"),
        "中标业绩数": rec.get("jskBidCount"),
        "四库业绩数": rec.get("projectCount"),
        "注册人员数": rec.get("persionCount"),
        "客户数": rec.get("customerCount"),
        "供应商数": rec.get("supplierCount"),
        "标签": collect_labels(rec.get("labels")),
        "详情页": "https://www.jiansheku.com/enterprise/%s/" % rec.get("id"),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    session = requests.Session()
    r = session.get("https://www.jiansheku.com/",
                    headers={"user-agent": UA}, timeout=20)
    print("主页状态: %d（建立会话）" % r.status_code)

    rows = []
    total = None
    for pg in range(1, PAGES + 1):
        data = fetch_page(session, pg)
        total = data.get("total")
        lst = data.get("list") or []
        print("第 %d 页: 抓到 %d 条 | 平台企业总数: %s" % (pg, len(lst), total))
        for rec in lst:
            rows.append(parse_record(rec))
        time.sleep(1)

    # 保存 JSON（完整数据）
    json_path = os.path.join(OUT_DIR, "案例1_建设库_企业数据.json")
    payload = {
        "案例": "案例1 建设库-企业搜索数据",
        "来源": "https://www.jiansheku.com/search/enterprise/",
        "接口": API,
        "平台企业总数": total,
        "抓取页数": PAGES,
        "抓取条数": len(rows),
        "抓取时间": time.strftime("%Y-%m-%d %H:%M:%S"),
        "数据": rows,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    # 保存 CSV
    csv_path = os.path.join(OUT_DIR, "案例1_建设库_企业数据.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("\n已保存:")
    print("  " + json_path, "(%d 条)" % len(rows))
    print("  " + csv_path)
    print("\n前 3 条预览:")
    for row in rows[:3]:
        print("  %s | %s | %s | 中标业绩:%s | 四库业绩:%s" % (
            row["企业ID"], row["企业名称"], row["法定代表人"],
            row["中标业绩数"], row["四库业绩数"]))


if __name__ == "__main__":
    main()
