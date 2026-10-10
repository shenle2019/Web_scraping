# -*- coding: utf-8 -*-
"""
Day21 练习案例 4/4 —— 贝壳找房 bj.ke.com「SSR + 异步接口参数」逆向
============================================================================
【练习来源】Day21 课件「练习案例」base64 目标4：
    aHR0cHM6Ly9iai5rZS5jb20vP3V0bV9zb3VyY2U9YmFpZHUmdXRtX21lZGl1bT1waW56aHVhbiZ1dG1fdGVybT1iaWFvdGkmdXRtX2NvbnRlbnQ9Ymlhb3RpbWlhb3NodSZ1dG1fY2FtcGFpZ249d3liZWlqaW5n
    = https://bj.ke.com/?utm_source=baidu&utm_medium=pinzhuan&utm_term=biaoti&utm_content=biaotimiaoshu&utm_campaign=wybeijing

【逆向结论】（页面 SSR 结构 + sellList/index.js 异步调用定位所得）
    1) 二手房列表页为 SSR 直出：
       https://bj.ke.com/ershoufang/          首页 30 条房源
       https://bj.ke.com/ershoufang/pg{n}     翻页（totalPage=100）
       页面内嵌 window.GLOBAL_INFOS 提供全部接口上下文：
         url        = "/web/ershoufang/sidebar"     （异步侧栏接口路径）
         sidebar    = {type:"city", cityId:110000, id:110000,
                       uuid:"8dbd37b0-41fc-4204-982d-706ceac36fd8", ucid:null}
         count      = 118360  （北京在售二手房总数）
         ids        = "101133..."  （本页 30 套房源 id 列表）
    2) 侧栏异步接口（getAsyncData 实现：$.ajax({url: API_URL+url, dataType:"jsonp"})）:
       注意 API_URL 来自 ljConf.domainConfig.ajaxapiroot = "https://ajax.api.ke.com/"
       GET https://ajax.api.ke.com/web/ershoufang/sidebar
           ?cityId=110000&id=110000&uuid=<uuid>&ucid=&type=city&callback=jQuery...&_=<ts>
       （JSONP 包装 jQuery...({...})，errno=0 时 data 含 price/agent/guide/
         resblock/redian/wenda/baike/vpoint/ditu 等 10 类数据）
    3) 搜索建议接口（sellList 搜索组件）：
       GET https://bj.ke.com/api/headerSearchForPlatC
           ?channel=ershoufang&cityId=110000&query=<关键字>
       （channel 映射 {sell:"ershoufang",...}[type]，cityId 取自 cookie select_city）

【合规声明】匿名、低频（每次运行仅 3 个请求）、仅用于学习验证页面结构与
           接口参数逆向结论，不批量翻页采集、不绕过任何登录/风控，
           输出数据仅本地留存。
"""
import json
import os
import re
import time

import requests

BASE = "https://bj.ke.com"
AJAX_API = "https://ajax.api.ke.com"          # ljConf.domainConfig.ajaxapiroot
LIST_URL = BASE + "/ershoufang/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def fetch_list_page():
    headers = {"User-Agent": UA, "Referer": BASE + "/"}
    resp = requests.get(LIST_URL, headers=headers, timeout=20)
    t = resp.text
    print("    HTTP %s  页面长度=%d" % (resp.status_code, len(t)))

    # 定位 window.GLOBAL_INFOS 块（JS 对象字面量，非严格 JSON，用正则逐字段提取）
    gi_pos = t.find("GLOBAL_INFOS")
    gi_seg = t[gi_pos:gi_pos + 6000] if gi_pos >= 0 else ""

    def pick(pat, default=None):
        m = re.search(pat, gi_seg)
        return m.group(1) if m else default

    info = {
        "url": pick(r"url\s*:\s*'([^']+)'"),
        "sidebar_raw": pick(r"sidebar\s*:\s*(\{[^}]+\})"),
        "count": pick(r"count\s*:\s*(\d+)"),
        "page_num": pick(r"pageNum\s*:\s*(\d+)"),
        "ids": pick(r"ids\s*:\s*'([^']*)'", ""),
    }
    info["sidebar"] = json.loads(info["sidebar_raw"]) if info["sidebar_raw"] else None
    info["ids_count"] = len(info["ids"].split(",")) if info["ids"] else 0

    # SSR 直出房源数 / 总页数
    info["ssr_items"] = len(re.findall(r'class="info clear"', t))
    m_tp = re.search(r'totalPage["\']?\s*:\s*(\d+)', t)
    info["total_page"] = m_tp.group(1) if m_tp else None

    print("    GLOBAL_INFOS: url=%s count=%s pageNum=%s ids=%d 个"
          % (info["url"], info["count"], info["page_num"], info["ids_count"]))
    print("    sidebar 参数: %s" % json.dumps(info["sidebar"], ensure_ascii=False))
    print("    SSR 房源块 %d 个 / totalPage=%s" % (info["ssr_items"], info["total_page"]))
    return info


