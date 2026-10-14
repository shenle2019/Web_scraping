# -*- coding: utf-8 -*-
"""03 Playwright 对比实验：抓取真实页面发出的签名材料，与本地补环境签名对照

目的：分辨 401 的原因（签名算法/拼串不对？还是 d_c0 不真实？）
输出：
    - 浏览器真实请求的 x-zse-93 / x-zse-96 / x-zst-81 / URL / d_c0
    - 本地补环境对同样输入的签名结果
    - 二者逐字符比对结论

仅限学习研究，禁止商用。
"""
import hashlib
import json
import subprocess

from playwright.sync_api import sync_playwright

COLLECTION_ID = '323709385'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')


def node_sign(md5_list):
    """Node 补环境黑箱批量签名"""
    p = subprocess.run(['node', r'js\zhihu_sign.js', json.dumps(md5_list)],
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode != 0:
        print('node 错误输出:', p.stderr[-800:])
        raise SystemExit('签名失败')
    return json.loads(p.stdout.strip().splitlines()[-1])


captured = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='chrome')
    ctx = browser.new_context(user_agent=UA, locale='zh-CN')
    page = ctx.new_page()

    def on_request(req):
        if '/api/v4/' in req.url:
            h = req.headers
            captured.append({
                'url': req.url,
                'x-zse-93': h.get('x-zse-93', ''),
                'x-zse-96': h.get('x-zse-96', ''),
                'x-zst-81': h.get('x-zst-81', '')[:40] + '...',
            })

    page.on('request', on_request)
    page.goto('https://www.zhihu.com/collection/%s' % COLLECTION_ID,
              wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(4000)
    # 滚动触发翻页加载
    for _ in range(5):
        page.mouse.wheel(0, 6000)
        page.wait_for_timeout(2500)
    print('页面标题:', page.title())

    # 浏览器真实 cookie
    cookies = {c['name']: c['value'] for c in ctx.cookies()}
    print('\n[1] 浏览器 cookies:', {k: (v[:40] + '...' if len(v) > 40 else v)
                                    for k, v in cookies.items()})
    d_c0 = cookies.get('d_c0')
    print('    d_c0 =', d_c0)

    print('\n[2] 捕获 API 请求数:', len(captured))
    if not captured:
        page.screenshot(path='output/pw_no_request.png')
        print('    未捕获到 API 请求，已截图 output/pw_no_request.png')

    # 取第一个 items 请求做对照
    items_req = None
    for item in captured:
        if '/items' in item['url']:
            items_req = item
            break
    item_req = items_req or (captured[0] if captured else None)

    if item_req and item_req.get('x-zse-96') and d_c0:
        print('\n[3] 对照实验（拿真实请求反推签名公式）')
        print('    真实 URL :', item_req['url'])
        print('    真实 93  :', item_req['x-zse-93'])
        print('    真实 96  :', item_req['x-zse-96'])
        real_sign = item_req['x-zse-96']
        if real_sign.startswith('2.0_'):
            real_sign = real_sign[4:]

        x93_real = item_req['x-zse-93']
        url_real = item_req['url']
        path_q = url_real.split('zhihu.com', 1)[1]

        candidates = [
            ('A 93+path+query+d_c0', '%s+%s+%s' % (x93_real, path_q, d_c0)),
            ('B 93+fullurl+d_c0', '%s+%s+%s' % (x93_real, url_real, d_c0)),
        ]
        for name, src in candidates:
            md5hex = hashlib.md5(src.encode()).hexdigest()
            sign = node_sign([md5hex])[0]
            flag = '★一致' if sign == real_sign else '✗不一致'
            print('    [%s] %s' % (name, flag))
            print('        拼串:', src)
            print('        本地:', sign)
            print('        真实:', real_sign)
    browser.close()
