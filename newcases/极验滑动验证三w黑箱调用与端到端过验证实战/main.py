# -*- coding: utf-8 -*-
"""
极验滑动验证「三 w」黑箱调用 · 端到端过验证实战
==================================================================
Day29/30/31 三课整合复刻（自研编排版）：

  设计思路
  --------
  - 加密全黑箱：三个 w（w1 配置加密 / w2 点击验证 / w3 滑动轨迹）全部交给
    Node 运行课件还原出的 JS（js/first_w.js、js/second_w.js、js/third_w.js），
    Python 侧不做任何加密算法的纯算重写；
  - 编排与图像全 Python：图片乱序还原（PIL）、缺口测距（OpenCV 模板匹配）、
    滑动轨迹生成（缓动算法）。

  流程 8 步
  ---------
  1. register-slide-official 拿 gt / challenge
  2. gettype.php             探测核心 js
  3. w1 → get.php (api.geetest.com)     第一个 w（配置体加密）
  4. w2 → ajax.php (api.geevisit.com)   第二个 w（点击验证）
  5. get.php (api.geevisit.com)         拿 new_challenge / c / s / 图片地址
  6. 下载图片 → PIL 乱序还原 → OpenCV 测距 → 生成滑动轨迹
  7. w3 → ajax.php (api.geevisit.com)   第三个 w（滑动轨迹）
  8. 判定响应中的 validate 字段

  产物：output/run_*.log、output/result.json、output/imgs/
"""
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
JS_DIR = BASE_DIR / 'js'
OUTPUT_DIR = BASE_DIR / 'output'
IMG_DIR = OUTPUT_DIR / 'imgs'
NODE = shutil.which('node')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

# 会话级日志文件（run_启动时刻.txt，用 .txt 避开 .gitignore 的 *.log 规则，便于入库）
LOG_FILE = OUTPUT_DIR / f"run_{time.strftime('%Y%m%d_%H%M%S')}.txt"


def log(msg):
    """控制台 + 日志文件双写"""
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as fp:
        fp.write(line + '\n')


def now_ms():
    return str(int(time.time() * 1000))


def brief(text, n=160):
    """长串截断显示"""
    text = str(text)
    return text if len(text) <= n else text[:n] + f'...({len(text)} chars)'


def jsonp_op(text):
    """解析 jsonp 响应：geetest_xxx({...}) → dict"""
    m = re.search(r'\((?P<code>.*)\)', text, re.S)
    return json.loads(m.group('code'))


def call_js(script, payload):
    """黑箱调用：node js/xxx.js '<json>' → 解析 stdout 最后一行 JSON"""
    cmd = [NODE, str(JS_DIR / script), json.dumps(payload, ensure_ascii=False)]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(JS_DIR), capture_output=True,
                          text=True, encoding='utf-8', timeout=60)
    cost = time.time() - t0
    if proc.returncode != 0:
        raise RuntimeError(f'{script} 运行失败: {proc.stderr.strip()}')
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    log(f'  [黑箱] node {script} 完成（{cost:.2f}s，输出 {len(proc.stdout)} 字节）')
    return result


# ============================ 流程步骤 ============================

def step1_register(sess):
    """注册验证码：拿 gt / challenge"""
    url = 'https://www.geetest.com/demo/gt/register-slide-official'
    ret = sess.get(url, params={'t': now_ms()}, headers={'user-agent': UA}, timeout=15).json()
    gt, challenge = ret['gt'], ret['challenge']
    log(f'[1/8] 注册成功 gt={gt}')
    log(f'      challenge={challenge}')
    return gt, challenge


def step2_gettype(sess, gt, challenge):
    """探测核心 js（响应仅记录）"""
    url = 'https://api.geetest.com/gettype.php'
    ret = sess.get(url, params={'gt': gt, 'challenge': challenge},
                   headers={'user-agent': UA}, timeout=15).text
    log(f'[2/8] gettype.php 完成，响应 {len(ret)} 字节：{brief(ret, 100)}')


