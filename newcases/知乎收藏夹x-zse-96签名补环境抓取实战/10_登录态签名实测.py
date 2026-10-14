# -*- coding: utf-8 -*-
"""10 登录态签名实测：requests + 本地补环境签名 请求 items API

对照三组实验：
    A. 登录 cookies + 不带任何签名头        → 看登录态是否放宽
    B. 登录 cookies + 本地补环境 x-zse-96   → 验证签名公式
    C. 同会话浏览器真实签名样本             → 穷举拼串变体锁定公式

仅限学习研究，禁止商用。
"""
import hashlib
import json
import subprocess
from urllib.parse import quote, quote_plus

import requests
from playwright.sync_api import sync_playwright

COLLECTION_ID = '323709385'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
STATE_FILE = 'output/zhihu_state.json'
PATH_Q = '/api/v4/collections/%s/items?offset=0&limit=20' % COLLECTION_ID


def node_sign(md5_list):
    p = subprocess.run(['node', r'js\zhihu_sign.js', json.dumps(md5_list)],
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode != 0:
        print('node 错误输出:', p.stderr[-800:])
        raise SystemExit('签名失败')
    return json.loads(p.stdout.strip().splitlines()[-1])


# ---------- 读登录态 cookies ----------
state = json.load(open(STATE_FILE, encoding='utf-8'))
cookies = {c['name']: c['value'] for c in state['cookies']}
d_c0 = cookies.get('d_c0', '')
print('[0] 登录态 cookie 数:', len(cookies), '| d_c0 =', d_c0)
print('    关键 cookie:', {k: (k in cookies) for k in ('z_c0', 'SESSIONID', 'd_c0')})

s = requests.Session()
s.headers.update({'User-Agent': UA, 'Referer': 'https://www.zhihu.com/collection/%s' % COLLECTION_ID})
for c in state['cookies']:
    s.cookies.set(c['name'], c['value'], domain=c.get('domain') or '.zhihu.com',
                  path=c.get('path', '/'))

# ---------- A. 登录态 + 无签名 ----------
rA = s.get('https://www.zhihu.com' + PATH_Q, timeout=30)
print('\n[A] 登录态 + 无签名 ->', rA.status_code)
print('    ', rA.text[:160])

# ---------- C. 采集浏览器登录态真实签名样本 ----------
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='chrome')
    ctx = browser.new_context(storage_state=STATE_FILE, user_agent=UA,
                              locale='zh-CN')
    page = ctx.new_page()
    sig_sample = {}

    def on_request(req):
        if '/api/v4/collections/%s/items' % COLLECTION_ID in req.url and 'offset=0' in req.url:
            h = req.headers
            sig_sample.update({
                'url': req.url,
                'x-zse-93': h.get('x-zse-93', ''),
                'x-zse-96': h.get('x-zse-96', ''),
                'x-zst-81': h.get('x-zst-81', '')[:30],
                'cookie_header': h.get('cookie', '')[:80],
            })

    page.on('request', on_request)
    page.goto('https://www.zhihu.com/collection/%s' % COLLECTION_ID,
              wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(6000)
    browser.close()

print('\n[C] 浏览器登录态真实签名样本:')
print('    url   :', sig_sample.get('url'))
print('    93    :', sig_sample.get('x-zse-93'))
print('    96    :', sig_sample.get('x-zse-96'))

real96 = sig_sample.get('x-zse-96', '')
real93 = sig_sample.get('x-zse-93', '')
url_real = sig_sample.get('url', '')
if real96.startswith('2.0_'):
    real96 = real96[4:]

if real96 and d_c0:
    path_q_real = url_real.split('zhihu.com', 1)[1]
    d_no_ts = d_c0.split('|')[0]
    variants = {
        'A1 93+pathq+d(raw)': '%s+%s+%s' % (real93, path_q_real, d_c0),
        'A2 93+pathq+d(no_ts)': '%s+%s+%s' % (real93, path_q_real, d_no_ts),
        'A3 93+pathq+d(enc)': '%s+%s+%s' % (real93, path_q_real, quote(d_c0, safe='')),
        'A4 93+pathq+d(enc+)': '%s+%s+%s' % (real93, path_q_real, quote_plus(d_c0)),
        'B1 93+full+d(raw)': '%s+%s+%s' % (real93, url_real, d_c0),
        'C1 93+path+d(raw)': '%s+%s+%s' % (real93, path_q_real.split('?')[0], d_c0),
        'E1 直接连接': '%s%s%s' % (real93, path_q_real, d_c0),
    }
    md5s = [hashlib.md5(v.encode()).hexdigest() for v in variants.values()]
    locals_ = node_sign(md5s)
    print('\n[穷举对照] 真实96 =', real96)
    hit = None
    for (name, src), local in zip(variants.items(), locals_):
        mark = '★命中' if local == real96 else '✗'
        print('    %-24s %s' % (name, mark))
        if local == real96:
            hit = (name, src)
    if hit:
        print('\n[结论] 命中变体:', hit[0])
        print('    拼串:', hit[1])
    else:
        print('\n[结论] 仍未命中，需进一步扩展（如 93 非请求头值、额外字段等）')

# ---------- B. requests + 本地签名（用 A1 公式先试） ----------
src_b = '%s+%s+%s' % ('101_3_3.0', PATH_Q, d_c0)
md5b = hashlib.md5(src_b.encode()).hexdigest()
sign_b = node_sign([md5b])[0]
hB = {
    'x-zse-93': '101_3_3.0',
    'x-zse-96': '2.0_' + sign_b,
    'x-requested-with': 'fetch',
}
rB = s.get('https://www.zhihu.com' + PATH_Q, headers=hB, timeout=30)
print('\n[B] 登录态 + 本地签名(A1公式) ->', rB.status_code)
print('    ', rB.text[:160])
