# -*- coding: utf-8 -*-
"""
30：完整爬虫 —— 对抗反调试 + Hook 定位 + 数据采集（一体化演示）
=========================================================
把 Day25 全部技术点串成一条真实的爬虫工作流：
  1. 注入 hook_scripts/anti_debugger.js —— 对抗无限 debugger，保证自动化不被拖住
  2. 注入 hook_cookie / hook_header / hook_eval —— 定位风控参数（令牌/签名/密钥）
  3. 打开页面，等待数据接口返回
  4. 采集数据：接口响应路线（主）+ DOM 解析路线（对照）
  5. 汇总输出：数据落盘 output/*.json；hook 定位摘要 + 结论打印

用法：
  python 30_crawler_full.py [--out output]

合规声明：目标为本地模拟站（自造数据），无任何真实站点请求。
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from playwright.sync_api import sync_playwright
import pw_common as C


def main():
    ap = argparse.ArgumentParser(description="Hook 演示站完整采集（学习验证用）")
    ap.add_argument("--out", type=str, default=os.path.join(C.BASE, "output"), help="输出目录")
    args = ap.parse_args()

    C.hr("30 完整爬虫：对抗反调试 + Hook 定位 + 数据采集")

    api_payloads = []   # 接口响应路线
    api_requests = []

    ok = True
    with C.LocalSite():
        with sync_playwright() as p:
            browser = C.launch_browser(p)
            context = browser.new_context()
            page = context.new_page()

            def on_response(resp):
                if "/api/goods" in resp.url:
                    try:
                        api_payloads.append({"url": resp.url, "status": resp.status, "json": resp.json()})
                    except Exception:
                        pass

            def on_request(req):
                if "/api/goods" in req.url:
                    api_requests.append(req.url)

            page.on("response", on_response)
            page.on("request", on_request)

            # 反调试对抗 + 三件套 hook（文档创建前注入）
            C.inject(page,
                     "hook_scripts/anti_debugger.js",
                     "hook_scripts/hook_cookie.js",
                     "hook_scripts/hook_header.js",
                     "hook_scripts/hook_eval.js")

            page.goto(C.URL_HOME, wait_until="domcontentloaded")
            page.wait_for_selector("#goods-list li", timeout=15000)
            page.wait_for_timeout(500)

            # ---------- 采集路线1：接口响应 ----------
            items_api = []
            for pl in api_payloads:
                if pl["status"] == 200 and isinstance(pl["json"], dict):
                    items_api = pl["json"].get("items", [])
            print("[30] 接口响应路线：HTTP %s，获取 %d 条" %
                  (api_payloads[0]["status"] if api_payloads else "无", len(items_api)))

            # ---------- 采集路线2：DOM 解析（对照） ----------
            items_dom = []
            for li in page.locator("#goods-list li").all():
                name_price = li.inner_text().split("\n")
                items_dom.append({"name": name_price[0].strip()})
            print("[30] DOM 解析路线：获取 %d 条" % len(items_dom))

            # ---------- Hook 定位摘要 ----------
            hook_cookie = page.evaluate("window.__hookCookie || []")
            hook_header = page.evaluate("window.__hookHeader || []")
            hook_eval = page.evaluate("window.__hookEval || []")
            anti_stats = page.evaluate("window.__antiStats || null")

            token_val = ""
            if hook_cookie:
                m = re.search(r"access_token=([^;]+)", hook_cookie[0]["value"])
                token_val = m.group(1) if m else ""
            sign_val = next((r["value"] for r in hook_header if r["name"].lower() == "x-sign"), "")
            eval_plain = next((r["code"] for r in hook_eval if r["type"] == "eval" and "secHash" in r["code"]), "")
            m_s = re.search(r'SECRET_S="([^"]+)"', eval_plain)
            secret_s = m_s.group(1) if m_s else ""

            print("\n[30] Hook 定位摘要：")
            print("     cookie 令牌 access_token = %s" % token_val)
            print("     请求头 X-Sign            = %s" % sign_val)
            print("     混淆段还原密钥 SECRET_S  = %s" % secret_s)
            print("     反调试对抗留痕           = %s" % anti_stats)

            # ---------- 输出数据 ----------
            os.makedirs(args.out, exist_ok=True)
            ts_name = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = os.path.join(args.out, "hook_demo_goods_%s.json" % ts_name)
            record = {
                "来源": C.URL_HOME + "（本地模拟站，自造数据）",
                "接口": "/api/goods",
                "风控机制": "cookie 令牌 + X-Sign 签名 + 无限 debugger 反调试",
                "对抗与定位": "anti_debugger.js 源头切断无限断点；hook cookie/header/eval 定位风控参数",
                "hook摘要": {
                    "access_token": token_val,
                    "X-Sign": sign_val,
                    "还原的 SECRET_S": secret_s,
                    "antiStats": anti_stats,
                },
                "采集时间": ts_name,
                "条数": len(items_api),
                "数据": items_api,
                "DOM对照条数": len(items_dom),
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=1)
            print("\n[30] 数据已写入: %s" % out_path)

            browser.close()

    print("\n----- 结论断言 -----")
    ok &= C.check("接口响应路线采集到 12 条数据", len(items_api) == 12)
    ok &= C.check("DOM 解析路线条数一致（12 条）", len(items_dom) == 12)
    ok &= C.check("cookie 令牌已被 hook 捕获", bool(token_val))
    ok &= C.check("X-Sign 签名已被 hook 捕获", bool(sign_val))
    ok &= C.check("混淆密钥已被 hook 还原", secret_s == "hk-demo-sign-salt-2026")
    ok &= C.check("无限 debugger 已被对抗（有留痕且页面未被拖死）",
                  bool(anti_stats) and anti_stats.get("intervalBlocked", 0) >= 1)

    C.hr("30 结论: " + ("全部通过 —— 反调试被对抗、风控参数被定位、数据采集完成" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
