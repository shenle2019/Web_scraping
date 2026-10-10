# -*- coding: utf-8 -*-
"""
Day21 练习案例 2/4 —— 精灵数据 jinglingshuju.com「响应 AES 加密」逆向
============================================================================
【练习来源】Day21 课件「练习案例」base64 目标2：
    aHR0cHM6Ly93d3cuamluZ2xpbmdzaHVqdS5jb20vYXJ0aWNsZXM=
    = https://www.jinglingshuju.com/articles

【逆向结论】（axios 拦截器响应解密链 + 接口字典 a5dfecc.js 定位所得）
    接口:  POST https://vapi.jinglingshuju.com/Data/getNewsList
    参数:  form: page=1&num=10（application/x-www-form-urlencoded）
    应答:  {"code":"200","status":1,"data":"<AES密文>"}  data 为字符串密文
    解密:  AES-ECB / PKCS7 / key = "DXZWdxUZ5jgsUFPF"（UTF-8 16字节）
           源码: var e = AES.decrypt(data, z, {
                     iv: Utf8.parse(j.substr(0, 16)),   // ECB 下为障眼法
                     mode: y.a.mode.ECB, padding: y.a.pad.Pkcs7
                 });
                 return JSON.parse(e.toString(Utf8));
           j = "DXZWdxUZ5jgsUFPF";  z = Utf8.parse(j)

【合规声明】匿名、低频（每次运行仅 1 个请求）、仅用于学习验证解密算法，
           不批量采集、不绕过任何登录/风控，输出数据仅本地留存。
"""
import base64
import json
import os

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

API_URL = "https://vapi.jinglingshuju.com/Data/getNewsList"
AES_KEY = b"DXZWdxUZ5jgsUFPF"          # 源码 j="DXZWdxUZ5jgsUFPF"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def aes_ecb_decrypt(cipher_text: str, key: bytes) -> str:
    """复刻拦截器解密：AES-ECB + Pkcs7，输入为 base64 字符串"""
    raw = base64.b64decode(cipher_text)
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(cipher.decrypt(raw), AES.block_size).decode("utf-8")


def request_news(page=1, num=10, timeout=15):
    headers = {
        "User-Agent": UA,
        "Referer": "https://www.jinglingshuju.com/",
        "Origin": "https://www.jinglingshuju.com",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    return requests.post(API_URL, data={"page": page, "num": num},
                         headers=headers, timeout=timeout)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=" * 72)
    print("[1] 请求接口 POST %s  form: page=1&num=10" % API_URL)

    resp = request_news()
    print("    HTTP %s  Content-Type: %s" % (resp.status_code,
                                             resp.headers.get("Content-Type", "")))
    body = resp.json()
    print("    外层应答: code=%s status=%s data 类型=%s"
          % (body.get("code"), body.get("status"), type(body.get("data")).__name__))

    envelope = body.get("data")
    if isinstance(envelope, str):
        cipher_text = envelope
    elif isinstance(envelope, dict):
        cipher_text = envelope.get("data", "")
    else:
        cipher_text = ""
    print("    密文样例: %s ...（长度 %d）" % (cipher_text[:64], len(cipher_text)))

    # ---- 对照组：错误 key 解密（本地验证，不发额外请求）----
    bad_ok = True
    try:
        wrong = aes_ecb_decrypt(cipher_text, b"0000000000000000")
        bad_ok = wrong.lstrip().startswith(("{", "["))
    except Exception:
        bad_ok = False
    print("\n[2] 对照组（错误 key 解密）-> %s"
          % ("仍得到 JSON，异常" if bad_ok else "解出乱码/抛异常，证明必须正确密钥"))

    # ---- 正确 key 解密 ----
    plain = aes_ecb_decrypt(cipher_text, AES_KEY)
    data = json.loads(plain)
    if isinstance(data, dict):
        items = data.get("list") or data.get("data") or data.get("rows") or []
        total = data.get("total") or data.get("count")
    else:
        items, total = data, None
    print("\n[3] AES-ECB 解密成功，明文 JSON 顶层类型=%s 文章数=%d total=%s"
          % (type(data).__name__, len(items), total))
    for i, it in enumerate(items[:3], 1):
        title = (it.get("title") or it.get("name") or "") if isinstance(it, dict) else str(it)
        print("    %d. %s" % (i, title[:60]))

    result = {
        "target": "jinglingshuju.com / vapi.jinglingshuju.com Data/getNewsList",
        "cipher_sample": cipher_text[:120],
        "http_status": resp.status_code,
        "verified": bool(items),
        "key": AES_KEY.decode(),
        "decrypted_top_keys": list(data.keys()) if isinstance(data, dict) else None,
        "item_count": len(items),
        "sample": items[:3],
    }
    fp = os.path.join(OUT_DIR, "jlsj_news_result.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n[4] 验证结果已保存: %s" % fp)


if __name__ == "__main__":
    main()
