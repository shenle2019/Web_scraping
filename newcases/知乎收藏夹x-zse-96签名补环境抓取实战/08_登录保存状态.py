# -*- coding: utf-8 -*-
"""08 登录并保存知乎登录态（一次性操作）

背景：知乎对该收藏夹强制登录可见（匿名 401 + 页面"请登录后查看"）。
方案：启动有头浏览器 → 人工扫码/验证码登录一次 → 登录态保存
      output/zhihu_state.json（已在 .gitignore 排除，凭证不入库）。

仅限学习研究，禁止商用。
"""
import time

from playwright.sync_api import sync_playwright

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
STATE_FILE = 'output/zhihu_state.json'
LOGIN_URL = 'https://www.zhihu.com/signin?next=%2Fcollection%2F323709385'

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False, channel='chrome',
        args=['--disable-blink-features=AutomationControlled'])
    ctx = browser.new_context(user_agent=UA, viewport={'width': 1280, 'height': 860},
                              locale='zh-CN')
    page = ctx.new_page()
    page.goto(LOGIN_URL, timeout=90000)
    print('=' * 56, flush=True)
    print('浏览器已打开登录页：请用知乎 App 扫码，或使用验证码登录', flush=True)
    print('登录成功后将自动保存登录态并关闭窗口（最多等 10 分钟）', flush=True)
    print('=' * 56, flush=True)

    deadline = time.time() + 600
    ok = False
    while time.time() < deadline:
        try:
            cookies = {c['name']: c['value'] for c in ctx.cookies()}
        except Exception:
            break
        if cookies.get('z_c0'):
            ok = True
            break
        try:
            page.wait_for_timeout(3000)
        except Exception:
            break  # 窗口被关闭

    if ok:
        page.wait_for_timeout(2000)
        ctx.storage_state(path=STATE_FILE)
        print('LOGIN_OK 登录态已保存到', STATE_FILE, flush=True)
        try:
            page.goto('https://www.zhihu.com/collection/323709385', timeout=60000)
            page.wait_for_timeout(4000)
            page.screenshot(path='output/logged_in.png')
            print('已截图 output/logged_in.png', flush=True)
        except Exception as e:
            print('截图失败:', e, flush=True)
    else:
        print('LOGIN_TIMEOUT 未检测到登录（或窗口被关闭）', flush=True)
    try:
        browser.close()
    except Exception:
        pass
