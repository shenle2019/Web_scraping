# -*- coding: utf-8 -*-
"""
21_video_url_extract.py —— 视频 URL 提取、真实访问与下载管线
=========================================================
链路：签名翻页采集（mock 站）→ 从 aweme_list 提取三类视频直链
      （play_addr ×2 / download_addr ×1 / cover ×1）→ 逐 URL 真实 GET
      → play 主链字节下载落盘 output/videos/ → 结构化 + 人类可读记录落盘

输出（全部在 output/，已 gitignore）：
  output/video_urls.json    结构化记录（每条视频的 URL 清单 + 访问结果）
  output/video_urls.txt     人类可读的"真实运行记录"
  output/videos/*.mp4       实际下载的视频字节（12 个）
  output/_video_result.json 用例汇总

合规说明：所有 URL 均为本地 mock 站（127.0.0.1:18990）自造直链；媒体字节
为确定性伪随机生成，不涉及任何真实站点、真实视频与真实 CDN。
"""
import json
import os
import sys
import time

import requests

import common

OUTPUT_DIR = os.path.join(common.BASE, "output")
VIDEO_DIR = os.path.join(OUTPUT_DIR, "videos")

# 与 20 管线一致的基础参数（max_cursor 用于翻页；演示值均为自造）
BASE_PARAMS = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "max_cursor": "0",
    "count": "6",
    "pc_client_type": "1",
    "version_code": "170400",
    "cookie_enabled": "true",
    "screen_width": "1496",
    "screen_height": "967",
    "browser_language": "zh-CN",
    "platform": "PC",
    "webid": "7371422219199055371",
    "msToken": "XBPLACEHOLDER",
}

CASES = []


def case(name, ok, detail=""):
    CASES.append({"name": name, "ok": bool(ok), "detail": detail})
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name, ("   " + detail) if detail else ""))
    return bool(ok)


def save_json(name, obj):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path


def extract_urls(item):
    """从单条 aweme 数据提取三类视频直链（复刻真实 API 的 video 字段形态）"""
    v = item.get("video", {})
    return {
        "play_addr": (v.get("play_addr") or {}).get("url_list") or [],
        "download_addr": (v.get("download_addr") or {}).get("url_list") or [],
        "cover": (v.get("cover") or {}).get("url_list") or [],
    }


def fetch(url, save_path=None, timeout=30):
    """真实 GET：返回 (status, size, ctype, cost_ms)；save_path 非空时流式落盘"""
    t0 = time.time()
    size = 0
    with requests.get(url, stream=True, timeout=timeout) as r:
        status, ctype = r.status_code, r.headers.get("Content-Type", "")
        f = open(save_path, "wb") if save_path else None
        try:
            for chunk in r.iter_content(8192):
                size += len(chunk)
                if f:
                    f.write(chunk)
        finally:
            if f:
                f.close()
    return status, size, ctype, round((time.time() - t0) * 1000)


def render_txt(records, summary):
    """人类可读记录：每条视频的三类直链与真实访问结果"""
    lines = [
        "视频 URL 提取与下载记录（真实运行输出）",
        "=" * 64,
        "生成时间: %s" % summary["generated_at"],
        "站点    : %s（本地 mock 站；页面/接口/媒体字节全部自造）" % common.URL_HOME,
        "总量    : %d 条视频 / %d 次直链访问（全部 200）/ 下载 %d 个 mp4 -> output/videos/"
        % (summary["total"], summary["access_count"], summary["saved"]),
        "",
    ]
    for i, rec in enumerate(records, 1):
        lines.append("[%02d] %s  %s" % (i, rec["aweme_id"], rec["desc"]))
        for a in rec["access"]:
            tag = a["kind"]
            if a["kind"] == "play_addr" and a["idx"] > 0:
                tag += "#%d" % (a["idx"] + 1)
            lines.append("     %-14s [%s] %7dB %-10s %4dms  %s%s" % (
                tag, a["status"], a["bytes"], a["content_type"], a["cost_ms"], a["url"],
                "  -> output/videos/%s.mp4" % rec["aweme_id"] if a["saved"] else ""))
        lines.append("")
    return "\n".join(lines)


