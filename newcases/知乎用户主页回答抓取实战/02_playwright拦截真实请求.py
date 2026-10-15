# -*- coding: utf-8 -*-
"""02 Playwright 拦截浏览器真实请求：看 members/answers 接口的真实 URL 与请求头

思路：复用登录态打开用户主页「回答」页，拦截 XHR，比对真实请求与我方 requests 的差异。

仅限学习研究，禁止商用。
"""
import json
import os

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(BASE_DIR, r'..\知乎收藏夹x-zse-96签名补环境抓取实战')
STATE_FILE = os.path.join(PREV, r'output\zhihu_state.json')
# 系统 Chrome（用户目录安装），避免 playwright install 下载内核
CHROME = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\Application\chrome.exe')

URL_TOKEN = 'bingo-liu-66'
TARGET = 'https://www.zhihu.com/people/%s/answers' % URL_TOKEN


def main():
    hits = []

    def on_response(resp):
        u = resp.url
        if '/members/' in u and ('answer' in u or 'include' in u):
            req = resp.request
            hits.append({
                'url': u,
                'status': resp.status,
                'x-zse-93': req.headers.get('x-zse-93', ''),
                'x-zse-96': (req.headers.get('x-zse-96') or '')[:24],
                'x-zst-81': (req.headers.get('x-zst-81') or '')[:24],
                'x-api-version': req.headers.get('x-api-version', ''),
                'sec-ch-ua': req.headers.get('sec-ch-ua', '')[:60],
            })
            print('[XHR] %s' % resp.status)
            print('  URL:', u[:200])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=CHROME)
        ctx = browser.new_context(storage_state=STATE_FILE,
                                  user_agent=('Mozilla/5.0 (Windows NT 10.0; '
                                              'Win64; x64) AppleWebKit/537.36 '
                                              '(KHTML, like Gecko) '
                                              'Chrome/124.0.0.0 Safari/537.36'))
        page = ctx.new_page()
        page.on('response', on_response)
        page.goto(TARGET, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(6000)
        # 滚动触发懒加载/翻页，等待更多 answers 请求
        for _ in range(3):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(2500)
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(BASE_DIR, 'output',
                                          'member_page.png'), full_page=False)
        browser.close()

    os.makedirs(os.path.join(BASE_DIR, 'output'), exist_ok=True)
    with open(os.path.join(BASE_DIR, 'output', 'real_requests.json'), 'w',
              encoding='utf-8') as f:
        json.dump(hits, f, ensure_ascii=False, indent=2)

    print('\n=== 命中 members 请求 %d 条，详情已存 output/real_requests.json ===' % len(hits))
    for h in hits:
        print(json.dumps(h, ensure_ascii=False)[:300])


if __name__ == '__main__':
    main()
