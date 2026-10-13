# -*- coding: utf-8 -*-
"""
22：Hook Eval 验证 —— 混淆代码运行时还原（eval + Function + atob 三入口）
=========================================================
对应课件：01/02 eval 案例的实战化。模拟站把 secHash 函数与两个密钥
base64 后经 eval 还原，静态源码里搜不到任何明文；本脚本验证 hook 后
"隐形代码"当场现形。
流程：
  1. 注入 hook_scripts/hook_eval.js 后打开页面
  2. 验证三件事：
     a) eval 入参 == 混淆段明文（含 secHash 定义与 SECRET_C/SECRET_S 密钥）
     b) atob 解码结果 == 同一份明文
     c) Function 构造器捕获到反调试构造 Function("debugger")
  3. 从还原出的明文里正则提取密钥，与已知密钥比对
"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from playwright.sync_api import sync_playwright
import pw_common as C

C.hr("22 Hook Eval 验证：混淆代码运行时还原")

ok = True
with C.LocalSite():
    with sync_playwright() as p:
        browser = C.launch_browser(p)
        context = browser.new_context()
        page = context.new_page()

        C.inject(page, "hook_scripts/hook_eval.js")
        page.goto(C.URL_HOME, wait_until="domcontentloaded")
        page.wait_for_selector("#goods-list li", timeout=15000)
        print("[22] 页面已渲染，商品条目: %d" % page.locator("#goods-list li").count())

        records = page.evaluate("window.__hookEval")
        by_type = {}
        for r in records:
            by_type.setdefault(r["type"], []).append(r)
        print("[22] 拦截记录: eval=%d, atob=%d, Function=%d" % (
            len(by_type.get("eval", [])), len(by_type.get("atob", [])), len(by_type.get("Function", []))))

        # --- a) eval 入参还原出明文 ---
        eval_codes = [r["code"] for r in by_type.get("eval", [])]
        plain = next((c for c in eval_codes if "secHash" in c), "")
        ok &= C.check("eval 入参已还原出源码明文（含 secHash 定义）", "function secHash" in plain)
        print("     还原出的 eval 明文（前 160 字）:")
        print("       " + plain[:160] + "...")

        # --- b) atob 解码结果 == 同一份明文 ---
        atob_codes = [r["code"] for r in by_type.get("atob", [])]
        atob_plain = next((c for c in atob_codes if "secHash" in c), "")
        ok &= C.check("atob 解码结果即同一份明文（eval(atob(...)) 链路完整现形）",
                      bool(atob_plain) and atob_plain[:100] == plain[:100])

        # --- c) Function 构造器捕获反调试构造 ---
        func_codes = [r["code"] for r in by_type.get("Function", [])]
        ok &= C.check("捕获到反调试构造 Function('debugger')", "debugger" in func_codes)

        # --- d) 从明文提密钥（正则） ---
        m_c = re.search(r'SECRET_C="([^"]+)"', plain)
        m_s = re.search(r'SECRET_S="([^"]+)"', plain)
        got_c = m_c.group(1) if m_c else ""
        got_s = m_s.group(1) if m_s else ""
        print("     提取密钥: SECRET_C=%s  SECRET_S=%s" % (got_c, got_s))
        ok &= C.check("密钥提取成功且与站内已知值一致",
                      got_c == "hk-demo-cookie-salt-2026" and got_s == "hk-demo-sign-salt-2026")

        browser.close()

C.hr("22 结论: " + ("全部通过 —— 静态全 base64 的混淆段被完整还原为明文" if ok else "存在失败项"))
sys.exit(0 if ok else 1)
