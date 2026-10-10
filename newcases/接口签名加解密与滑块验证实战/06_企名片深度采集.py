# -*- coding: utf-8 -*-
"""案例3 企名片：记录首页全部 XHR + 访问主要页面触发懒加载 chunk"""
import json
import os

from playwright.sync_api import sync_playwright

SAVE = "分析素材"
os.makedirs(SAVE, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

xhr_log = []
js_urls = set()


def on_response(resp):
    try:
        rt = resp.request.resource_type
        if rt in ("xhr", "fetch"):
            body = ""
            try:
                body = resp.text()[:800]
            except Exception:
                pass
            xhr_log.append({"url": resp.url, "status": resp.status, "body": body})
        if rt == "script" or resp.url.split("?")[0].endswith(".js"):
            js_urls.add(resp.url.split("?")[0])
    except Exception:
        pass


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    ctx = browser.new_context(user_agent=UA)
    page = ctx.new_page()
    page.on("response", on_response)

    page.goto("https://www.qimingpian.com/", timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    # 收集页面上所有内部链接
    links = page.evaluate("""
        () => Array.from(document.querySelectorAll('a[href]'))
              .map(a => a.href)
              .filter(u => u.includes('qimingpian.com'))
    """)
    uniq = []
    for u in links:
        if u not in uniq:
            uniq.append(u)
    print("内部链接数:", len(uniq))

    # 依次打开主要页面（最多 6 个不同的）
    visited = {"https://www.qimingpian.com/"}
    count = 0
    for u in uniq:
        if count >= 6:
            break
        if u in visited:
            continue
        visited.add(u)
        count += 1
        try:
            print("访问:", u)
            page.goto(u, timeout=45000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2500)
        except Exception as e:
            print("  访问失败:", type(e).__name__)

    browser.close()

print("\n=== XHR/fetch 请求数:", len(xhr_log), "===")
for x in xhr_log:
    tag = ""
    if "encrypt" in x["body"] or "encrypt" in x["url"]:
        tag = "  <<< 含 encrypt"
    print(" ", x["status"], x["url"][:130], tag)

with open(os.path.join(SAVE, "qmp_xhr_log.json"), "w", encoding="utf-8") as f:
    json.dump(xhr_log, f, ensure_ascii=False, indent=1)

print("\n=== JS 累计:", len(js_urls), "===")
for u in sorted(js_urls):
    if "qimingpian" in u:
        print(" ", u)

with open(os.path.join(SAVE, "qmp_js_urls2.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(js_urls)))
print("已保存 分析素材/qmp_xhr_log.json 与 qmp_js_urls2.txt")