def main():
    t0 = time.time()
    common.hr("21 视频 URL 提取与真实访问（提取 -> 访问 -> 下载 -> 落盘）")
    os.makedirs(VIDEO_DIR, exist_ok=True)

    records = []
    with common.LocalSite():
        # ---------- A. 签名翻页采集 ----------
        items = []
        for cursor in ("0", "6"):
            p = dict(BASE_PARAMS)
            p["max_cursor"] = cursor
            st, body, _ = common.signed_get(p)
            if st == 200:
                items += body.get("aweme_list", [])
        case("A 签名翻页采集 12 条", len(items) == 12, "n=%d" % len(items))

        # ---------- B. 视频 URL 提取 ----------
        n_play = n_dl = n_cov = 0
        for it in items:
            urls = extract_urls(it)
            n_play += len(urls["play_addr"])
            n_dl += len(urls["download_addr"])
            n_cov += len(urls["cover"])
            records.append({"aweme_id": it["aweme_id"], "desc": it["desc"],
                            "urls": urls, "access": []})
        case("B 三类直链提取完整（play/dl/cover）",
             n_play == 24 and n_dl == 12 and n_cov == 12,
             "play=%d download=%d cover=%d" % (n_play, n_dl, n_cov))

        # ---------- C. 逐 URL 真实访问 + play 主链下载 ----------
        n_ok, n_err, total_bytes, n_saved = 0, 0, 0, 0
        for rec in records:
            for kind, urls in rec["urls"].items():
                for idx, url in enumerate(urls):
                    save_path = None
                    if kind == "play_addr" and idx == 0:
                        save_path = os.path.join(VIDEO_DIR, "%s.mp4" % rec["aweme_id"])
                    st, size, ctype, ms = fetch(url, save_path=save_path)
                    ok = (st == 200 and size > 0)
                    n_ok += int(ok)
                    n_err += int(not ok)
                    total_bytes += size
                    if save_path and ok:
                        n_saved += 1
                    rec["access"].append({"kind": kind, "idx": idx, "url": url,
                                          "status": st, "bytes": size,
                                          "content_type": ctype, "cost_ms": ms,
                                          "saved": bool(save_path)})
        n_access = n_ok + n_err
        case("C 全部直链真实访问 200 且有字节", n_err == 0 and n_access == 48,
             "访问 %d 次 ok=%d err=%d 累计 %d bytes" % (n_access, n_ok, n_err, total_bytes))
        case("D play 主链下载落盘 12 个", n_saved == 12, "output/videos/ *.mp4 x%d" % n_saved)

    # ---------- E. 记录落盘 ----------
    summary = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "site": common.URL_HOME,
        "total": len(records),
        "access_count": n_access,
        "saved": n_saved,
        "total_bytes": total_bytes,
    }
    path_json = save_json("video_urls.json", {"summary": summary, "items": records})
    txt = render_txt(records, summary)
    path_txt = os.path.join(OUTPUT_DIR, "video_urls.txt")
    with open(path_txt, "w", encoding="utf-8") as f:
        f.write(txt)
    case("E 记录落盘（json + txt）",
         os.path.exists(path_json) and os.path.exists(path_txt),
         "video_urls.json / video_urls.txt")

    # ---------- 汇总 ----------
    n_pass = sum(1 for c in CASES if c["ok"])
    n_fail = len(CASES) - n_pass
    dur = round(time.time() - t0, 2)
    common.hr("汇总")
    print("  用例通过 %d / %d（耗时 %.2fs）" % (n_pass, len(CASES), dur))
    print("  记录落盘: %s" % path_txt)
    print("  下载目录: %s（%d 个 mp4，共 %d bytes）" % (VIDEO_DIR, n_saved, total_bytes))
    save_json("_video_result.json", {"pass": n_pass, "total": len(CASES), "cost_s": dur,
                                     "summary": summary, "cases": CASES})
    common.hr("VIDEO-URL %s" % ("PASS" if n_fail == 0 else "FAIL"))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
