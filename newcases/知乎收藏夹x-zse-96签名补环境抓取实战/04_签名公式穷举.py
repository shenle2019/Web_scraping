# -*- coding: utf-8 -*-
"""04 签名公式穷举对照：采集 2+ 个真实样本，本地穷举拼串变体锁定公式

思路：
    - Playwright 匿名打开收藏夹，捕获多个真实 API 请求（URL / x-zse-93 / x-zse-96）
    - 同一会话 d_c0 固定；对每个样本穷举「url 形态 x d_c0 形态」组合
    - 本地补环境 ZP 批量签名，找能让【全部样本】都一致的组合

仅限学习研究，禁止商用。
"""
import hashlib
import json
import subprocess
from urllib.parse import quote

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


# ---------- 1. 采集真实样本 ----------
captured = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='chrome')
    ctx = browser.new_context(user_agent=UA, locale='zh-CN')
    page = ctx.new_page()

    def on_response(resp):
        req = resp.request
        if '/api/v4/collections/' in req.url:
            h = req.headers
            captured.append({
                'url': req.url,
                'x-zse-93': h.get('x-zse-93', ''),
                'x-zse-96': h.get('x-zse-96', ''),
                'status': resp.status,
            })

    page.on('response', on_response)
    page.goto('https://www.zhihu.com/collection/%s' % COLLECTION_ID,
              wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(3000)
    # 滚动触发多页加载，尽量拿到 ≥2 个不同 offset 的 items 请求
    for _ in range(8):
        page.mouse.wheel(0, 8000)
        page.wait_for_timeout(2000)
        if len({c['url'] for c in captured}) >= 3:
            break
    cookies = {c['name']: c['value'] for c in ctx.cookies()}
    d_c0 = cookies.get('d_c0', '')
    browser.close()

print('[1] 捕获请求 %d 个：' % len(captured))
for c in captured:
    print('    [%s] %s' % (c['status'], c['url'][:110]))
    print('          96 =', c['x-zse-96'])
print('[2] d_c0 =', d_c0)

samples = [c for c in captured
           if '/items' in c['url'] and c['x-zse-96'].startswith('2.0_')]
# 去重（同 URL 只留一个）
uniq, seen = [], set()
for c in samples:
    if c['url'] not in seen:
        uniq.append(c)
        seen.add(c['url'])
samples = uniq
print('[3] 有效 items 样本数:', len(samples))
if not samples:
    raise SystemExit('未采集到签名样本')

with open('output/sign_samples.json', 'w', encoding='utf-8') as f:
    json.dump({'d_c0': d_c0, 'samples': samples}, f, ensure_ascii=False, indent=2)
print('    样本已保存 output/sign_samples.json')

# ---------- 2. 穷举拼串变体 ----------
real_signs = [s['x-zse-96'][4:] for s in samples]
x93 = samples[0]['x-zse-93']
d_no_ts = d_c0.split('|')[0]

def build_variants(url):
    """对一个真实 URL 生成所有候选拼串"""
    path_q = url.split('zhihu.com', 1)[1]
    path = path_q.split('?')[0]
    v = {
        'A1 93+path_q+d(raw)': '%s+%s+%s' % (x93, path_q, d_c0),
        'A2 93+path_q+d(no_ts)': '%s+%s+%s' % (x93, path_q, d_no_ts),
        'A3 93+path_q+d(enc)': '%s+%s+%s' % (x93, path_q, quote(d_c0, safe='')),
        'B1 93+full+d(raw)': '%s+%s+%s' % (x93, url, d_c0),
        'B2 93+full+d(no_ts)': '%s+%s+%s' % (x93, url, d_no_ts),
        'C1 93+path+d(raw)': '%s+%s+%s' % (x93, path, d_c0),
        'D1 path_q+d(raw)': '%s+%s' % (path_q, d_c0),
        'E1 93全连path_q+d': '%s%s%s' % (x93, path_q, d_c0),
        'F1 path_q+d+93': '%s+%s+%s' % (path_q, d_c0, x93),
        'G1 93+full+d+p(enc)': '%s+%s+%s' % (x93, url, quote(d_c0, safe='')),
        'H1 full+d(raw)': '%s+%s' % (url, d_c0),
    }
    return v

all_md5 = []
variant_names = None
per_sample_variants = []
for s in samples:
    variants = build_variants(s['url'])
    if variant_names is None:
        variant_names = list(variants.keys())
    per_sample_variants.append(variants)
    for name in variant_names:
        all_md5.append(hashlib.md5(variants[name].encode()).hexdigest())

local_signs = node_sign(all_md5)

# ---------- 3. 比对 ----------
n_var = len(variant_names)
print('\n[4] 逐变体比对（%d 变体 x %d 样本）' % (n_var, len(samples)))
found = []
for vi, name in enumerate(variant_names):
    ok = all(local_signs[si * n_var + vi] == real_signs[si]
             for si in range(len(samples)))
    mark = '★命中' if ok else ''
    print('    %-24s %s' % (name, mark or '不一致'))
    if ok:
        found.append(name)

print('\n[5] 结论: %s' % ('命中变体 -> ' + ', '.join(found) if found
                         else '全部不一致，需继续扩展变体'))
if found:
    print('    命中示例拼串:', per_sample_variants[0][found[0]])
    print('    本地签名:', local_signs[found.index(found[0])])
    print('    真实签名:', real_signs[0])
