# -*- coding: utf-8 -*-
"""06 检查本机 Chrome 是否有知乎登录态（只读副本，不改动原文件）

- 复制 Cookies sqlite 副本，统计 zhihu 域 cookie 与加密前缀
- 读取 Local State 判断加密方案（v10 / v20 App-Bound）
"""
import json
import os
import shutil
import sqlite3

UD = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data"
COOKIE_SRC = os.path.join(UD, r"Default\Network\Cookies")
COOKIE_DST = os.path.join("output", "chrome_cookies_copy.db")
LOCAL_STATE = os.path.join(UD, "Local State")

# Chrome 版本
ver_file = os.path.join(UD, "Last Version")
if os.path.exists(ver_file):
    print('[0] Chrome 版本:', open(ver_file, encoding='utf-8').read().strip())

# Local State 加密 key 前缀
try:
    ls = json.load(open(LOCAL_STATE, encoding='utf-8'))
    ek = ls.get('os_crypt', {}).get('encrypted_key', '')
    import base64
    raw = base64.b64decode(ek) if ek else b''
    print('[1] encrypted_key 前缀:', raw[:5], '(b"DPAPI"=传统 DPAPI)')
except Exception as e:
    print('[1] Local State 读取失败:', e)

# 复制 cookies 副本并查询
try:
    shutil.copy2(COOKIE_SRC, COOKIE_DST)
    conn = sqlite3.connect(COOKIE_DST)
    rows = conn.execute(
        "SELECT host_key, name, substr(encrypted_value,1,3) "
        "FROM cookies WHERE host_key LIKE '%zhihu%'").fetchall()
    print('\n[2] zhihu 域 cookie 数:', len(rows))
    for host, name, prefix in rows[:40]:
        print('    %-18s %-28s %s' % (host, name, prefix))
    # 关键登录态 cookie
    names = {r[1] for r in rows}
    print('\n[3] 关键 cookie 存在性:')
    for key in ('z_c0', 'SESSIONID', 'd_c0', 'q_c1'):
        print('    %-10s %s' % (key, '存在' if key in names else '无'))
    conn.close()
except Exception as e:
    print('[2] cookies 读取失败:', e)
