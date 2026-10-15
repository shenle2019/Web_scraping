# -*- coding: utf-8 -*-
"""01c 对照实验2：确认 answers 403 是用户级还是接口级限制

F: 从 relations/mutuals（200）拿一个真实用户 token，测其 answers 接口
G: 刘老湿 answers 完全复刻浏览器 URL（新版 include + ws_qiangzhisafe=0）
H: 刘老湿 articles 接口（同类 members 列表接口对照）

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
# 与浏览器捕获一致的新版 include 与参数
BROWSER_QUERY = {
    'include': ('data[*].is_normal,admin_closed_comment,reward_info,'
                'is_collapsed,annotation_action,annotation_detail,'
                'collapse_reason,collapsed_by,suggest_edit,comment_count,'
                'can_comment,content,editable_content,attachment,voteup_count,'
                'reshipment_settings,comment_permission,created_time,'
                'updated_time,review_info,excerpt,paid_info,'
                'reaction_instruction,is_labeled,label_info,'
                'relationship.is_authorized,voting,is_author,is_thanked,'
                'is_nothelp,reaction,vessay_info;'
                'data[*].author.badge[?(type=best_answerer)].topics;'
                'data[*].author.kvip_info;data[*].author.vip_info;'
                'data[*].question.has_publishing_draft,relationship'),
    'offset': 0, 'limit': 5, 'sort_by': 'created', 'ws_qiangzhisafe': 0,
}


def node_sign(md5_list):
    p = subprocess.run(['node', JS_SIGN, json.dumps(md5_list)],
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode != 0:
        raise RuntimeError('签名失败: ' + p.stderr[-400:])
    return json.loads(p.stdout.strip().splitlines()[-1])


def make_x_zse_96(path_q, d_c0):
    md5hex = hashlib.md5(('%s+%s+%s' % (X93, path_q, d_c0)).encode()).hexdigest()
    return '2.0_' + node_sign([md5hex])[0]


def do_req(s, path_q, d_c0):
    headers = {'x-zse-93': X93, 'x-zse-96': make_x_zse_96(path_q, d_c0)}
    r = s.get(BASE + path_q, headers=headers, timeout=30)
    info = ''
    if r.status_code == 200:
        d = r.json()
        items = d.get('data', [])
        info = 'totals=%s 条数=%d' % (d.get('paging', {}).get('totals'),
                                     len(items))
    else:
        try:
            info = r.json().get('error', {}).get('message', r.text[:80])
        except Exception:
            info = r.text[:80]
    return r.status_code, info


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

    # F: 先拿一个 mutual 用户 token
    path_q = ('/api/v4/members/%s/relations/mutuals?include=data%%5B*%%5D'
              '.answer_count%%2Carticles_count%%2Cgender%%2Cfollower_count'
              '%%2Cfollower_count_text%%2Cis_followed%%2Cis_following'
              '&offset=0&limit=10') % URL_TOKEN
    r = s.get(BASE + path_q, headers={'x-zse-93': X93,
                                      'x-zse-96': make_x_zse_96(path_q, d_c0)},
              timeout=30)
    other_token = None
    if r.status_code == 200:
        data = r.json().get('data', [])
        if data:
            other_token = data[0].get('url_token')
    print('[F] mutuals 接口: %d, 对照组用户 token=%s' % (r.status_code, other_token))

    if other_token:
        path_q = '/api/v4/members/%s/answers?%s' % (
            other_token, urlencode({'offset': 0, 'limit': 5,
                                    'sort_by': 'created'}))
        st, info = do_req(s, path_q, d_c0)
        print('    %s 的 answers -> %s | %s' % (other_token, st, info))

    # G: 刘老湿 answers 完全复刻浏览器参数
    path_q = '/api/v4/members/%s/answers?%s' % (URL_TOKEN,
                                                urlencode(BROWSER_QUERY))
    st, info = do_req(s, path_q, d_c0)
    print('[G] 刘老湿 answers(浏览器全参) -> %s | %s' % (st, info))

    # H: 刘老湿 articles 接口
    path_q = '/api/v4/members/%s/articles?%s' % (
        URL_TOKEN, urlencode({'offset': 0, 'limit': 5, 'sort_by': 'created'}))
    st, info = do_req(s, path_q, d_c0)
    print('[H] 刘老湿 articles -> %s | %s' % (st, info))


if __name__ == '__main__':
    main()