def fetch_sidebar(info):
    """JSONP 方式请求侧栏接口：真实域名为 ljConf.domainConfig.ajaxapiroot"""
    sb = info["sidebar"] or {}
    ts = int(time.time() * 1000)
    cb = "jQuery1102000000000000000000_%d" % ts
    params = {
        "cityId": sb.get("cityId"),
        "id": sb.get("id"),
        "uuid": sb.get("uuid"),
        "ucid": sb.get("ucid") or "",
        "type": sb.get("type") or "city",
        "callback": cb,
        "_": ts,
    }
    url = AJAX_API + (info["url"] or "/web/ershoufang/sidebar")
    headers = {"User-Agent": UA, "Referer": LIST_URL}
    resp = requests.get(url, params=params, headers=headers, timeout=20)
    print("    GET %s" % resp.url)
    print("    HTTP %s  Content-Type=%s" % (resp.status_code,
                                            resp.headers.get("Content-Type", "")))
    m = re.match(r"^[^(]*\((.*)\)\s*;?\s*$", resp.text.strip(), re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            keys = list((data.get("data") or {}).keys())
            print("    JSONP 解析成功 errno=%s request_id=%s"
                  % (data.get("errno"), data.get("request_id")))
            print("    data 分区: %s" % keys[:12])
            return resp.status_code, data
        except ValueError:
            pass
    print("    非 JSONP/JSON 响应: %s" % resp.text[:180])
    return resp.status_code, None


def fetch_suggest(keyword="望京"):
    url = BASE + "/api/headerSearchForPlatC"
    headers = {"User-Agent": UA, "Referer": LIST_URL}
    params = {"channel": "ershoufang", "cityId": "110000", "query": keyword}
    resp = requests.get(url, params=params, headers=headers, timeout=20)
    print("    GET %s" % resp.url)
    print("    HTTP %s" % resp.status_code)
    try:
        data = resp.json()
        result = (data.get("data") or {}).get("result") or []
        print("    code=%s 建议条数=%d" % (data.get("code"), len(result)))
        for i, it in enumerate(result[:5], 1):
            text = it.get("text") or it.get("title") or it.get("str") or str(it)[:40]
            print("      %d. %s" % (i, str(text)[:60]))
    except ValueError:
        data, result = None, []
        print("    非 JSON 响应: %s" % resp.text[:180])
    return resp.status_code, data, result


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=" * 72)
    print("[1] SSR 列表页解析: %s" % LIST_URL)
    info = fetch_list_page()

    time.sleep(1.5)
    print("\n[2] 侧栏异步接口（GLOBAL_INFOS.url + sidebar 参数）")
    sb_status, sb_data = fetch_sidebar(info)

    time.sleep(1.5)
    print("\n[3] 搜索建议接口 headerSearchForPlatC（query=望京）")
    sug_status, sug_data, sug_result = fetch_suggest("望京")

    verified = (bool(info["sidebar"]) and info["ids_count"] > 0
                and sb_status == 200 and isinstance(sb_data, dict)
                and sb_data.get("errno") == 0)
    result = {
        "target": "bj.ke.com 北京二手房（SSR + sidebar + headerSearchForPlatC）",
        "ssr": {
            "count": info["count"],
            "page_num": info["page_num"],
            "ssr_items": info["ssr_items"],
            "total_page": info["total_page"],
            "ids_count": info["ids_count"],
        },
        "sidebar": {
            "status": sb_status,
            "errno": sb_data.get("errno") if isinstance(sb_data, dict) else None,
            "request_id": sb_data.get("request_id") if isinstance(sb_data, dict) else None,
            "data_keys": list((sb_data.get("data") or {}).keys())[:12]
                         if isinstance(sb_data, dict) else None,
        },
        "suggest": {"status": sug_status,
                    "count": len(sug_result),
                    "sample": sug_result[:3]},
        "verified": verified,
    }
    fp = os.path.join(OUT_DIR, "ke_ershoufang_result.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n[4] 验证结果已保存: %s" % fp)


if __name__ == "__main__":
    main()
