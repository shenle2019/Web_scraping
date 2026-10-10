# -*- coding: utf-8 -*-
"""案例2 招标网 第二阶段攻坚：真实窗口 + 尝试拖动滑块过验证

背景: headless 模式停在阿里云滑块验证页（请完成安全验证 - 拖动滑块到最右边），
      但验证页源码含 initAliyunCaptcha_config.test=true（测试模式配置）。
策略:
  C1. requests 探测主站 www.bidcenter.com.cn 是否也拦
  C2. headed Playwright 打开验证页，定位滑块（穿透 shadow DOM），模拟人类轨迹拖动
  C3. 若跳转成功 -> 落盘结果页 HTML/截图 + 导出 cookies，并立即用 requests 复测
"""
import json
import os
import time

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
URL = "https://search.bidcenter.com.cn/search?keywords=%E6%9C%8D%E5%8A%A1"
os.makedirs("分析素材", exist_ok=True)

# ============ C1. 主站探测 ============
print("=" * 60)
print("C1. requests 探测主站 www.bidcenter.com.cn")
try:
    r = requests.get("https://www.bidcenter.com.cn/",
                     headers={"User-Agent": UA}, timeout=20)
    t = r.text
    title = t[t.find("<title>") + 7: t.find("</title>")][:60]
    print("  状态码:", r.status_code, "| 长度:", len(t), "| 标题:", title)
    print("  含'人机验证':", "人机验证" in t)
except Exception as e:
    print("  异常:", type(e).__name__, e)

# ============ C2. headed 拖滑块 ============
print("=" * 60)
print("C2. headed 浏览器打开验证页并尝试拖滑块")

from playwright.sync_api import sync_playwright  # noqa: E402

passed = False
result_html = ""
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    page.goto(URL, timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    print("  当前标题:", page.title(), "| URL:", page.url[:80])

    # 定位滑块（Playwright CSS 选择器可穿透 shadow DOM）
    slider = page.locator("#aliyunCaptcha-sliding-slider")
    try:
        slider.wait_for(state="visible", timeout=10000)
        box = slider.bounding_box()
        print("  找到滑块:", box)
    except Exception as e:
        box = None
        print("  未找到标准滑块选择器:", type(e).__name__)
        # 兜底：枚举 shadow root 内所有 id 含 slide 的元素
        ids = page.evaluate("""() => {
            const found = [];
            const walk = (root) => {
                root.querySelectorAll('*').forEach(el => {
                    if (el.id && /slide|btn|captcha/i.test(el.id)) found.push(el.id);
                    if (el.shadowRoot) walk(el.shadowRoot);
                });
            };
            walk(document);
            return found;
        }""")
        print("  shadow DOM 中含 slide/btn/captcha 的 id:", ids)

    if box:
        # 找轨道宽度：取滑块容器宽度作为拖动距离
        try:
            wrapper = page.locator("#aliyunCaptcha-sliding-wrapper")
            wbox = wrapper.bounding_box()
            track_w = wbox["width"] - box["width"]
            print("  容器:", wbox, "| 拖动距离:", track_w)
        except Exception:
            track_w = 320

        sx = box["x"] + box["width"] / 2
        sy = box["y"] + box["height"] / 2
        page.mouse.move(sx, sy)
        page.mouse.down()
        # 模拟人类轨迹：先慢后快 + 轻微抖动
        import math
        steps = 40
        for i in range(1, steps + 1):
            frac = i / steps
            ease = 1 - math.pow(1 - frac, 3)      # easeOutCubic
            x = sx + track_w * ease + (2 if i % 7 == 0 else 0)
            y = sy + (1 if i % 5 == 0 else 0)
            page.mouse.move(x, y)
            page.wait_for_timeout(12 + (i % 5) * 3)
        page.mouse.up()
        print("  拖动完成，等待验证结果 ...")

    # 轮询等待跳转（最多 30 秒）
    for i in range(10):
        page.wait_for_timeout(3000)
        cur = page.url
        title = page.title()
        print("  t+%2ds | %s | %s" % ((i + 1) * 3, title[:24], cur[:70]))
        if "search.bidcenter.com.cn" in cur and "HumanMachine" not in cur:
            passed = True
            break

    if passed:
        page.wait_for_timeout(3000)
        result_html = page.content()
        with open("分析素材/bidcenter_result.html", "w", encoding="utf-8") as f:
            f.write(result_html)
        page.screenshot(path="分析素材/bidcenter_result.png", full_page=False)
        json.dump(ctx.cookies(), open("分析素材/bidcenter_cookies.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("  [OK] 验证通过！已保存结果页 HTML/截图/cookies")
    else:
        page.screenshot(path="分析素材/bidcenter_fail.png", full_page=False)
        print("  [FAIL] 30 秒内未通过验证")

    browser.close()

# ============ C3. 复测 ============
print("=" * 60)
print("C3. 结论")
if passed:
    cookies = json.load(open("分析素材/bidcenter_cookies.json", encoding="utf-8"))
    ck = {c["name"]: c["value"] for c in cookies}
    r = requests.get(URL, headers={"User-Agent": UA}, cookies=ck, timeout=20)
    print("  requests 复用 cookies 复测: 状态码=%d 长度=%d" % (r.status_code, len(r.text)))
    print("  含'人机验证':", "人机验证" in r.text)
    print("  结果页 HTML 长度:", len(result_html))
else:
    print("  滑块验证未通过——该验证需人工交互或更高级手段，如实记录")
