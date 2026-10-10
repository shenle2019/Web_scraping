# -*- coding: utf-8 -*-
"""
企名片频道资讯采集爬虫（打包 JS 解密 · 正式版）
================================================================
目标站点：https://www.qimingpian.com/（企名片）
数据接口：POST https://vipapi.qimingpian.cn/Activity/channelInformationByChannelName
  参数：channel_name/p/num/unionid（表单格式）

逆向要点：
  1. 接口响应为 {"status":0,"message":"success","encrypt_data":"<base64密文>"}
     真实数据在 encrypt_data 中，需 3DES 解密；
  2. 解密函数取自站点打包 JS（daily-activity.af082922.js / entry 入口产物）：
       V0(_) = JSON.parse(N0("sjdqmp20161205#_316@gfmt", L0.decode(_), 0, 0, "012345677890123", 1))
     其中 N0 为打包产物中的自定义 3DES 实现（ECB + PKCS7 去尾填充），
     L0.decode 等价于 base64 解码为二进制串；
  3. 实测本接口（vipapi）使用的密钥为 "5e5062e82f15fe4ca9d24bc5"（与打包 JS
     中 V0 硬编码密钥不同，属不同环境/接口的密钥配置）；
  4. 已用 Node 直接执行打包 JS 中提取的原版 N0 函数解密实时数据，
     与本脚本的 Python 复刻（pycryptodome DES3-ECB）逐字节一致（见 README）。

输出：output/ 下 JSON + CSV（仅本地保留）

合规声明：本脚本仅限个人学习研究使用，禁止商用；
  默认低频访问（请求间隔 >= 1.5 秒），保持小批量采集。

用法：
  python qmp_channel_crawler.py                    # 默认采集 3 页
  python qmp_channel_crawler.py --pages 5 --channel 24新声
"""
import argparse
import base64
import csv
import json
import os
import sys
import time
from datetime import datetime

import requests
from Crypto.Cipher import DES3  # pip install pycryptodome

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------- 逆向所得常量 ----------------
API = "https://vipapi.qimingpian.cn/Activity/channelInformationByChannelName"
KEY = b"5e5062e82f15fe4ca9d24bc5"          # 3DES 密钥（24 字节）
IV = "012345677890123"                     # 打包 JS 中的 IV 参数（ECB 模式下未参与运算）
PC_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")


def decrypt_encrypt_data(b64_text: str) -> dict:
    """复刻打包 JS 中 N0(key, bin(data), 0, 0, iv, 1)：3DES-ECB 解密 + PKCS7 去尾填充"""
    raw = DES3.new(KEY, DES3.MODE_ECB).decrypt(base64.b64decode(b64_text))
    pad = raw[-1] if raw else 0          # JS 逻辑：末尾字节 <=8 则截掉该长度
    if 0 < pad <= 8:
        raw = raw[:-pad]
    return json.loads(raw.decode("utf-8"))


def crawl(channel: str, pages: int, num: int, interval: float, out_dir: str):
    session = requests.Session()
    all_rows, raw_pages = [], []

    def log(msg=""):
        print(msg)

    log("=" * 60)
    log("企名片频道资讯采集（打包 JS 解密版）  频道: %s" % channel)
    log("仅限学习研究，禁止商用；请求间隔 %.1fs" % interval)
    log("=" * 60)

    for p in range(1, pages + 1):
        resp = session.post(
            API,
            headers={
                "accept": "application/json, text/plain, */*",
                "origin": "https://www.qimingpian.com",
                "referer": "https://www.qimingpian.com/",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": PC_UA,
            },
            data={"channel_name": channel, "page": str(p), "num": str(num), "unionid": ""},
            timeout=20)
        try:
            result = resp.json()
        except Exception as e:
            log("[第%d页] JSON 解析失败: %r | %s" % (p, e, resp.text[:150]))
            time.sleep(interval)
            continue

        if result.get("status") == 60004:
            log("[第%d页] 服务端登录限制: %s（未登录仅可看 1 页，翻页到此为止）"
                % (p, result.get("message")))
            log("  -> 学习研究场景不绕过登录限制，停止翻页")
            break
        if result.get("status") != 0 or "encrypt_data" not in result:
            log("[第%d页] 接口异常: %s" % (p, json.dumps(result, ensure_ascii=False)[:200]))
            time.sleep(interval)
            continue

        data = decrypt_encrypt_data(result["encrypt_data"])
        lst = data.get("list") or []
        log("[第%d页] 解密成功 本条数=%d min_create_time=%s" % (p, len(lst), data.get("min_create_time")))

        if not lst:
            log("  -> 无更多数据，提前结束")
            break

        raw_pages.append({"page": p, "data": data})
        for it in lst:
            all_rows.append({
                "newsId": it.get("news_id"),
                "name": it.get("name"),
                "content": it.get("content"),
                "newsAbstract": it.get("news_abstract"),
                "newsType": it.get("news_type"),
                "createTime": it.get("create_time"),
                "linkUrl": it.get("link_url"),
                "linkImg": it.get("link_img"),
                "activityId": it.get("activity_id"),
            })
            if p == 1 and len(all_rows) <= 3:
                log("    - [%s] %s" % (it.get("create_time"), (it.get("content") or "")[:42]))

        time.sleep(interval)

    # -------- 保存 --------
    os.makedirs(out_dir, exist_ok=True)
    ts_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = os.path.join(out_dir, "qmp_channel_raw_%s.json" % ts_name)
    json_path = os.path.join(out_dir, "qmp_channel_items_%s.json" % ts_name)
    csv_path = os.path.join(out_dir, "qmp_channel_items_%s.csv" % ts_name)

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_pages, f, ensure_ascii=False, indent=1)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"channel": channel, "来源": "https://www.qimingpian.com/",
                   "接口": API, "加密": "3DES-ECB+PKCS7(base64)", "采集时间": ts_name,
                   "条数": len(all_rows), "数据": all_rows}, f, ensure_ascii=False, indent=1)
    if all_rows:
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            w.writeheader()
            w.writerows(all_rows)

    log()
    log("采集完成：共 %d 页、%d 条资讯" % (len(raw_pages), len(all_rows)))
    log("原始数据: %s" % raw_path)
    log("提取字段: %s" % json_path)
    if all_rows:
        log("CSV: %s" % csv_path)
    return all_rows


def main():
    ap = argparse.ArgumentParser(description="企名片频道资讯采集（学习研究用）")
    ap.add_argument("--channel", type=str, default="24新声", help="频道名称（默认 24新声）")
    ap.add_argument("--pages", type=int, default=3, help="采集页数（默认 3）")
    ap.add_argument("--num", type=int, default=20, help="每页条数（默认 20）")
    ap.add_argument("--interval", type=float, default=1.5, help="请求间隔秒（默认 1.5）")
    ap.add_argument("--out", type=str,
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"),
                    help="输出目录")
    args = ap.parse_args()
    crawl(args.channel, args.pages, args.num, max(args.interval, 1.0), args.out)


if __name__ == "__main__":
    main()
