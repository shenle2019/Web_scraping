# -*- coding: utf-8 -*-
"""案例3 企名片：用本机 Chrome 打开首页，收集全部加载的 JS + 拦截 recommendInfo 接口样本"""
import json
import os
import re

from playwright.sync_api import sync_playwright

SAVE = "分析素材"
os.makedirs(SAVE, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

js_urls = set()
api_samples = []


def on_response(resp):
    url = resp.url
    try:
        if ".js" in url.split("?")[0][-8:] or url.endswith(".js"):
            js_urls.add(url.split("?")[0])
        if "recommendInfo" in url or "qimingpian" in url and "api" in url:
            try:
                body = resp.text()
            except Exception:
                body = "<body读取失败>"
            api_samples.append({
                "url": url,
                "status": resp.status,
                "req_headers": resp.request.headers,
                "req_post_data": resp.request.post_data,
                "resp_body": body[:2000],
            })
    except Exception:
        pass


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    ctx = browser.new_context(user_agent=UA)
    page = ctx.new_page()
    page.on("response", on_response)
    print("打开企名片首页 ...")
    page.goto("https://www.qimingpian.com/", timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    page.mouse.wheel(0, 4000)
    page.wait_for_timeout(4000)
    page.mouse.wheel(0, 4000)
    page.wait_for_timeout(4000)
    title = page.title()
    print("页面标题:", title)
    # 页面全部资源里的 JS（含懒加载）
    scripts = page.evaluate(
        "Array.from(document.querySelectorAll('script[src]')).map(s => s.src)")
    for s in scripts:
        js_urls.add(s.split("?")[0])
    browser.close()

print("\n=== 收集到 JS 数:", len(js_urls), "===")
for u in sorted(js_urls):
    print(" ", u)

print("\n=== API 样本数:", len(api_samples), "===")
with open(os.path.join(SAVE, "qmp_api_samples.json"), "w", encoding="utf-8") as f:
    json.dump(api_samples, f, ensure_ascii=False, indent=1)
for s in api_samples[:5]:
    print(" ", s["status"], s["url"][:120])
    print("   响应前300:", s["resp_body"][:300].replace("\n", " "))

with open(os.path.join(SAVE, "qmp_js_urls.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(js_urls)))
print("\nJS 清单已保存 分析素材/qmp_js_urls.txt")
