# -*- coding: utf-8 -*-
"""09 Playwright 登录态采集：滚动加载收藏夹全部条目，拦截 items API 响应

原理：浏览器已登录（zhihu_state.json），页面自己会发带正确签名的
     /api/v4/collections/323709385/items 请求；本脚本只做"监听器"，
     把每页响应原样收下——不需要自己计算签名（保底数据通道）。

仅限学习研究，禁止商用。
"""
import json
import time
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

COLLECTION_ID = '323709385'
COLLECTION_URL = 'https://www.zhihu.com/collection/%s' % COLLECTION_ID
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
STATE_FILE = 'output/zhihu_state.json'

pages = {}       # offset -> 响应 JSON
is_end = False


def on_response(resp):
    global is_end
    url = resp.url
    if ('/api/v4/collections/%s/items' % COLLECTION_ID) not in url:
        return
    if resp.status != 200:
        print('  [异常状态]', resp.status, url[:120])
        return
    try:
        data = resp.json()
    except Exception as e:
        print('  [解析失败]', e)
        return
    q = parse_qs(urlparse(url).query)
    offset = int(q.get('offset', ['0'])[0])
    pages[offset] = data
    pg = data.get('paging', {})
    print('  捕获 offset=%-4s 本页=%s 累计总数=%s is_end=%s 请求URL=%s' % (
        offset, len(data.get('data', [])), pg.get('totals'),
        pg.get('is_end'), url[:150]))
    if pg.get('is_end'):
        is_end = True


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='chrome')
    ctx = browser.new_context(storage_state=STATE_FILE, user_agent=UA,
                              locale='zh-CN', viewport={'width': 1280, 'height': 900})
    page = ctx.new_page()
    page.on('response', on_response)

    print('[1] 打开收藏夹页面（标题）:', end=' ', flush=True)
    page.goto(COLLECTION_URL, wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(4000)
    print(page.title(), flush=True)

    # 滚动触发无限加载，直到 is_end 或达到最大轮次
    print('[2] 开始滚动加载……')
    for i in range(80):
        if is_end:
            break
        page.mouse.wheel(0, 12000)
        page.wait_for_timeout(1600)
        if i % 10 == 9:
            print('    已滚动 %d 轮，当前页数 %d' % (i + 1, len(pages)), flush=True)

    page.wait_for_timeout(3000)
    # 页面级证据：渲染的条目数
    dom_items = page.query_selector_all('div.List-item')
    print('[3] 页面 DOM 条目数:', len(dom_items), '（仅供对照）')

    # 截图留档
    page.screenshot(path='output/collection_loaded.png')
    browser.close()

# 汇总保存
all_items = []
for off in sorted(pages):
    all_items.extend(pages[off].get('data', []))

totals = None
for off in pages:
    totals = pages[off].get('paging', {}).get('totals', totals)
    break

print('\n[4] 采集完成：收到 %d 页，累计条目 %d 条，服务端总数 %s' % (
    len(pages), len(all_items), totals))

with open('output/collection_raw_pages.json', 'w', encoding='utf-8') as f:
    json.dump({'collection_id': COLLECTION_ID, 'pages': pages}, f,
              ensure_ascii=False)

# 抽样查看一条结构
if all_items:
    sample = all_items[0]
    print('\n[5] 首条结构键位:', list(sample.keys()))
    content = sample.get('content', {})
    print('    content 键位:', list(content.keys())[:20])
    print('    content.type =', content.get('type'),
          '| content.id =', content.get('id'))
    print('    是否含全文 content 字段:',
          'content' in content and isinstance(content.get('content'), str))
    raw = json.dumps(sample, ensure_ascii=False)
    print('    首条 JSON 大小:', len(raw), '字符')
