# -*- coding: utf-8 -*-
"""案例2 招标网（bidcenter.com.cn）搜索页攻坚诊断

已知情况: requests 直连 search.bidcenter.com.cn 会返回阿里云"人机验证"页
         （AliyunCaptcha SceneId=wr4rg7sl，验证通过后 onBizResultCallback 跳转目标URL）
本脚本:
  A. requests 直连确认拦截形态
  B. Playwright + 本机 Chrome 打开搜索页，观察能否自动通过验证并出结果
  C. 现象落盘（HTML + 截图）供分析
"""
import os
import time

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
URL = "https://search.bidcenter.com.cn/search?keywords=%E6%9C%8D%E5%8A%A1"  # keywords=服务
os.makedirs("分析素材", exist_ok=True)

# ============ Phase A: requests 直连 ============
print("=" * 60)
print("A. requests 直连探测")
try:
    r = requests.get(URL, headers={"User-Agent": UA}, timeout=20)
    html = r.text
    print("  状态码:", r.status_code, "| 长度:", len(html))
    print("  标题:", html[html.find("<title>") + 7: html.find("</title>")][:50])
    print("  含'人机验证':", "人机验证" in html)
    print("  含 AliyunCaptcha:", "AliyunCaptcha" in html)
    print("  含结果特征(中标/搜索列表):", ("中标" in html) or ("search-list" in html))
except Exception as e:
    print("  异常:", type(e).__name__, e)

# ============ Phase B: Playwright 真浏览器 ============
print("=" * 60)
print("B. Playwright + 本机 Chrome 打开搜索页（观察 18 秒）")

from playwright.sync_api import sync_playwright  # noqa: E402

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    page.goto(URL, timeout=60000, wait_until="domcontentloaded")

    final_state = None
    for i in range(6):  # 最多观察 18 秒，等自动跳转
        page.wait_for_timeout(3000)
        title = page.title()
        url_now = page.url
        body = page.content()
        has_captcha = ("captcha-element" in body) or ("AliyunCaptcha" in body) or ("人机验证" in title)
        has_result = ("中标" in body) and ("搜索" in body) and ("captcha-element" not in body)
        print("  t+%2ds | 标题: %-22s | 验证码仍在: %s | 疑似结果页: %s"
              % ((i + 1) * 3, title[:22], has_captcha, has_result))
        final_state = (title, url_now, has_captcha, has_result, body)
        if not has_captcha and has_result:
            break

    title, url_now, has_captcha, has_result, body = final_state

    # 证据落盘
    with open("分析素材/bidcenter_pw.html", "w", encoding="utf-8") as f:
        f.write(body)
    try:
        page.screenshot(path="分析素材/bidcenter_pw.png", full_page=False)
        print("  截图: 分析素材/bidcenter_pw.png")
    except Exception as e:
        print("  截图失败:", e)

    # 检查是否出现了验证码 iframe / 滑块
    frames = [f.url for f in page.frames]
    print("  页面 frame 数:", len(frames))
    for fu in frames:
        print("    frame:", fu[:100])

    browser.close()

print("=" * 60)
print("C. 结论")
print("  最终标题:", title)
print("  最终 URL:", url_now)
print("  验证码仍在:", has_captcha)
print("  疑似拿到结果页:", has_result)
print("  HTML 已保存: 分析素材/bidcenter_pw.html (%d 字符)" % len(body))
