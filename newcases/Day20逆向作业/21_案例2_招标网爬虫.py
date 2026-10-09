# -*- coding: utf-8 -*-
"""案例2：招标网（采招网）数据爬虫 —— 【接口直连方案】

=========================================================
反爬链路（三层）与破解方式：
  ① 阿里云滑块人机验证
     -> Playwright 真实浏览器（headed）+ 模拟人类轨迹拖拽过验证，
        导出 cookies 缓存到 分析素材/bidcenter_cookies.json（可复用）
  ② 搜索结果为 JS 异步渲染（requests 只能拿到壳页面，0 条数据）
     -> 放弃解析 DOM，直接抓数据接口
  ③ 数据接口响应加密
     POST https://interface.bidcenter.com.cn/search/GetSearchProHandler.ashx
     响应 = AES-CBC + ZeroPadding 加密的 base64
     -> KEY/IV 从 searchv17.js 的 variate 对象还原
        （words 数组 = CryptoJS WordArray，32bit 大端拼接）
=========================================================
运行方式：python 21_案例2_招标网爬虫.py
（首次运行若无 cookies 或 cookies 失效，会自动弹出 Chrome 窗口
  自动拖滑块过一次验证，无需人工操作）
"""
import base64
import csv
import json
import math
import os
import time
import uuid
from urllib.parse import quote

import requests
from Crypto.Cipher import AES

BASE = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(BASE, "分析素材", "bidcenter_cookies.json")
OUT_DIR = os.path.join(BASE, "作业结果")

# ============ 配置 ============
KEYWORDS = "服务"                 # 搜索关键词
PAGES = 3                         # 抓取页数（每页 40 条）
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
API = "https://interface.bidcenter.com.cn/search/GetSearchProHandler.ashx"
SEARCH_URL = "https://search.bidcenter.com.cn/search?keywords=%s" % quote(KEYWORDS)

# ============ AES 解密（复刻 searchv17.js AESDecrypt） ============
# KEY/IV 来自 searchv17.js 第 107-119 行 variate.key / variate.aceIV 的 words 数组
KEY = b"".join(w.to_bytes(4, "big") for w in
               [863652730, 2036741733, 1164342596, 1782662963])
IV = b"".join(w.to_bytes(4, "big") for w in
              [1719227713, 1314533489, 1397643880, 1749959510])


def aes_decrypt(b64_text):
    """AES-CBC + ZeroPadding 解密接口响应（对应 JS: CryptoJS.AES.decrypt + pad.ZeroPadding）"""
    ct = base64.b64decode(b64_text.strip())
    pt = AES.new(KEY, AES.MODE_CBC, IV).decrypt(ct)
    return pt.rstrip(b"\x00").decode("utf-8")


# ============ cookies 管理：缓存复用 / 滑块刷新 ============
def load_cookies():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, encoding="utf-8") as f:
            return {c["name"]: c["value"] for c in json.load(f)}
    return None


def test_cookies(cookies):
    """用接口发一次真实请求验证 cookies 是否有效"""
    if not cookies:
        return False
    try:
        r = post_api(cookies, page=1)
        data = json.loads(aes_decrypt(r.text))
        return bool(data.get("ret"))
    except Exception:
        return False


