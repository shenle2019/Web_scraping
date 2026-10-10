# -*- coding: utf-8 -*-
"""
惠农网 H5（m.cnhnb.com）供应列表采集爬虫
================================================================
技术要点：请求签名 x-client-sign 的逆向与复刻
  逆向来源：m.cnhnb.com 首页加载的 vendors.app.js（webpack 模块 311）
  签名算法（H5 场景 secretType=2，生产环境密钥）：
      L = MD5(nonce)
      B = SHA1(timestamp)
      N = MD5(nonce + deviceId)
      C = SHA1(secret + timestamp)
      C = C[len-16 : len-1]          # 取中间 15 个 hex 字符
      D = 无符号十六进制转十进制(C)   # 复刻 Long.fromString(C,true,16).toUnsigned().toString(10)
      sign = SHA384(L + "!" + B + "!" + N + "!" + D)
  签名器已用 3 组线上真实抓包样本 100% 匹配验证（见 README.md）。

目标接口：POST https://appapi.cnhnb.com/recq/api/transform/supply/v501/index
  请求体：{"pageNumber": N, "pageSize": 20, "ad_ch": 1}
  响应：{"code":0,"msg":"success","data":{"datas":[...],...}}

合规声明：本脚本仅限个人学习研究使用，禁止商用；
  默认低频访问（每次请求间隔 >= 1.5 秒），请勿修改为高频采集。

用法：
  python cnhnb_supply_crawler.py                # 默认采集 3 页
  python cnhnb_supply_crawler.py --pages 5      # 采集 5 页
  python cnhnb_supply_crawler.py --pages 2 --page-size 10
"""
import argparse
import hashlib
import json
import os
import secrets
import sys
import time
from datetime import datetime

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------- 签名器（纯 Python 复刻，已用 3 组抓包样本验证） ----------------
# 生产环境 H5 密钥（逆向自 vendors.app.js 模块 311 RC4 混淆字符串解码结果）
SECRET_H5_PROD = "EOi^0N5sWWHhkrF2A0gekY9U20BgnAcr"


def make_sign(nonce: str, timestamp: str, device_id: str) -> str:
    """复刻 vendors.app.js 模块 311 的签名函数（secretType=2，H5 场景）"""
    L = hashlib.md5(nonce.encode()).hexdigest()
    B = hashlib.sha1(timestamp.encode()).hexdigest()
    N = hashlib.md5((nonce + device_id).encode()).hexdigest()
    C = hashlib.sha1((SECRET_H5_PROD + timestamp).encode()).hexdigest()
    C = C[len(C) - 16: len(C) - 1]           # substring(len-16, len-1) 共 15 字符
    D = str(int(C, 16))                       # Long 无符号转十进制
    F = "!".join([L, B, N, D])
    return hashlib.sha384(F.encode()).hexdigest()


# ---------------- 请求头构造 ----------------
H5_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
         "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")
B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def to_b36(num: int, length: int) -> str:
    s = ""
    while num > 0 and len(s) < length:
        s = B36[num % 36] + s
        num //= 36
    return s.rjust(length, "0")


def rand_device_id() -> str:
    """生成符合服务端格式校验的设备 ID（7-4-4-4-9 位十六进制，共 28 hex）"""
    h = secrets.token_hex(14)
    return "%s-%s-%s-%s-%s" % (h[0:7], h[7:11], h[11:15], h[15:19], h[19:28])


def build_headers():
    """构造带 x-client-* 签名的完整请求头（复刻浏览器实际行为）"""
    nonce = secrets.token_hex(16)                       # 32 位 hex，每次请求随机
    timestamp = str(int(time.time() * 1000))            # 毫秒时间戳
    device_id = rand_device_id()                        # 符合服务端格式校验的设备 ID
    sign = make_sign(nonce, timestamp, device_id)

    trace_id = to_b36(int(time.time() * 1000), 9) + to_b36(secrets.randbelow(78364164096), 7)
    sid = "S_" + to_b36(int(time.time() * 1000), 9) + to_b36(secrets.randbelow(78364164096), 7)

    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN",
        "content-type": "application/json",
        "origin": "https://m.cnhnb.com",
        "referer": "https://m.cnhnb.com/",
        "user-agent": H5_UA,
        "x-b3-traceid": trace_id,
        "x-client-appid": "5",
        "x-client-environment": "pro",
        "x-client-id": device_id,
        "x-client-nonce": nonce,
        "x-client-page": "/",
        "x-client-sid": sid,
        "x-client-sign": sign,
        "x-client-time": timestamp,
        "x-hn-job": X_HN_JOB,
    }


