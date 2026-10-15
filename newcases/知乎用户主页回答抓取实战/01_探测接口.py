# -*- coding: utf-8 -*-
"""01 探测知乎用户主页回答接口（复用收藏夹案例的登录态 + 补环境签名组件）

目标：https://www.zhihu.com/people/bingo-liu-66（丧心病狂刘老湿）
接口：GET /api/v4/members/bingo-liu-66/answers?include=...&offset=0&limit=5&sort_by=created

验证点：
    1. 登录态 + 本地补环境签名下接口是否 200
    2. 返回结构：data 数组 / paging.is_end / totals
    3. 回答是否直接携带全文（content HTML）

仅限学习研究，禁止商用。低频单线程。
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
X_ZST_81 = ('3_2.0aR_sn77yn6O92wOB8hPZnQr0EMYxc4f18wNBUgpTQ6nxERFZKTY0-4Lm-h3_tufIwJS8gcx'
            'TgJS_AuPZNcXCTwxI78YxEM20s4PGDwN8gGcYAupMWufIoLVqr4gxrRPOI0cY7HL8qun9g93m'
            'FukyigcmebS_FwOYPRP0E4rZUrN9DDom3hnynAUMnAVPF_PhaueTFAuqa9F9kcLBEGFYCGeYFw2p'
            '2eS_fcXMoAwOave8FhpCnU2BbUL1_bxBHreTVMo_XJpYQCCO1hVKfXpKgJx1JBVOcw28RgemqULqJ'
            '_xVfBNftcfMpqeL6GHBjqcM_vS_iJoGLUYOuC39ihXKCUUBnqNx6w2CwhpOBhVMJgxMyuY_y9Y0O'
            'g_zCqHmBrHf5rNOkcwyDUOfuhLmMCofrHHMhgeBYCYZ0B3O_BO1gwVm3htKJ9HKbggq-qX_99t9p0'
            'oBcrx9AUosJ8SqhgtKr4omaUef8JLmthxMQANCe8ws')
INCLUDE = ('data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,'
           'annotation_action,annotation_detail,collapse_reason,is_sticky,'
           'collapsed_by,suggest_edit,comment_count,can_comment,content,'
           'editable_content,attachment,voteup_count,reshipment_settings,'
           'comment_permission,created_time,updated_time,review_info,'
           'relevant_info,question,excerpt,is_labeled,paid_info,'
           'paid_info_content,relationship.is_authorized,is_author,voting,'
           'is_thanked,is_nothelp,is_recognized;'
           'data[*].author.badge[?(type=best_answerer)].topics')


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
    cookies = {c['name']: c['value'] for c in state['cookies']}
    d_c0 = cookies.get('d_c0', '')
    print('[1] 登录态载入：cookie %d 个' % len(cookies))

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

    # include 含 [?(...)] 特殊字符，必须 urlencode 后拼路径（签名与实际 URL 严格一致）
    query = urlencode({'include': INCLUDE, 'offset': 0, 'limit': 5,
                       'sort_by': 'created'})
    path_q = '/api/v4/members/%s/answers?%s' % (URL_TOKEN, query)
    headers = {
        'x-zse-93': X93,
        'x-zse-96': make_x_zse_96(path_q, d_c0),
        'x-zst-81': X_ZST_81,
    }
    r = s.get(BASE + path_q, headers=headers, timeout=30)
    print('[2] 请求状态码:', r.status_code)
    if r.status_code != 200:
        print('    响应前 300 字:', r.text[:300])
        raise SystemExit('接口未通过，中止')

    data = r.json()
    pg = data.get('paging', {})
    items = data.get('data', [])
    print('[3] 返回结构检查:')
    print('    totals=%s is_end=%s 本页条数=%d' % (
        pg.get('totals'), pg.get('is_end'), len(items)))
    if items:
        first = items[0]
        q = (first.get('question') or {}).get('title', '(无标题)')
        c = first.get('content') or ''
        print('    首条: 问题=%s' % q[:40])
        print('    首条含全文 HTML: %s（长度 %d）' % ('是' if c else '否', len(c)))
        print('    首条字段: id=%s 赞同=%s 评论=%s 创建=%s' % (
            first.get('id'), first.get('voteup_count'),
            first.get('comment_count'), first.get('created_time')))

    # 探测输出留档
    os.makedirs(os.path.join(BASE_DIR, 'output'), exist_ok=True)
    with open(os.path.join(BASE_DIR, 'output', 'probe_page1.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'status': r.status_code, 'paging': pg, 'first_3': items[:3]},
                  f, ensure_ascii=False, indent=2)
    print('[4] 探测结果已留档 output/probe_page1.json')


if __name__ == '__main__':
    main()
