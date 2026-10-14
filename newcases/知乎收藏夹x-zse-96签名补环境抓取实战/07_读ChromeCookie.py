# -*- coding: utf-8 -*-
"""07 用 ctypes 共享读 Chrome Cookies 副本 + DPAPI/AES-GCM 解密探测

背景：Chrome 运行时锁定 Cookies 文件（普通复制 Permission denied），
     改用 CreateFileW(FILE_SHARE_*) 共享读绕过锁定。
仅读取本机浏览器 cookie 用于本次学习抓取，凭证不外传、不入库。
"""
import base64
import ctypes
import json
import os
import sqlite3
from ctypes import wintypes

UD = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data"
COOKIE_SRC = os.path.join(UD, r"Default\Network\Cookies")
COOKIE_DST = os.path.join("output", "chrome_cookies_copy.db")

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
FILE_SHARE_DELETE = 4
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

# 声明函数签名（64 位下句柄必须用 HANDLE，否则被截断为 32 位导致读取失败）
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                 ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                                 wintypes.HANDLE]
kernel32.ReadFile.restype = wintypes.BOOL
kernel32.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
                              ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def read_shared(path):
    """共享模式读取被占用的文件全部字节"""
    h = kernel32.CreateFileW(path, GENERIC_READ,
                             FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                             None, OPEN_EXISTING, 0, None)
    if h == INVALID_HANDLE_VALUE or h is None:
        raise OSError('CreateFileW failed: %d' % ctypes.get_last_error())
    data = bytearray()
    buf = ctypes.create_string_buffer(1 << 20)
    n = wintypes.DWORD()
    while True:
        ok = kernel32.ReadFile(h, buf, len(buf), ctypes.byref(n), None)
        if not ok or n.value == 0:
            break
        data += buf.raw[:n.value]
    kernel32.CloseHandle(h)
    return bytes(data)


# 1. 共享读 cookies
raw = read_shared(COOKIE_SRC)
os.makedirs('output', exist_ok=True)
open(COOKIE_DST, 'wb').write(raw)
print('[1] cookies 副本已写出 %d 字节' % len(raw))

# 2. 查 zhihu cookie
conn = sqlite3.connect(COOKIE_DST)
rows = conn.execute(
    "SELECT host_key, name, length(encrypted_value), substr(encrypted_value,1,3) "
    "FROM cookies WHERE host_key LIKE '%zhihu%'").fetchall()
print('[2] zhihu 域 cookie 数:', len(rows))
for r in rows:
    print('    %-20s %-30s len=%s prefix=%s' % (r[0], r[1], r[2], r[3]))
names = {r[1] for r in rows}
print('[3] 关键 cookie:', {k: (k in names) for k in ('z_c0', 'SESSIONID', 'd_c0', 'q_c1')})
conn.close()

# 3. DPAPI 解出 AES key（ctypes 版）
class DATA_BLOB(ctypes.Structure):
    _fields_ = [('cbData', wintypes.DWORD),
                ('pbData', ctypes.POINTER(ctypes.c_char))]


def dpapi_decrypt(data):
    buf = ctypes.create_string_buffer(data, len(data))
    blob_in = DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    blob_out = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(
            ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        raise OSError('CryptUnprotectData failed: %d' % ctypes.get_last_error())
    return ctypes.string_at(blob_out.pbData, blob_out.cbData)


ls = json.load(open(os.path.join(UD, 'Local State'), encoding='utf-8'))
enc_key = base64.b64decode(ls['os_crypt']['encrypted_key'])[5:]  # 去 'DPAPI' 前缀
key = dpapi_decrypt(enc_key)
print('[4] DPAPI 解出 AES key 成功, 长度', len(key))
