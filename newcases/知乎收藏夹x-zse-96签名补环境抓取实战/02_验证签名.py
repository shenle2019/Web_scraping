# -*- coding: utf-8 -*-
"""02 验证：补环境黑箱签名 + requests 实测 collections/items 接口

签名公式（调用方前置步骤，ZP 只管其后加密）：
    x-zse-96 = "2.0_" + ZP(md5(x-zse-93 + "+" + url + "+" + d_c0))
    其中 ZP = yuan.loader(1514)["ZP"]，由 Node 补环境脚本黑箱产出。

仅限学习研究，禁止商用。
"""
import hashlib
import json
import subprocess
import time
import uuid

import requests

COLLECTION_ID = '323709385'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
# 课件里的 x-zst-81 静态指纹串（另一路 JSVMP 产物，本案例直接沿用）
X_ZST_81 = ('3_2.0aR_sn77yn6O92wOB8hPZnQr0EMYxc4f18wNBUgpTQ6nxERFZKTY0-4Lm-h3_tufIwJS8gcx'
            'TgJS_AuPZNcXCTwxI78YxEM20s4PGDwN8gGcYAupMWufIoLVqr4gxrRPOI0cY7HL8qun9g93m'
            'FukyigcmebS_FwOYPRP0E4rZUrN9DDom3hnynAUMnAVPF_PhaueTFAuqa9F9kcLBEGFYCGeYFw2p'
            '2eS_fcXMoAwOave8FhpCnU2BbUL1_bxBHreTVMo_XJpYQCCO1hVKfXpKgJx1JBVOcw28RgemqULqJ'
            '_xVfBNftcfMpqeL6GHBjqcM_vS_iJoGLUYOuC39ihXKCUUBnqNx6w2CwhpOBhVMJgxMyuY_y9Y0O'
            'g_zCqHmBrHf5rNOkcwyDUOfuhLmMCofrHHMhgeBYCYZ0B3O_BO1gwVm3htKJ9HKbggq-qX_99t9p0'
            'oBcrx9AUosJ8SqhgtKr4omaUef8JLmthxMQANCe8ws')


def node_sign(md5_list):
    """调用 Node 补环境脚本批量签名（黑箱，不纯算）"""
    p = subprocess.run(['node', r'js\zhihu_sign.js', json.dumps(md5_list)],
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode != 0:
        print('node 错误输出:', p.stderr[-500:])
        raise SystemExit('签名失败')
    return json.loads(p.stdout.strip().splitlines()[-1])


def make_sign_headers(path_query, d_c0, url_mode='path'):
    """构造带 x-zse-96 的请求头"""
    x93 = '101_3_3.0'
    sign_src = '%s+%s+%s' % (x93, path_query, d_c0)
    md5hex = hashlib.md5(sign_src.encode()).hexdigest()
    sign = node_sign([md5hex])[0]
    print('    [%s] 拼串: %s' % (url_mode, sign_src))
    print('    [%s] md5 : %s' % (url_mode, md5hex))
    return {
        'x-zse-93': x93,
        'x-zse-96': '2.0_' + sign,
        'x-zst-81': X_ZST_81,
        'x-requested-with': 'fetch',
        'x-api-version': '3.0.53',
        'Referer': 'https://www.zhihu.com/collection/%s' % COLLECTION_ID,
    }


s = requests.Session()
s.headers.update({'User-Agent': UA})
d_c0 = uuid.uuid4().hex + '|' + str(int(time.time()))
s.cookies.set('d_c0', d_c0, domain='.zhihu.com')
print('[0] 自造 d_c0 =', d_c0)

path_query = ('/api/v4/collections/%s/items?offset=0&limit=20') % COLLECTION_ID

# 形态 A：签名源串用 path+query（不带域名）
print('\n[A] 签名源串 = path+query')
hA = make_sign_headers(path_query, d_c0, 'A')
rA = s.get('https://www.zhihu.com' + path_query, headers=hA, timeout=30)
print('    ->', rA.status_code, rA.text[:250])

# 形态 B：签名源串用完整 URL
if rA.status_code != 200:
    print('\n[B] 签名源串 = 完整 URL')
    hB = make_sign_headers('https://www.zhihu.com' + path_query, d_c0, 'B')
    rB = s.get('https://www.zhihu.com' + path_query, headers=hB, timeout=30)
    print('    ->', rB.status_code, rB.text[:250])

# 形态 C：去掉 x-zst-81 再试 A
if rA.status_code != 200:
    print('\n[C] 形态A 但去掉 x-zst-81 头')
    hC = make_sign_headers(path_query, d_c0, 'C')
    hC.pop('x-zst-81')
    rC = s.get('https://www.zhihu.com' + path_query, headers=hC, timeout=30)
    print('    ->', rC.status_code, rC.text[:250])
