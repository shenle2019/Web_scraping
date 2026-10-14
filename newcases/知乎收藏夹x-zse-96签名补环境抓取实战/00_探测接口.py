# -*- coding: utf-8 -*-
"""00 探测：收藏夹接口结构、cookie 获取、签名必要性确认

仅限学习研究，禁止商用。
"""
import requests

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
COLLECTION_ID = '323709385'

s = requests.Session()
s.headers.update({'User-Agent': UA})

# 1. 访问首页拿 cookie（重点是 d_c0，参与 x-zse-96 签名拼串）
r0 = s.get('https://www.zhihu.com/', timeout=30)
print('[1] 访问首页:', r0.status_code)
cookies = s.cookies.get_dict()
print('    cookie keys:', list(cookies.keys()))
print('    d_c0 =', cookies.get('d_c0'))

# 2. 无签名请求收藏夹 items 接口
url = ('https://www.zhihu.com/api/v4/collections/%s/items'
       '?offset=0&limit=20') % COLLECTION_ID
headers1 = {'Referer': 'https://www.zhihu.com/collection/%s' % COLLECTION_ID}
r1 = s.get(url, headers=headers1, timeout=30)
print('\n[2] 无签名 items API:', r1.status_code)
print('    resp:', r1.text[:400])

# 3. 收藏夹基本信息（同样无签名）
r2 = s.get('https://www.zhihu.com/api/v4/collections/%s' % COLLECTION_ID,
           headers=headers1, timeout=30)
print('\n[3] 无签名收藏夹信息:', r2.status_code)
print('    resp:', r2.text[:400])

# 4. 页面本身（HTML）是否可以匿名访问
r3 = s.get('https://www.zhihu.com/collection/%s' % COLLECTION_ID,
           timeout=30)
print('\n[4] 收藏夹页面:', r3.status_code, '长度', len(r3.text))
for key in ('10万', '十万'):
    if key in r3.text:
        idx = r3.text.find(key)
        print('    页面标题片段附近:', r3.text[max(0, idx-60):idx+30].replace('\n', ' '))
        break
