# -*- coding: utf-8 -*-
"""建设库：Playwright 抓真实 API 请求（sign/timestamp/cookie/body），离线比对签名算法"""
import json

from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

captured = []


def on_request(req):
    if "capi.jiansheku.com" in req.url and "enterprice/page" in req.url:
        captured.append({
            "url": req.url,
            "headers": dict(req.headers),
            "post_data": req.post_data,
        })


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    ctx = browser.new_context(user_agent=UA)
    page = ctx.new_page()
    page.on("request", on_request)
    print("打开建设库搜索页 ...")
    try:
        page.goto("https://www.jiansheku.com/search/enterprise/",
                  timeout=60000, wait_until="domcontentloaded")
    except Exception as e:
        print("打开异常:", type(e).__name__)
    page.wait_for_timeout(8000)
    # 尝试翻页触发 API
    try:
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(3000)
    except Exception:
        pass
    title = page.title()
    print("页面标题:", title)
    browser.close()

print("\n捕获请求数:", len(captured))
if captured:
    c = captured[0]
    print("\n=== 捕获到的请求头（关键项）===")
    for k in ("sign", "timestamp", "page", "devicetype", "cookie", "origin", "referer"):
        v = c["headers"].get(k, "<无>")
        print("  %s: %s" % (k, v if len(str(v)) < 200 else str(v)[:200] + "..."))
    print("\n=== POST body (前 800 字符) ===")
    print((c["post_data"] or "")[:800])
    # 全部请求头落盘
    with open("分析素材/jsk_live_request.json", "w", encoding="utf-8") as f:
        json.dump(captured, f, ensure_ascii=False, indent=1)
    print("\n已保存 分析素材/jsk_live_request.json（%d 个请求）" % len(captured))
    print("下一步: 运行 17_离线比对sign.py 验证算法")
else:
    print("未捕获到 API 请求——页面可能未触发真实搜索，或被 WAF 拦截")
