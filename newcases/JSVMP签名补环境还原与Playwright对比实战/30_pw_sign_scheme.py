# -*- coding: utf-8 -*-
"""
30：Playwright 方案 —— 真实浏览器环境运行 JSVMP 产出签名
=========================================================
思路（与 20 补环境方案的核心对比点）：
  不补环境、不碰字节码，直接在系统 Edge 里打开本地签名页
  （pw_assets/sign_page.html 加载 js_asset/source.js，与补环境共用同一份资产），
  页面内调用 window._webmsxyw 生成 X-s/X-t，Python 侧拿回签名请求 mock 站。

  浏览器环境天然给足一切（真实 navigator/document/location/Canvas），
  代价是必须启动浏览器、自动化痕迹需额外处理（本脚本演示 navigator.webdriver 修正）。

流程：
  1. 启动 mock 站 + Edge（headless, channel=msedge，免 playwright install）
  2. 打开签名页（add_init_script 修正 navigator.webdriver）
  3. 观察浏览器环境特征（UA / webdriver / cookie 字段数）
  4. 页面内签名 -> 结构分析（字段 / payload 长度 / 指纹头）
  5. 用浏览器签名请求 mock 站 -> 断言 200
  6. 与补环境方案的 payload 头 32 对比，结果落盘 output/pw_sign_result.json

运行：
  python run_log.py 30_pw_sign.txt -- python 30_pw_sign_scheme.py
"""
import json
import os
import time

import pw_common as C

OUT_DIR = os.path.join(C.BASE, "output")


def save_json(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    fp = os.path.join(OUT_DIR, name)
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print("  [落盘] %s" % fp)


def main():
    C.hr("30 Playwright 方案：真实浏览器环境产出 X-s 签名")
    results = []
    detail = {}

    with C.LocalSite():
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # ---------- 1~2. 启动浏览器 + 打开签名页 ----------
            t0 = time.time()
            browser = C.launch_browser(p)
            ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            # 反自动化修正：headless Edge 的 navigator.webdriver = true，真实用户是 false
            ctx.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: function () { return false; }});")
            page = ctx.new_page()
            page.goto(C.URL_HOME)
            page.wait_for_function("window.__xhsReady === true", timeout=15000)
            cold_ms = (time.time() - t0) * 1000.0

            # ---------- 3. 浏览器环境观察 ----------
            print("\n--- 浏览器环境观察 ---")
            env = page.evaluate("""() => ({
                ua: navigator.userAgent,
                webdriver: navigator.webdriver,
                cookieFields: window.__cookieFields,
                cookieRaw: document.cookie,
                signFn: typeof window._webmsxyw,
            })""")
            print("  navigator.userAgent  = %s" % env["ua"])
            print("  navigator.webdriver  = %s（add_init_script 修正后）" % env["webdriver"])
            print("  document.cookie 字段数 = %s（与补环境 PLACEHOLDER_COOKIE 对齐）" % env["cookieFields"])
            print("  document.cookie 内容  = %s" % env["cookieRaw"])
            print("  typeof window._webmsxyw = %s" % env["signFn"])
            print("  浏览器冷启动（launch -> 页面就绪）墙钟 = %.0f ms" % cold_ms)
            results.append(C.check("页面加载后 window._webmsxyw 可用", env["signFn"] == "function"))
            results.append(C.check("navigator.webdriver 已修正为 false", env["webdriver"] is False))
            results.append(C.check("9 字段假 cookie 全部写入浏览器（逐条写入）", env["cookieFields"] == 9))

            # ---------- 4. 页面内签名 + 结构分析 ----------
            print("\n--- 页面内签名（真实浏览器环境） ---")
            t1 = time.time()
            sig = page.evaluate("(a) => window.xhsSign(a.path, a.body)",
                                {"path": C.API_PATH, "body": C.COURSE_BODY})
            one_ms = (time.time() - t1) * 1000.0
            info = C.decode_xs(sig["X-s"])
            print("  X-s len=%d | 字段=%s | payload=%d 位 | 头32=%s"
                  % (len(sig["X-s"]), ",".join(info["fields"]), info["payload_len"], info["payload_head"]))
            print("  X-t=%s | 单次签名（含 evaluate 往返）墙钟 = %.1f ms" % (sig["X-t"], one_ms))
            results.append(C.check("浏览器签名结构完整（4 字段含 appId，payload 384 位）",
                                   info["fields"] == ["signSvn", "signType", "appId", "payload"]
                                   and info["payload_len"] == 384))

            # ---------- 5. 与补环境方案的对比 ----------
            print("\n--- 与补环境方案（01+02）的对比 ---")
            t2 = time.time()
            env_sig = C.node_sign(C.API_PATH, C.COURSE_BODY)
            env_wall_ms = (time.time() - t2) * 1000.0
            env_info = C.decode_xs(env_sig["X-s"])
            print("  补环境: 字段=%s | payload=%d 位 | 头32=%s | 含进程启动墙钟=%.0f ms"
                  % (",".join(env_info["fields"]), env_info["payload_len"], env_info["payload_head"], env_wall_ms))
            print("  浏览器: 字段=%s | payload=%d 位 | 头32=%s"
                  % (",".join(info["fields"]), info["payload_len"], info["payload_head"]))
            same_head = info["payload_head"] == env_info["payload_head"]
            results.append(C.check("两方案 payload 头 32 位一致（同一输入的输入指纹等价）", same_head))

            # ---------- 6. 端到端请求 ----------
            print("\n--- 端到端：浏览器签名请求 mock 站 ---")
            status, resp = C.post_signed(C.COURSE_BODY, xs=sig["X-s"], xt=sig["X-t"])
            ok_e2e = (status == 200 and resp.get("success") is True)
            results.append(C.check("浏览器签名 -> HTTP 200（服务端三层校验通过）", ok_e2e))
            print("  HTTP %s | total=%s" % (status, (resp.get("data") or {}).get("total")))

            detail = {
                "browser_cold_start_ms": round(cold_ms, 1),
                "browser_env": env,
                "browser_sign": {"xs_len": len(sig["X-s"]), "xt": sig["X-t"], "one_call_wall_ms": round(one_ms, 1)},
                "browser_sign_decode": {"fields": info["fields"], "payload_len": info["payload_len"], "payload_head": info["payload_head"]},
                "env_sign_decode": {"fields": env_info["fields"], "payload_len": env_info["payload_len"], "payload_head": env_info["payload_head"]},
                "same_payload_head": same_head,
                "e2e_status": status,
            }
            browser.close()

    passed = sum(1 for r in results if r)
    print("\n" + "=" * 64)
    print("30 结论: %d PASS / %d FAIL" % (passed, len(results) - passed))
    print("=" * 64)
    save_json("pw_sign_result.json", {"passed": passed, "total": len(results), "detail": detail})
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
