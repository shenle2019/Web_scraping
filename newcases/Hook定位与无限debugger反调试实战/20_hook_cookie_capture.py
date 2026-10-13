# -*- coding: utf-8 -*-
"""
20：Hook Cookie 验证 —— 拦截 document.cookie 写入，定位生成位置
=========================================================
对应课件：05 hook cookie.js（注入版）→ 本脚本驱动浏览器验证其有效性
流程：
  1. 启动本地模拟站（10_local_server.py）
  2. Playwright 启动 Edge，先注入 hook_scripts/hook_cookie.js（文档创建前）
  3. 打开页面，等待商品数据渲染完成
  4. 读取 window.__hookCookie 验证：
     a) 拦截到 access_token 的写入（含完整调用栈）
     b) 调用栈指向 main.js（成功定位"谁写了 cookie"）
     c) 拦截值 == 浏览器实际 cookie（证明原生 setter 透传成功，页面不受影响）
"""
import sys

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from playwright.sync_api import sync_playwright
import pw_common as C

C.hr("20 Hook Cookie 验证：拦截 cookie 写入 + 定位生成位置")

ok = True
with C.LocalSite():
    with sync_playwright() as p:
        browser = C.launch_browser(p)
        context = browser.new_context()
        page = context.new_page()

        C.inject(page, "hook_scripts/hook_cookie.js")   # 页面任何脚本执行前注入
        page.goto(C.URL_HOME, wait_until="domcontentloaded")
        page.wait_for_selector("#goods-list li", timeout=15000)   # 等页面渲染完成
        print("[20] 页面已渲染 ，商品条目: %d" % page.locator("#goods-list li").count())

        records = page.evaluate("window.__hookCookie")
        print("[20] 拦截记录数: %d" % len(records))

        # --- a) 拦截到写入 ---
        ok &= C.check("拦截到 document.cookie 写入", len(records) >= 1)
        first = records[0] if records else {"value": "", "stack": ""}
        print("     拦截到的写入: %s" % first["value"])

        # --- b) 调用栈定位到 main.js ---
        stack_lines = first.get("stack", "").split("\n")
        print("     调用栈（前 4 帧）:")
        for ln in stack_lines[:4]:
            print("       " + ln.strip())
        ok &= C.check("调用栈定位到 server_assets/main.js", "main.js" in first.get("stack", ""))

        # --- c) 拦截值 == 页面真实 cookie（透传成功） ---
        captured_val = ""
        if "access_token=" in first["value"]:
            captured_val = first["value"].split("access_token=", 1)[1].split(";")[0].strip()
        real_cookies = context.cookies()
        real_val = ""
        for ck in real_cookies:
            if ck["name"] == "access_token":
                real_val = ck["value"]
        print("     拦截值 vs 实际 cookie: %s vs %s" % (captured_val, real_val))
        ok &= C.check("拦截值 == 浏览器实际 cookie（原生 setter 透传成功）",
                      bool(captured_val) and captured_val == real_val)

        # --- 附加：证明 cookie 有效（接口因此返回数据） ---
        status_text = page.locator("#status").inner_text()
        print("     页面状态栏: %s" % status_text)
        ok &= C.check("带令牌请求已被服务端接受（数据渲染成功）", "12" in status_text)

        browser.close()

C.hr("20 结论: " + ("全部通过 —— hook cookie 成功定位写入位置且页面功能零影响" if ok else "存在失败项"))
sys.exit(0 if ok else 1)
