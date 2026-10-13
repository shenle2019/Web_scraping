# -*- coding: utf-8 -*-
"""
31：离线复刻验证 —— 从 Hook 结果到脱离浏览器的纯算直连
=========================================================
逆向工作流的最终闭环（对应课程"纯算复刻"目标）：
  阶段1（Hook 取证）：
      注入 hook_eval / hook_cookie / hook_header，打开页面，
      拿到 ①混淆段还原的明文密钥 ②页面真实生成的 token ③真实 X-Sign 及 ts
  阶段2（离线复刻）：
      Python 独立实现 secHash（按 hook 还原出的 JS 明文重写），
      用还原出的密钥重算 token 与 sign，与页面真实值逐一比对
  阶段3（直连验证）：
      requests 完全脱离浏览器，用复刻算法自造新签名请求接口：
        - 正确签名 → 200（12 条数据）
        - 错误签名 → 403（对照组，证明服务端确在验签）

合规声明：目标为本地模拟站（自造数据），无任何真实站点请求。
"""
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

import requests
from playwright.sync_api import sync_playwright
import pw_common as C


# ============ 阶段2预备：Python 独立复刻 secHash（按 hook 还原的 JS 明文重写） ============
def sec_hash(s):
    """JS 明文：h1=((h1<<5)+h1+c)>>>0; h2=((h2<<4)+h2+c)>>>0 （djb2 变体双通道）

    (h<<5)+h 等价于 h*33，>>>0 等价于 & 0xFFFFFFFF
    """
    h1, h2 = 5381, 131
    for ch in s:
        c = ord(ch)
        h1 = (h1 * 33 + c) & 0xFFFFFFFF
        h2 = (h2 * 17 + c) & 0xFFFFFFFF
    return "%08x%08x" % (h1, h2)


def main():
    C.hr("31 离线复刻验证：Hook 取证 → Python 纯算复刻 → 直连验证")

    # ================= 阶段1：Hook 取证 =================
    api_urls = []
    with C.LocalSite():
        with sync_playwright() as p:
            browser = C.launch_browser(p)
            context = browser.new_context()
            page = context.new_page()

            page.on("request", lambda r: api_urls.append(r.url) if "/api/goods" in r.url else None)
            C.inject(page,
                     "hook_scripts/hook_cookie.js",
                     "hook_scripts/hook_header.js",
                     "hook_scripts/hook_eval.js")
            page.goto(C.URL_HOME, wait_until="domcontentloaded")
            page.wait_for_selector("#goods-list li", timeout=15000)

            hook_cookie = page.evaluate("window.__hookCookie || []")
            hook_header = page.evaluate("window.__hookHeader || []")
            hook_eval = page.evaluate("window.__hookEval || []")
            browser.close()

    # ① 从 hook_eval 还原的明文中提取密钥（不靠任何硬编码）
    plain = next((r["code"] for r in hook_eval if r["type"] == "eval" and "secHash" in r["code"]), "")
    secret_c = (re.search(r'SECRET_C="([^"]+)"', plain) or [None, ""])[1]
    secret_s = (re.search(r'SECRET_S="([^"]+)"', plain) or [None, ""])[1]
    print("\n[阶段1] Hook 取证结果：")
    print("   还原密钥 SECRET_C = %s" % secret_c)
    print("   还原密钥 SECRET_S = %s" % secret_s)

    # ② 页面真实 token
    token_real = ""
    if hook_cookie:
        m = re.search(r"access_token=([^;]+)", hook_cookie[0]["value"])
        token_real = m.group(1).strip() if m else ""
    # ③ 真实 X-Sign 与 ts
    sign_real = next((r["value"] for r in hook_header if r["name"].lower() == "x-sign"), "")
    ts_real = parse_qs(urlparse(api_urls[0]).query).get("ts", [""])[0] if api_urls else ""
    print("   页面真实 token    = %s" % token_real)
    print("   页面真实 X-Sign   = %s（ts=%s）" % (sign_real, ts_real))

    # ================= 阶段2：离线复刻比对 =================
    day = datetime.utcnow().strftime("%Y-%m-%d")
    token_calc = sec_hash("atk|" + day + "|" + secret_c)
    sign_calc = sec_hash("page=1&ts=" + ts_real + "|" + secret_s)
    print("\n[阶段2] Python 纯算复刻：")
    print("   复刻 token        = %s" % token_calc)
    print("   复刻 X-Sign       = %s" % sign_calc)

    ok = True
    ok &= C.check("复刻 token == 页面真实 token（cookie 算法还原成功）", bool(token_real) and token_calc == token_real)
    ok &= C.check("复刻 X-Sign == 页面真实 X-Sign（签名算法还原成功）", bool(sign_real) and sign_calc == sign_real)

    # ================= 阶段3：脱离浏览器直连 =================
    print("\n[阶段3] requests 直连（完全脱离浏览器，自造新签名）：")
    ts_new = str(int(time.time() * 1000))
    sign_new = sec_hash("page=1&ts=" + ts_new + "|" + secret_s)
    r = requests.get(C.URL_HOME + "api/goods",
                     params={"page": "1", "ts": ts_new},
                     cookies={"access_token": token_calc},
                     headers={"X-Sign": sign_new},
                     timeout=10)
    j = r.json()
    print("   直连请求1（复刻签名）: HTTP %s, total=%s" % (r.status_code, j.get("total")))
    ok &= C.check("复刻算法直连接口成功（200，12 条数据）",
                  r.status_code == 200 and j.get("total") == 12)

    r2 = requests.get(C.URL_HOME + "api/goods",
                      params={"page": "1", "ts": ts_new},
                      cookies={"access_token": token_calc},
                      headers={"X-Sign": "deadbeefdeadbeef"},
                      timeout=10)
    print("   直连请求2（错误签名对照）: HTTP %s, msg=%s" % (r2.status_code, r2.json().get("msg")))
    ok &= C.check("错误签名被服务端拒绝（403，证明验签真实有效）", r2.status_code == 403)

    C.hr("31 结论: " + ("全部通过 —— 从 hook 取证到纯算直连的完整闭环" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
