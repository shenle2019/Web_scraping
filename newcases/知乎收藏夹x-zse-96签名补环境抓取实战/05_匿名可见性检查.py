# -*- coding: utf-8 -*-
"""05 匿名可见性检查：截图确认匿名访问收藏夹时页面实际渲染内容

仅限学习研究，禁止商用。
"""
from playwright.sync_api import sync_playwright

COLLECTION_ID = '323709385'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='chrome')
    ctx = browser.new_context(user_agent=UA, locale='zh-CN',
                              viewport={'width': 1280, 'height': 900})
    page = ctx.new_page()
    page.goto('https://www.zhihu.com/collection/%s' % COLLECTION_ID,
              wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(3000)
    page.screenshot(path='output/anon_page.png', full_page=False)

    # 统计页面上的条目与关键提示文案
    print('标题:', page.title())
    body = page.inner_text('body')
    print('body 长度:', len(body))
    for kw in ('登录', '登入', '查看全部', '查看更多', '下载知乎', 'App 内打开'):
        if kw in body:
            print('  发现关键词:', kw)
    # 找条目容器数量线索
    for sel in ('div.List-item', '.List-item', 'section', '.CollectionDetailPage'):
        n = page.query_selector_all(sel)
        if n:
            print('  选择器 %s 命中 %d 个' % (sel, len(n)))
    print('\n--- 页面正文前 600 字 ---')
    print(body[:600])
    browser.close()
