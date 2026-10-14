# -*- coding: utf-8 -*-
"""12 正式爬虫：知乎收藏夹「10万赞以上的回答」全量抓取

链路设计（JS 逆向路线）：
    JS 逆向补环境三件套（env/mod/loader）→ 黑箱函数 ZP
    → x-zse-96 = "2.0_" + ZP(md5(x-zse-93 + "+" + 请求路径+查询 + "+" + d_c0))
    → requests 携带登录态 cookies + 签名头，逐页抓取 items API

输出：
    output/collection_raw_pages.json   每页原始响应（留档）
    output/collection_all_items.json   合并去重后的全部条目（供解析）

合规：低频抓取（间隔 1.2s，共 14 页），仅限学习研究，禁止商用。
"""
import hashlib
import json
import subprocess
import time

import requests

COLLECTION_ID = '323709385'
BASE = 'https://www.zhihu.com'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
X93 = '101_3_3.0'          # 客户端版本标识（与真实请求头一致）
X_ZST_81 = ('3_2.0aR_sn77yn6O92wOB8hPZnQr0EMYxc4f18wNBUgpTQ6nxERFZKTY0-4Lm-h3_tufIwJS8gcx'
            'TgJS_AuPZNcXCTwxI78YxEM20s4PGDwN8gGcYAupMWufIoLVqr4gxrRPOI0cY7HL8qun9g93m'
            'FukyigcmebS_FwOYPRP0E4rZUrN9DDom3hnynAUMnAVPF_PhaueTFAuqa9F9kcLBEGFYCGeYFw2p'
            '2eS_fcXMoAwOave8FhpCnU2BbUL1_bxBHreTVMo_XJpYQCCO1hVKfXpKgJx1JBVOcw28RgemqULqJ'
            '_xVfBNftcfMpqeL6GHBjqcM_vS_iJoGLUYOuC39ihXKCUUBnqNx6w2CwhpOBhVMJgxMyuY_y9Y0O'
            'g_zCqHmBrHf5rNOkcwyDUOfuhLmMCofrHHMhgeBYCYZ0B3O_BO1gwVm3htKJ9HKbggq-qX_99t9p0'
            'oBcrx9AUosJ8SqhgtKr4omaUef8JLmthxMQANCe8ws')
STATE_FILE = 'output/zhihu_state.json'
LIMIT = 20
INTERVAL = 1.2             # 低频抓取间隔（秒）


def node_sign(md5_list):
    """调用 Node 补环境脚本批量签名（黑箱，不纯算）"""
    p = subprocess.run(['node', r'js\zhihu_sign.js', json.dumps(md5_list)],
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode != 0:
        raise RuntimeError('签名失败: ' + p.stderr[-400:])
    return json.loads(p.stdout.strip().splitlines()[-1])


def make_x_zse_96(path_q, d_c0):
    """本地补环境生成 x-zse-96（拼串+md5 在调用方，ZP 黑箱出主体）"""
    md5hex = hashlib.md5(('%s+%s+%s' % (X93, path_q, d_c0)).encode()).hexdigest()
    return '2.0_' + node_sign([md5hex])[0]


def main():
    # 1. 装载登录态
    state = json.load(open(STATE_FILE, encoding='utf-8'))
    cookies = {c['name']: c['value'] for c in state['cookies']}
    d_c0 = cookies.get('d_c0', '')
    print('[1] 登录态载入：cookie %d 个, d_c0=%s' % (len(cookies), d_c0[:20] + '...'))

    s = requests.Session()
    s.headers.update({
        'User-Agent': UA,
        'Referer': BASE + '/collection/%s' % COLLECTION_ID,
        'x-requested-with': 'fetch',
    })
    for c in state['cookies']:
        s.cookies.set(c['name'], c['value'],
                      domain=c.get('domain') or '.zhihu.com',
                      path=c.get('path', '/'))

    # 2. 逐页抓取
    pages = {}
    offset = 0
    totals = None
    while True:
        path_q = '/api/v4/collections/%s/items?offset=%d&limit=%d' % (
            COLLECTION_ID, offset, LIMIT)
        headers = {
            'x-zse-93': X93,
            'x-zse-96': make_x_zse_96(path_q, d_c0),   # ← JS 逆向补环境签名
            'x-zst-81': X_ZST_81,
        }
        data = None
        for attempt in range(3):
            try:
                r = s.get(BASE + path_q, headers=headers, timeout=30)
                if r.status_code == 200:
                    data = r.json()
                    break
                print('    请求异常 status=%s，第 %d 次重试' % (
                    r.status_code, attempt + 1))
            except requests.RequestException as e:
                print('    网络异常 %s，第 %d 次重试' % (e, attempt + 1))
            time.sleep(2.5)
        if data is None:
            raise SystemExit('第 %d 页重试耗尽，中止' % (offset // LIMIT + 1))

        pg = data.get('paging', {})
        totals = pg.get('totals', totals)
        items = data.get('data', [])
        pages[offset] = data
        print('[页 %2d] offset=%-4d 本页=%-3d 服务端总数=%s is_end=%s' % (
            offset // LIMIT + 1, offset, len(items), totals, pg.get('is_end')))

        if pg.get('is_end') or not items:
            break
        offset += LIMIT
        time.sleep(INTERVAL)

    # 3. 合并去重
    seen, all_items = set(), []
    for off in sorted(pages):
        for item in pages[off].get('data', []):
            key = item.get('content', {}).get('id') or json.dumps(item)[:64]
            if key in seen:
                continue
            seen.add(key)
            all_items.append(item)

    with open('output/collection_raw_pages.json', 'w', encoding='utf-8') as f:
        json.dump({'collection_id': COLLECTION_ID, 'pages': pages}, f,
                  ensure_ascii=False)
    with open('output/collection_all_items.json', 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False)

    # 4. 统计
    types = {}
    for it in all_items:
        t = it.get('content', {}).get('type', 'unknown')
        types[t] = types.get(t, 0) + 1
    print('\n[2] 抓取完成：%d 页，去重后 %d 条（服务端总数 %s）' % (
        len(pages), len(all_items), totals))
    print('    类型分布:', types)
    with_content = sum(1 for it in all_items
                       if it.get('content', {}).get('content'))
    print('    含全文条数:', with_content)
    print('    已保存 output/collection_raw_pages.json / collection_all_items.json')


if __name__ == '__main__':
    main()
