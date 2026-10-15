# -*- coding: utf-8 -*-
"""02b 检查用户主页回答页的真实渲染状态：页面文本 + SSR 内嵌数据

目的：确认 members/answers 403 是服务端限制，还是页面有替代数据源（如 SSR initialData）。

仅限学习研究，禁止商用。
"""
import json
import os
import re

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(BASE_DIR, r'..\知乎收藏夹x-zse-96签名补环境抓取实战')
STATE_FILE = os.path.join(PREV, r'output\zhihu_state.json')
CHROME = os.path.join(os.environ['LOCALAPPDATA'],
                      r'Google\Chrome\Application\chrome.exe')

URL_TOKEN = 'bingo-liu-66'
TARGET = 'https://www.zhihu.com/people/%s/answers' % URL_TOKEN


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=CHROME)
        ctx = browser.new_context(storage_state=STATE_FILE)
        page = ctx.new_page()
        page.goto(TARGET, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(8000)

        html = page.content()
        text = page.inner_text('body')
        print('=== 页面可见文本前 1200 字 ===')
        print(text[:1200])
        print()
        print('=== 关键信号 ===')
        print('含"登录"提示:', '登录' in text)
        print('含"没有更多"或"暂无":', ('暂无' in text) or ('没有更多' in text))
        print('含回答数文本(个回答):', bool(re.search(r'\d+\s*(个|条)\s*(回答|想法|文章)', text)))

        # SSR 内嵌数据
        m = re.search(r'<script id="js-initialData" type="text/json">(.*?)</script>',
                      html, re.S)
        print('存在 js-initialData:', bool(m))
        if m:
            try:
                init = json.loads(m.group(1))
                keys = list(init.get('initialState', {}).keys())[:30]
                print('initialState keys:', keys)
                entities = init.get('initialState', {}).get('entities', {})
                print('entities keys:', list(entities.keys())[:30])
                users = entities.get('users', {})
                print('users keys:', list(users.keys())[:10])
            except Exception as e:
                print('解析 initialData 失败:', e)
                print(m.group(1)[:300])

        browser.close()


if __name__ == '__main__':
    main()