API_URL = "https://appapi.cnhnb.com/recq/api/transform/supply/v501/index"

# 关键头：服务端实际校验此头（缺省即返回 500301），内容为官方"招聘信"彩蛋
X_HN_JOB = ("If you see these message, I hope you dont hack us, "
            "I hope you can join us! Please visit https://www.cnhnkj.com/job.html")


def pick_item(d: dict) -> dict:
    """从原始条目中提取关键字段（宽容取值，字段缺失则为 None）"""
    return {
        "supplyId": d.get("supplyId"),
        "title": d.get("title"),
        "price": d.get("price"),
        "priceUnit": d.get("priceUnit"),
        "unitName": d.get("unitName"),
        "stock": d.get("stock"),
        "province": d.get("provinceName") or d.get("provinceId"),
        "city": d.get("cityName") or d.get("cityId"),
        "shopName": d.get("shopName") or d.get("userName"),
        "publishTime": d.get("publishTime") or d.get("createTime"),
        "categoryName": d.get("categoryName"),
    }


def crawl(pages: int, page_size: int, interval: float, out_dir: str):
    session = requests.Session()
    all_items, raw_pages, logs = [], [], []

    def log(msg=""):
        print(msg)
        logs.append(str(msg))

    log("=" * 60)
    log("惠农网 H5 供应列表采集（签名逆向复刻版）")
    log("仅限学习研究，禁止商用；请求间隔 %.1fs" % interval)
    log("=" * 60)

    for page in range(1, pages + 1):
        headers = build_headers()
        body = {"pageNumber": page, "pageSize": page_size, "ad_ch": 1}
        try:
            resp = session.post(API_URL, headers=headers, json=body, timeout=20)
            j = resp.json()
        except Exception as e:
            log("[第%d页] 请求异常: %r" % (page, e))
            time.sleep(interval)
            continue

        code, msg = j.get("code"), j.get("msg")
        datas = ((j.get("data") or {}).get("datas")) or []
        log("[第%d页] HTTP=%s code=%s msg=%s 本条数=%d 签名前8位=%s..."
            % (page, resp.status_code, code, msg, len(datas), headers["x-client-sign"][:8]))

        if code != 0:
            log("  -> 签名或参数被拒，响应: %s" % json.dumps(j, ensure_ascii=False)[:200])
            break
        if not datas:
            log("  -> 无更多数据，提前结束")
            break

        raw_pages.append({"page": page, "datas": datas})
        for d in datas:
            all_items.append(pick_item(d))
            if len(all_items) <= 5:
                log("    - %s | %s%s | %s" % (d.get("title"), d.get("price"),
                                              d.get("priceUnit") or "", d.get("provinceName") or ""))

        time.sleep(interval)

    # ------- 保存结果 -------
    os.makedirs(out_dir, exist_ok=True)
    ts_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = os.path.join(out_dir, "cnhnb_supply_raw_%s.json" % ts_name)
    slim_path = os.path.join(out_dir, "cnhnb_supply_items_%s.json" % ts_name)

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_pages, f, ensure_ascii=False, indent=2)
    with open(slim_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    log()
    log("采集完成：共 %d 页、%d 条供应数据" % (len(raw_pages), len(all_items)))
    log("原始数据: %s" % raw_path)
    log("提取字段: %s" % slim_path)
    return all_items


def main():
    ap = argparse.ArgumentParser(description="惠农网 H5 供应列表采集（学习研究用）")
    ap.add_argument("--pages", type=int, default=3, help="采集页数（默认 3）")
    ap.add_argument("--page-size", type=int, default=20, help="每页条数（接口上限约 20）")
    ap.add_argument("--interval", type=float, default=1.5, help="请求间隔秒（默认 1.5，勿低于 1）")
    ap.add_argument("--out", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"),
                    help="输出目录")
    args = ap.parse_args()
    crawl(args.pages, args.page_size, max(args.interval, 1.0), args.out)


if __name__ == "__main__":
    main()