def step3_w1(sess, gt, challenge):
    """第一个 w：黑箱生成 → 请求 get.php（api.geetest.com）"""
    ret = call_js('first_w.js', {'gt': gt, 'challenge': challenge})
    aes_key = ret['aesKey']
    w1 = ret['s']['w']
    log(f'      w1 长度={len(w1)}，aesKey={aes_key}（共享给 w2）')

    params = {'gt': gt, 'challenge': challenge, 'lang': 'zh-cn', 'pt': '0',
              'client_type': 'web', 'callback': f'geetest_{now_ms()}', 'w': w1}
    resp = sess.get('https://api.geetest.com/get.php', params=params,
                    headers={'user-agent': UA}, timeout=15).text
    log(f'[3/8] get.php#1(w1) 完成，响应 {len(resp)} 字节：{brief(resp, 100)}')
    return aes_key


def step4_w2(sess, gt, challenge, aes_key):
    """第二个 w：黑箱生成（复用 w1 的 aesKey）→ 请求 ajax.php（点击验证）"""
    ret = call_js('second_w.js', {'aesKey': aes_key, 'gt': gt, 'challenge': challenge})
    w2 = ret['w']
    log(f'      w2 长度={len(w2)}')

    params = {'gt': gt, 'challenge': challenge, 'lang': 'zh-cn', 'pt': '0',
              'client_type': 'web', 'w': w2, 'callback': f'geetest_{now_ms()}'}
    resp = sess.get('https://api.geevisit.com/ajax.php', params=params,
                    headers={'user-agent': UA}, timeout=15).text
    log(f'[4/8] ajax.php#1(w2 点击验证) 完成：{brief(resp, 200)}')
    return jsonp_op(resp) if '(' in resp else {}


def step5_getphp2(sess, gt, challenge):
    """滑动验证的 get.php：拿 new_challenge / c / s / 图片地址"""
    params = {'is_next': 'true', 'type': 'slide3', 'gt': gt, 'challenge': challenge,
              'lang': 'zh-cn', 'https': 'true', 'protocol': 'https://',
              'offline': 'false', 'product': 'embed', 'api_server': 'api.geevisit.com',
              'isPC': 'true', 'autoReset': 'true', 'width': '100%',
              'callback': f'geetest_{now_ms()}'}
    resp = sess.get('https://api.geevisit.com/get.php', params=params,
                    headers={'user-agent': UA}, timeout=15).text
    data = jsonp_op(resp)
    new_challenge = data['challenge']
    log(f'[5/8] get.php#2(slide3) 完成：new_challenge={new_challenge}（比原值多 2 位）')
    log(f'      c={data["c"]} s={data["s"]}')
    return data


