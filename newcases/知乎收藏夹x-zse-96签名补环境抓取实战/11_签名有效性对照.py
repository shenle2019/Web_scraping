# -*- coding: utf-8 -*-
"""11 签名有效性对照：登录态下三种请求方式的服务端反应

    ① 无签名头
    ② 明显错误的签名（2.0_ + 全 A）
    ③ 本地补环境签名（A1 公式）
用于确认：登录态下 x-zse-96 是否被服务端强校验。

仅限学习研究，禁止商用。
"""
import hashlib
import json
import subprocess
import time

import requests

COLLECTION_ID = '323709385'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
STATE_FILE = 'output/zhihu_state.json'
PATH_Q = '/api/v4/collections/%s/items?offset=0&limit=5' % COLLECTION_ID


def node_sign(md5_list):
    p = subprocess.run(['node', r'js\zhihu_sign.js', json.dumps(md5_list)],
                       capture_output=True, text=True, encoding='utf-8')
    return json.loads(p.stdout.strip().splitlines()[-1])


state = json.load(open(STATE_FILE, encoding='utf-8'))
cookies = {c['name']: c['value'] for c in state['cookies']}
d_c0 = cookies.get('d_c0', '')

s = requests.Session()
s.headers.update({'User-Agent': UA,
                  'Referer': 'https://www.zhihu.com/collection/%s' % COLLECTION_ID})
for c in state['cookies']:
    s.cookies.set(c['name'], c['value'],
                  domain=c.get('domain') or '.zhihu.com', path=c.get('path', '/'))

url = 'https://www.zhihu.com' + PATH_Q

# ① 无签名
r1 = s.get(url, timeout=30)
print('[1] 无签名           ->', r1.status_code, r1.text[:80])
time.sleep(1.2)

# ② 错误签名
h2 = {'x-zse-93': '101_3_3.0', 'x-zse-96': '2.0_' + 'A' * 64}
r2 = s.get(url, headers=h2, timeout=30)
print('[2] 错误签名(全A)     ->', r2.status_code, r2.text[:80])
time.sleep(1.2)

# ③ 本地补环境签名
src = '101_3_3.0+%s+%s' % (PATH_Q, d_c0)
md5hex = hashlib.md5(src.encode()).hexdigest()
sign = node_sign([md5hex])[0]
h3 = {'x-zse-93': '101_3_3.0', 'x-zse-96': '2.0_' + sign}
r3 = s.get(url, headers=h3, timeout=30)
print('[3] 本地补环境签名    ->', r3.status_code, r3.text[:80])

print('\n[结论] 登录态下签名校验强度：', end='')
if r2.status_code == 200:
    print('错误签名也放行 → 服务端对登录用户未强校验 x-zse-96')
elif r3.status_code == 200:
    print('错误签名被拒、本地签名放行 → 本地签名真实有效')
else:
    print('需进一步分析')
