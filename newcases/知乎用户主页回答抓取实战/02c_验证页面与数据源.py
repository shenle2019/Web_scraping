# -*- coding: utf-8 -*-
"""02c 验证：另一个用户的 answers 页面是否也"系统繁忙" + 拦截全部 API 请求找数据源

仅限学习研究，禁止商用。
"""
import json
import os

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(BASE_DIR, r'..\知乎收藏夹x-zse-96签名补环境抓取实战')
STATE_FILE = os.path.join(PREV, r'output\zhihu_state.json')
CHROME = os.path.join(os.environ['LOCALAPPDATA'],
                      r'Google\Chrome\Application\chrome.exe')


def check_user(page, token):
    """打开某用户 answers 页，打印答案区文本与全部 API 请求"""
    print('\n========== 用户 %s ==========' % token)
    apis = []

    def on_response(resp):
        u = resp.url
        if '/api/' in u:
            apis.append((resp.status, u[:160]))
            print('  [API %s] %s' % (resp.status, u[:150]))

    page.on('response', on_response)
    page.goto('https://www.zhihu.com/people/%s/answers' % token,
              wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(8000)
    text = page.inner_text('body')
    # 找"他的回答"附近的文本
    idx = text.find('他的回答')
    print('  答案区文本:', text[idx:idx + 120].replace('\n', ' / ') if idx >= 0
          else '(未找到"他的回答"区域)')
    page.off('response', on_response)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=CHROME)
        ctx = browser.new_context(storage_state=STATE_FILE)
        page = ctx.new_page()
        check_user(page, 'zhouyuan')     # 对照组用户
        check_user(page, 'bingo-liu-66')  # 刘老湿
        browser.close()


if __name__ == '__main__':
    main()