def step6_prepare(sess, gt, challenge, get2):
    """图片下载 → PIL 乱序还原 → OpenCV 测距 → 缓动轨迹生成"""
    from urllib.parse import urljoin
    from PIL import Image
    import cv2
    import random

    static = 'https://static.geetest.com/'
    files = {}
    for name, key in [('bg.jpg', 'bg'), ('slice.jpg', 'slice')]:
        url = urljoin(static, get2[key])
        data = sess.get(url, headers={'user-agent': UA}, timeout=15).content
        path = IMG_DIR / name
        path.write_bytes(data)
        files[name] = path
        log(f'      下载图片 {name}（{len(data)} 字节）')

    # ---- 乱序还原：52 块（26列x2行），源步进 12px 取 10px，拼到 260x160 ----
    old = Image.open(files['bg.jpg'])
    new = Image.new('RGB', (260, 160))
    ut = [39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26,
          36, 37, 31, 30, 44, 45, 43, 42, 12, 13, 23, 22, 14, 15, 21, 20, 8, 9,
          25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]
    half = 80
    for i in range(52):
        c = ut[i] % 26 * 12 + 1
        u = half if ut[i] > 25 else 0
        block = old.crop((c, u, c + 10, u + half))
        new.paste(block, (i % 26 * 10, half if i > 25 else 0))
    bg_restored = IMG_DIR / 'new_bg_img.jpg'
    new.save(bg_restored)
    log(f'[6/8] 图片还原完成（{old.size[0]}x{old.size[1]} → 260x160）')

    # ---- 缺口测距：Canny 边缘 + 模板匹配 ----
    # 注意：cv2.imread 在 Windows 下不支持中文路径，用 np.fromfile + imdecode 绕过
    import numpy as np

    def imread_cn(path):
        return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)

    bg = imread_cn(bg_restored)
    slide = imread_cn(files['slice.jpg'])
    bg = cv2.Canny(cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY), 255, 255)
    slide = cv2.Canny(cv2.cvtColor(slide, cv2.COLOR_BGR2GRAY), 255, 255)
    result = cv2.matchTemplate(bg, slide, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    distance = max_loc[0]
    log(f'      缺口测距 distance={distance}（匹配度 {max_val:.4f}）')

    # ---- 缓动轨迹生成（ease_out_expo） ----
    def ease_out_expo(sep):
        return 1 if sep == 1 else 1 - pow(2, -10 * sep)

    count = 30 + int(distance / 2)
    track = [[random.randint(-50, -10), random.randint(-50, -10), 0], [0, 0, 0]]
    t = random.randint(50, 100)
    _x = 0
    for i in range(count):
        x = round(ease_out_expo(i / count) * distance)
        t += random.randint(10, 20)
        if x == _x:
            continue
        track.append([x, 0, t])
        _x = x
    track.append([distance, 0, t])
    log(f'      轨迹生成 {len(track)} 点，总耗时 passtime={t}ms')
    return distance, t, track


def step7_w3(sess, gt, new_challenge, distance, passtime, guiji, c, s):
    """第三个 w：黑箱生成 → 请求 ajax.php（滑动验证）"""
    ret = call_js('third_w.js', {'distance': distance, 'passtime': passtime,
                                 'guiji': guiji, 'c': c, 's': s,
                                 'gt': gt, 'challenge': new_challenge})
    w3 = ret['w']
    log(f'      w3 长度={len(w3)}')

    ret['callback'] = f'geetest_{now_ms()}'
    resp = sess.get('https://api.geevisit.com/ajax.php', params=ret,
                    headers={'user-agent': UA}, timeout=15).text
    log(f'[7/8] ajax.php#2(w3 滑动验证) 完成：{brief(resp, 260)}')
    return jsonp_op(resp)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    IMG_DIR.mkdir(exist_ok=True)
    t_start = time.time()
    steps = {}

    def mark(name, t0):
        steps[name] = round(time.time() - t0, 2)

    log('=' * 62)
    log('极验滑动验证「三 w」黑箱调用 · 端到端过验证 开始')
    log('=' * 62)

    sess = requests.Session()
    t0 = time.time()
    gt, challenge = step1_register(sess)
    mark('register', t0)

    t0 = time.time()
    step2_gettype(sess, gt, challenge)
    mark('gettype', t0)

    t0 = time.time()
    aes_key = step3_w1(sess, gt, challenge)
    mark('w1_getphp', t0)

    t0 = time.time()
    step4_w2(sess, gt, challenge, aes_key)
    mark('w2_ajax', t0)

    t0 = time.time()
    get2 = step5_getphp2(sess, gt, challenge)
    new_challenge = get2['challenge']
    mark('getphp2', t0)

    t0 = time.time()
    distance, passtime, guiji = step6_prepare(sess, gt, challenge, get2)
    mark('image_track', t0)

    t0 = time.time()
    final_resp = step7_w3(sess, gt, new_challenge, distance, passtime, guiji, get2['c'], get2['s'])
    mark('w3_ajax', t0)

    # ---- 判定结果 ----
    validate = final_resp.get('validate', '')
    success = bool(validate)
    log('[8/8] 验证' + ('通过 ✔ validate=' + validate if success
                        else '未通过：' + json.dumps(final_resp, ensure_ascii=False)))
    total = round(time.time() - t_start, 2)
    log(f'总耗时 {total}s')

    result = {
        'success': success,
        'gt': gt,
        'challenge': challenge,
        'new_challenge': new_challenge,
        'aeskey': aes_key,
        'slide': {'distance': distance, 'passtime': passtime, 'track_points': len(guiji)},
        'validate': validate,
        'final_response': final_resp,
        'step_seconds': steps,
        'total_seconds': total,
        'log_file': LOG_FILE.name,
    }
    (OUTPUT_DIR / 'result.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    log(f'结果已写入 output/result.json')
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
