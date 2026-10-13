# -*- coding: utf-8 -*-
"""
21：Hook Header 验证 —— 拦截 XHR 请求头（X-Sign 签名头），定位生成位置
=========================================================
对应课件：06 hook header.js（注入版）→ 本脚本驱动浏览器验证其有效性
流程：
  1. 启动本地模拟站；注入 hook_scripts/hook_header.js 后打开页面
  2. 同时用 page.on("request") 监听真实网络请求作为"**对照组**"
  3. 验证：
     a) hook 捕获到 X-Sign 头的设置（含调用栈，指向 main.js 签名生成行）
     b) hook 捕获的值 == 真实请求实际携带的 X-Sign（证明拦截无损）
     c) 签名被服务端接受（数据返回 12 条）
"""
import sys

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from playwright.sync_api import sync_playwright
import pw_common as C

C.hr("21 Hook Header 验证：拦截 X-Sign 签名头 + 定位生成位置")

ok = True
api_requests = []   # 对照组：真实网络请求

with C.LocalSite():
    with sync_playwright() as p:
        browser = C.launch_browser(p)
        context = browser.new_context()
        page = context.new_page()

        def on_request(req):
            if "/api/goods" in req.url:
                api_requests.append(req)

        page.on("request", on_request)
        C.inject(page, "hook_scripts/hook_header.js")
        page.goto(C.URL_HOME, wait_until="domcontentloaded")
        page.wait_for_selector("#goods-list li", timeout=15000)
        print("[21] 页面已渲染，商品条目: %d" % page.locator("#goods-list li").count())

        records = page.evaluate("window.__hookHeader")
        print("[21] hook 拦截记录数: %d" % len(records))

        # --- a) 捕获到 X-Sign ---
        sign_records = [r for r in records if r["name"].lower() == "x-sign"]
        ok &= C.check("hook 捕获到 X-Sign 头设置（共 %d 条）" % len(sign_records), len(sign_records) >= 1)
        first = sign_records[0] if sign_records else {"type": "", "value": "", "stack": ""}
        print("     通路: %s    X-Sign = %s" % (first.get("type"), first.get("value")))
        print("     调用栈（前 4 帧）:")
        for ln in first.get("stack", "").split("\n")[:4]:
            print("       " + ln.strip())
        ok &= C.check("调用栈定位到 server_assets/main.js", "main.js" in first.get("stack", ""))

        # --- b) hook 值 == 真实请求头（对照组） ---
        real_sign = ""
        if api_requests:
            real_sign = api_requests[0].headers.get("x-sign", "")
        print("     hook 值 vs 真实请求头: %s vs %s" % (first.get("value", ""), real_sign))
        ok &= C.check("hook 捕获值 == 实际发出请求的 X-Sign（拦截无损）",
                      bool(first.get("value")) and first.get("value") == real_sign)

        # --- c) 签名被服务端接受 ---
        status_text = page.locator("#status").inner_text()
        print("     页面状态栏: %s" % status_text)
        ok &= C.check("签名通过服务端校验（数据渲染成功）", "12" in status_text)

        browser.close()

C.hr("21 结论: " + ("全部通过 —— hook header 成功捕获签名头并定位生成位置" if ok else "存在失败项"))
sys.exit(0 if ok else 1)