def refresh_cookies_by_slider():
    """Playwright headed 打开搜索页，自动拖滑块过阿里云人机验证，导出 cookies"""
    from playwright.sync_api import sync_playwright

    print("  [刷新] 启动 Chrome 过阿里云滑块验证 ...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(SEARCH_URL, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        print("  当前页面:", page.title()[:30], "|", page.url[:70])

        # 若直接进入搜索页（无需验证），快速返回
        if "HumanMachine" not in page.url and "search.bidcenter.com.cn" in page.url:
            json.dump(ctx.cookies(), open(COOKIE_FILE, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            browser.close()
            return True

        # 定位滑块（Playwright 选择器可穿透 shadow DOM）
        slider = page.locator("#aliyunCaptcha-sliding-slider")
        try:
            slider.wait_for(state="visible", timeout=10000)
            box = slider.bounding_box()
        except Exception as e:
            page.screenshot(path=os.path.join(BASE, "分析素材", "bidcenter_fail.png"))
            browser.close()
            raise RuntimeError("未找到滑块元素: %s" % e)

        wrapper = page.locator("#aliyunCaptcha-sliding-wrapper").bounding_box()
        track_w = wrapper["width"] - box["width"]
        print("  找到滑块，拖动距离 %.0f px" % track_w)

        # 模拟人类轨迹：easeOutCubic 缓动 + 轻微抖动（对齐 21b 验证成功的轨迹）
        sx = box["x"] + box["width"] / 2
        sy = box["y"] + box["height"] / 2
        page.mouse.move(sx, sy)
        page.mouse.down()
        steps = 40
        for i in range(1, steps + 1):
            frac = i / steps
            ease = 1 - math.pow(1 - frac, 3)
            x = sx + track_w * ease + (2 if i % 7 == 0 else 0)
            y = sy + (1 if i % 5 == 0 else 0)
            page.mouse.move(x, y)
            page.wait_for_timeout(12 + (i % 5) * 3)
        page.mouse.up()
        print("  拖动完成，等待验证跳转 ...")

        passed = False
        for i in range(10):
            page.wait_for_timeout(3000)
            cur = page.url
            print("  t+%2ds | %s | %s" % ((i + 1) * 3, page.title()[:20], cur[:64]))
            if "search.bidcenter.com.cn" in cur and "HumanMachine" not in cur:
                passed = True
                break

        if passed:
            page.wait_for_timeout(3000)
            json.dump(ctx.cookies(), open(COOKIE_FILE, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print("  [OK] 验证通过，cookies 已保存")
        else:
            page.screenshot(path=os.path.join(BASE, "分析素材", "bidcenter_fail.png"))
        browser.close()
        return passed


# ============ 接口请求 ============
def post_api(cookies, page=1):
    """复刻前端 searchv17.js 的请求构造
    form 参数: from/guid/location/token/deftag/keywords/mod/vtime(+page)
    注意 keywords 前端做了双重编码（urlencode 后的字面值再作为表单值发送）
    """
    form = {
        "from": "6137",
        "guid": str(uuid.uuid4()),
        "location": "6138",
        "token": "",
        "deftag": "1",
        "keywords": quote(KEYWORDS),
        "mod": "0",
        "vtime": str(int(time.time() * 1000)),
    }
    if page > 1:
        form["page"] = str(page)     # searchv17.js 第 2303 行: params.page = jq_searchDataNew.page
    headers = {
        "user-agent": UA,
        "referer": SEARCH_URL,
        "origin": "https://search.bidcenter.com.cn",
        "x-requested-with": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    return requests.post(API, data=form, headers=headers, cookies=cookies, timeout=20)


def fetch_page(session, page):
    """抓取一页并解密，返回 (listData, realInfoCount)"""
    r = post_api(session, page)
    data = json.loads(aes_decrypt(r.text))
    if not data.get("ret"):
        raise RuntimeError("接口返回 ret=false, msg=%s" % data.get("msg"))
    o2 = data.get("other2") or {}
    return o2.get("listData") or [], o2.get("realInfoCount", 0)


# ============ 字段解析 ============
def parse_item(item):
    url = item.get("news_url", "")
    if url.startswith("//"):
        url = "https:" + url
    return {
        "编号": item.get("news_id"),
        "信息类型": item.get("news_type_des"),
        "标题": (item.get("news_title_show") or "").strip(),
        "链接": url,
        "发布时间": item.get("news_star_time_show"),
        "地区": item.get("news_diqustr"),
        "采购方式": item.get("news_cgfs"),
        "预算金额": item.get("news_zbje_show"),
        "中标金额": item.get("news_zhongbiaojine_show"),
        "命中内容": item.get("contain_kwd_fujian"),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=" * 64)
    print("案例2：招标网搜索「%s」 —— 接口直连方案" % KEYWORDS)
    print("=" * 64)

    # 1. cookies：优先缓存，失效则自动过滑块刷新
    cookies = load_cookies()
    if test_cookies(cookies):
        print("[1/3] cookies 缓存有效（来自 分析素材/bidcenter_cookies.json）")
    else:
        print("[1/3] cookies 缺失或已失效，自动刷新 ...")
        if not refresh_cookies_by_slider():
            raise SystemExit("滑块验证未通过，请重试或手动运行 21b_招标网滑块攻坚.py")
        cookies = load_cookies()

    # 2. 逐页抓取
    print("[2/3] 开始抓取 %d 页（每页 40 条）..." % PAGES)
    session = cookies
    all_items = []
    real_count = 0
    for page in range(1, PAGES + 1):
        items, real_count = fetch_page(session, page)
        records = [parse_item(it) for it in items]
        all_items.extend(records)
        first = records[0]["标题"][:28] if records else "(空)"
        print("  第 %d 页: %2d 条 | 首条: %s" % (page, len(records), first))
        time.sleep(1)   # 温和间隔

    # 3. 保存结果
    print("[3/3] 保存结果 ...")
    json_path = os.path.join(OUT_DIR, "案例2_招标网_%s搜索结果.json" % KEYWORDS)
    csv_path = os.path.join(OUT_DIR, "案例2_招标网_%s搜索结果.csv" % KEYWORDS)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"关键词": KEYWORDS, "总条数": real_count,
                   "抓取条数": len(all_items), "数据": all_items},
                  f, ensure_ascii=False, indent=2)
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_items[0].keys()))
        writer.writeheader()
        writer.writerows(all_items)

    print("  JSON -> %s" % json_path)
    print("  CSV  -> %s" % csv_path)
    print("结果: 站方声称共 %s 条，本次抓取 %d 条" % (real_count, len(all_items)))


if __name__ == "__main__":
    main()
