# -*- coding: utf-8 -*-
"""01b 对照实验：定位 members/answers 接口 403(10003) 的触发参数

A: 仅 offset/limit（无 include 无 sort_by）
B: offset/limit + sort_by=created
C: offset/limit + 完整 include（无 sort_by）
D: offset/limit + 精简 include（少量字段）

仅限学习研究，禁止商用。
"""
import hashlib
import json
import os
import subprocess
from urllib.parse import urlencode

import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(BASE_DIR, r'..\知乎收藏夹x-zse-96签名补环境抓取实战')
JS_SIGN = os.path.join(PREV, r'js\zhihu_sign.js')
STATE_FILE = os.path.join(PREV, r'output\zhihu_state.json')

BASE = 'https://www.zhihu.com'
URL_TOKEN = 'bingo-liu-66'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
X93 = '101_3_3.0'
INCLUDE_FULL = ('data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,'
                'annotation_action,annotation_detail,collapse_reason,is_sticky,'
                'collapsed_by,suggest_edit,comment_count,can_comment,content,'
                'editable_content,attachment,voteup_count,reshipment_settings,'
                'comment_permission,created_time,updated_time,review_info,'
                'relevant_info,question,excerpt,is_labeled,paid_info,'
                'paid_info_content,relationship.is_authorized,is_author,voting,'
                'is_thanked,is_nothelp,is_recognized;'
                'data[*].author.badge[?(type=best_answerer)].topics')
INCLUDE_MIN = ('data[*].content,voteup_count,comment_count,created_time,'
               'question,excerpt')


def node_sign(md5_list):
    p = subprocess.run(['node', JS_SIGN, json.dumps(md5_list)],
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode != 0:
        raise RuntimeError('签名失败: ' + p.stderr[-400:])
    return json.loads(p.stdout.strip().splitlines()[-1])


def make_x_zse_96(path_q, d_c0):
    md5hex = hashlib.md5(('%s+%s+%s' % (X93, path_q, d_c0)).encode()).hexdigest()
    return '2.0_' + node_sign([md5hex])[0]


def main():
    state = json.load(open(STATE_FILE, encoding='utf-8'))
    d_c0 = ''
    for c in state['cookies']:
        if c['name'] == 'd_c0':
            d_c0 = c['value']

    s = requests.Session()
    s.headers.update({
        'User-Agent': UA,
        'Referer': '%s/people/%s/answers' % (BASE, URL_TOKEN),
        'x-requested-with': 'fetch',
    })
    for c in state['cookies']:
        s.cookies.set(c['name'], c['value'],
                      domain=c.get('domain') or '.zhihu.com',
                      path=c.get('path', '/'))

    groups = [
        ('A 无include无sort', {'offset': 0, 'limit': 3}),
        ('B 带sort_by', {'offset': 0, 'limit': 3, 'sort_by': 'created'}),
        ('C 完整include', {'include': INCLUDE_FULL, 'offset': 0, 'limit': 3}),
        ('D 精简include', {'include': INCLUDE_MIN, 'offset': 0, 'limit': 3}),
    ]
    for name, params in groups:
        query = urlencode(params)
        path_q = '/api/v4/members/%s/answers?%s' % (URL_TOKEN, query)
        headers = {'x-zse-93': X93,
                   'x-zse-96': make_x_zse_96(path_q, d_c0)}
        r = s.get(BASE + path_q, headers=headers, timeout=30)
        info = ''
        if r.status_code == 200:
            d = r.json()
            items = d.get('data', [])
            first_q = (items[0].get('question') or {}).get('title', '') if items else ''
            has_c = bool(items and items[0].get('content'))
            info = 'totals=%s 条数=%d 首条问题=%s 含全文=%s' % (
                d.get('paging', {}).get('totals'), len(items),
                first_q[:24], has_c)
        else:
            try:
                info = r.json().get('error', {}).get('message', r.text[:80])
            except Exception:
                info = r.text[:80]
        print('%-18s -> %s | %s' % (name, r.status_code, info))

    # E 组：收藏夹 items 接口（此前验证过的链路），确认登录态与签名本身是否仍有效
    path_q = '/api/v4/collections/323709385/items?offset=0&limit=3'
    headers = {'x-zse-93': X93,
               'x-zse-96': make_x_zse_96(path_q, d_c0)}
    r = s.get(BASE + path_q, headers=headers, timeout=30)
    info = ''
    if r.status_code == 200:
        d = r.json()
        info = 'totals=%s 条数=%d' % (d.get('paging', {}).get('totals'),
                                     len(d.get('data', [])))
    else:
        try:
            info = r.json().get('error', {}).get('message', r.text[:80])
        except Exception:
            info = r.text[:80]
    print('%-18s -> %s | %s' % ('E 收藏夹items对照', r.status_code, info))


if __name__ == '__main__':
    main()
