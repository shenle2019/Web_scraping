# -*- coding: utf-8 -*-
"""抓取招标网搜索页的 XHR 数据接口：cookies 有效状态下监听所有网络请求"""
import json

from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
URL = "https://search.bidcenter.com.cn/search?keywords=%E6%9C%8D%E5%8A%A1"

cookies = [{"name": c["name"], "value": c["value"], "domain": c["domain"], "path": c["path"]}
           for c in json.load(open("分析素材/bidcenter_cookies.json", encoding="utf-8"))]

xhr_log = []


def on_response(resp):
    req = resp.request
    rtype = req.resource_type
    if rtype in ("xhr", "fetch"):
        item = {
            "method": req.method,
            "url": resp.url,
            "status": resp.status,
            "type": rtype,
            "post_data": req.post_data,
        }
        try:
            ct = resp.headers.get("content-type", "")
            item["content_type"] = ct
            if "json" in ct or "text" in ct:
                body = resp.text()
                item["body_head"] = body[:1500]
                item["body_len"] = len(body)
                item["has_news"] = ("news-" in body) or ("ssjg-list" in body)
        except Exception as e:
            item["body_error"] = str(e)[:100]
        xhr_log.append(item)


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
    ctx.add_cookies(cookies)
    page = ctx.new_page()
    page.on("response", on_response)

    print("打开搜索页 ...")
    page.goto(URL, timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    title = page.title()
    print("标题:", title)

    # 触发加载：滚到底 + 等待
    page.mouse.wheel(0, 4000)
    page.wait_for_timeout(4000)
    page.mouse.wheel(0, 4000)
    page.wait_for_timeout(3000)

    # 当前 DOM 里有多少条结果
    n_cells = page.locator("div.ssjg-list_cell").count()
    n_news = page.locator("a[href*='news-']").count()
    print("DOM 中 ssjg-list_cell 数:", n_cells, "| news- 链接数:", n_news)

    browser.close()

print("\n=== XHR/fetch 请求共 %d 个 ===" % len(xhr_log))
for i, item in enumerate(xhr_log):
    print("\n[%d] %s %s -> %s (%s)" % (i, item["method"], item["status"],
                                        item["url"][:130], item.get("content_type", "")[:40]))
    if item.get("body_len"):
        print("    body长度=%d has_news=%s" % (item["body_len"], item.get("has_news")))

json.dump(xhr_log, open("分析素材/bidcenter_xhr.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n已保存 分析素材/bidcenter_xhr.json")
