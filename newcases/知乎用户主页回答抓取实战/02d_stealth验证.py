# -*- coding: utf-8 -*-
"""02d stealth 反检测验证：注入 stealth.min.js 后 answers 接口是否放行

对照变量：navigator.webdriver 等自动化特征。若注入后接口 200，
则说明此前 403 是自动化浏览器指纹触发，可转向页面内驱动抓取。

仅限学习研究，禁止商用。
"""
import os

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(BASE_DIR, r'..\知乎收藏夹x-zse-96签名补环境抓取实战')
STATE_FILE = os.path.join(PREV, r'output\zhihu_state.json')
CHROME = os.path.join(os.environ['LOCALAPPDATA'],
                      r'Google\Chrome\Application\chrome.exe')
STEALTH = r'E:\webspider\Web_scraping\playwright\stealth.min.js'

TARGET = 'https://www.zhihu.com/people/bingo-liu-66/answers'


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=CHROME)
        ctx = browser.new_context(storage_state=STATE_FILE)
        ctx.add_init_script(path=STEALTH)
        page = ctx.new_page()
        answers_status = []

        def on_response(resp):
            if 'members/bingo-liu-66/answers' in resp.url:
                answers_status.append(resp.status)
                print('[answers XHR] status=%s' % resp.status)

        page.on('response', on_response)
        page.goto(TARGET, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(10000)

        webdriver = page.evaluate('navigator.webdriver')
        print('navigator.webdriver =', webdriver)
        text = page.inner_text('body')
        idx = text.find('他的回答')
        seg = text[idx:idx + 200].replace('\n', ' / ') if idx >= 0 else ''
        print('答案区文本:', seg[:200])
        print('answers 请求状态序列:', answers_status)
        browser.close()


if __name__ == '__main__':
    main()
