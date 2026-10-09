# -*- coding: utf-8 -*-
"""案例3 企名片 首页推荐资讯爬虫（Day20 逆向作业 · 正式交付版）

目标站点: https://www.qimingpian.com/          （企名片 - 首页"最新融资资讯"）
数据接口: GET https://vipapi.qimingpian.cn/HomePage/recommendInfo

逆向要点:
  1. 接口响应为: {"status":0,"message":"success","encrypt_data":"<base64密文>"}
     明文数据藏在 encrypt_data 字段中，需要解密；
  2. 前端解密函数（来自 cms.qmpoa.com/_nuxt/iconfont.570166c6.js）:
       function ct(me){ return JSON.parse(kt("50e2673ff3ecb6e82f15fe4c",
                       atob(me), 0, 0, "012345677890123", 1)) }
     其中 kt 为经典 des.js 系 3DES 实现（key 24 字节走 3DES、ECB、去尾补位）；
  3. 实测该接口（老版 vipapi）使用的 key 为 "5e5062e82f15fe4ca9d24bc5"，
     Python 等价实现 = pycryptodome 的 DES3-ECB 解密 + 去 PKCS7 补位
     （已与 Node 执行原版 JS 的结果逐字节比对一致）。

输出: 作业结果/案例3_企名片_推荐资讯.json / .csv
"""
import base64
import csv
import json
import os
import time

import requests
from Crypto.Cipher import DES3  # pip install pycryptodome

# ==================== 参数配置 ====================
OUT_DIR = "作业结果"
API = "https://vipapi.qimingpian.cn/HomePage/recommendInfo"
KEY = b"5e5062e82f15fe4ca9d24bc5"   # 24 字节 -> 3DES 密钥
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
# ==================================================


def decrypt_3des(b64_text):
    """3DES-ECB 解密 + 去 PKCS7 补位（等价于前端 kt(key, atob(密文), 0, 0, iv, 1)）"""
    cipher_text = base64.b64decode(b64_text)
    cipher = DES3.new(KEY, DES3.MODE_ECB)
    plain = cipher.decrypt(cipher_text)
    pad = plain[-1]                     # JS kt 尾部逻辑: 末尾字节 <=8 则截掉
    if 0 < pad <= 8:
        plain = plain[:-pad]
    return plain.decode("utf-8")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    headers = {
        "accept": "application/json, text/plain, */*",
        "origin": "https://www.qimingpian.com",
        "referer": "https://www.qimingpian.com/",
        "user-agent": UA,
    }
    resp = requests.get(API, headers=headers, timeout=20)
    resp.raise_for_status()
    result = resp.json()
    print("接口状态: %s | status=%s" % (resp.status_code, result.get("status")))

    enc = result.get("encrypt_data")
    if not enc:
        raise RuntimeError("响应中没有 encrypt_data 字段: %s" % str(result)[:200])
    print("encrypt_data 长度: %d 字符（base64）" % len(enc))

    plain = decrypt_3des(enc)
    news = json.loads(plain)
    print("解密成功，共 %d 条资讯\n" % len(news))

    rows = []
    for item in news:
        rows.append({
            "资讯ID": item.get("id"),
            "内容": item.get("content"),
            "原文链接": item.get("link_url"),
            "发布时间": item.get("open_time"),
            "配图": item.get("link_img"),
        })

    # 保存 JSON
    json_path = os.path.join(OUT_DIR, "案例3_企名片_推荐资讯.json")
    payload = {
        "案例": "案例3 企名片-首页推荐资讯",
        "来源": "https://www.qimingpian.com/",
        "接口": API,
        "加密方式": "3DES-ECB + PKCS7（base64 传输），key=%s" % KEY.decode(),
        "抓取时间": time.strftime("%Y-%m-%d %H:%M:%S"),
        "条数": len(rows),
        "数据": rows,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    # 保存 CSV
    csv_path = os.path.join(OUT_DIR, "案例3_企名片_推荐资讯.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("已保存:")
    print("  " + json_path, "(%d 条)" % len(rows))
    print("  " + csv_path)
    print("\n全部资讯:")
    for row in rows:
        print("  [%s] %s" % (row["发布时间"], row["内容"][:50]))
    print("\n首条明文示例（解密后）:")
    print(json.dumps(news[0], ensure_ascii=False, indent=1)[:600])


if __name__ == "__main__":
    main()
