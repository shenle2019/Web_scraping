# -*- coding: utf-8 -*-
"""01 探测：d_c0 cookie 的获取方式（响应头 set-cookie / 页面嵌入逻辑）

仅限学习研究，禁止商用。
"""
import re
import requests

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

s = requests.Session()
s.headers.update({'User-Agent': UA})

r = s.get('https://www.zhihu.com/', timeout=30)
print('[1] GET / ->', r.status_code)
print('    set-cookie 响应头:')
for k, v in r.headers.items():
    if k.lower() == 'set-cookie':
        print('     ', v[:160])
print('    session cookies:', s.cookies.get_dict())

# 页面 HTML 里找 d_c0 写入逻辑
hits = [m.start() for m in re.finditer(r'd_c0', r.text)]
print('\n[2] HTML 中 d_c0 出现次数:', len(hits))
for pos in hits[:6]:
    seg = r.text[max(0, pos - 100):pos + 150].replace('\n', ' ')
    print('    ...', seg[:250])

# 探测其它常见入口是否下 d_c0
for path in ('/signin', '/search?q=test', '/question/19581624'):
    r2 = s.get('https://www.zhihu.com' + path, timeout=30)
    sc = [v for k, v in r2.headers.items() if k.lower() == 'set-cookie']
    print('\n[3] GET %s -> %s, set-cookie: %s' % (path, r2.status_code, sc if sc else '无'))
    print('    d_c0 =', s.cookies.get_dict().get('d_c0'))
