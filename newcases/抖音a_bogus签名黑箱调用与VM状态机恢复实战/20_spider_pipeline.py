# -*- coding: utf-8 -*-
"""
20_spider_pipeline.py —— 端到端爬虫管线（翻页 + 风控反例）
=========================================================
链路：Python 管线 → node 02 引擎签名（恢复法）→ mock 站三层校验 → 数据落盘
用例：
  A1 翻页第 1 页（max_cursor=0）：200 / 6 条 / has_more=1 → output/aweme_page1.json
  A2 翻页第 2 页（max_cursor=6）：200 / 6 条 / has_more=0 → output/aweme_page2.json
     （每页独立 Node 进程签名 = 演示"连续多次签名"的工程可用性）
  B  无签名       → 406
  C  伪造乱串签名 → 406
  D  篡改真签名（改主体位）→ 406
  E  重放第 1 页签名 → 406（replay 防护）
  F  健康检查：白名单位数在当前量级（19~40）
汇总与结果落盘至 output/_pipeline_result.json（output/ 已 gitignore）

合规说明：全部请求只发往 127.0.0.1 本地模拟站；演示数据为自造内容。
"""
import json
import os
import sys
import time

import common

OUTPUT_DIR = os.path.join(common.BASE, "output")

# 与课件场景一致的基础参数（max_cursor 用于翻页；演示值均为自造）
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


def main():
    t0 = time.time()
    common.hr("20 端到端管线：翻页采集 + 风控反例（mock 站三层校验）")

    with common.LocalSite():
        # ---------- A1 第 1 页 ----------
        print("\n--- A1 翻页第 1 页（max_cursor=0）---")
        p1 = dict(BASE_PARAMS)
        st, body, sig1 = common.signed_get(p1)
        n1 = len(body.get("aweme_list", []))
        case("A1 状态码 200", st == 200, "status=%s" % st)
        case("A1 返回 6 条", n1 == 6, "n=%d" % n1)
        case("A1 has_more=1", body.get("has_more") == 1)
        case("A1 下一页游标=6", body.get("max_cursor") == 6, "cursor=%s" % body.get("max_cursor"))
        path1 = save_json("aweme_page1.json", body)
        print("     第 1 页落盘: %s" % path1)

        # ---------- A2 第 2 页（新签名） ----------
        print("\n--- A2 翻页第 2 页（max_cursor=6，独立新签名）---")
        p2 = dict(BASE_PARAMS)
        p2["max_cursor"] = "6"
        st, body2, sig2 = common.signed_get(p2)
        n2 = len(body2.get("aweme_list", []))
        case("A2 状态码 200", st == 200, "status=%s" % st)
        case("A2 返回 6 条", n2 == 6, "n=%d" % n2)
        case("A2 has_more=0（已到末页）", body2.get("has_more") == 0)
        case("A2 两页 ID 无重复", not (set(x["aweme_id"] for x in body.get("aweme_list", [])) &
                                       set(x["aweme_id"] for x in body2.get("aweme_list", []))))
        path2 = save_json("aweme_page2.json", body2)
        print("     第 2 页落盘: %s" % path2)

        # ---------- B 无签名 ----------
        print("\n--- B 反例：无签名 ---")
        st, body = common.get_no_sig(p1)
        case("B 无签名被拒 406", st == 406, "status=%s msg=%s" % (st, body.get("status_msg")))

        # ---------- C 伪造乱串 ----------
        print("\n--- C 反例：伪造乱串签名 ---")
        st, body = common.get_with_sig(p1, "A" * 164)
        case("C 乱串签名被拒 406", st == 406, "status=%s msg=%s" % (st, body.get("status_msg")))

        # ---------- D 篡改真签名 ----------
        print("\n--- D 反例：篡改真签名（改主体位 idx100）---")
        sig_d, _ = common.gen_sig(p2)
        tampered = sig_d[:100] + ("A" if sig_d[100] != "A" else "B") + sig_d[101:]
        st, body = common.get_with_sig(p2, tampered)
        case("D 篡改签名被拒 406", st == 406, "status=%s msg=%s" % (st, body.get("status_msg")))

        # ---------- E 重放第 1 页签名 ----------
        print("\n--- E 反例：重放第 1 页签名 ---")
        st, body = common.get_with_sig(p1, sig1)
        case("E 重放签名被拒 406", st == 406, "status=%s msg=%s" % (st, body.get("status_msg")))

        # ---------- F 健康检查 ----------
        print("\n--- F 健康检查 ---")
        st, body = common.get_health()
        wl = body.get("whitelist_size", -1)
        case("F 健康检查 200", st == 200, "status=%s" % st)
        case("F 白名单量级 19~40 位", 19 <= wl <= 40, "whitelist=%s（随机位+进程级副本位）" % wl)
        probe = body.get("probe", {})
        print("     探测摘要: samples=%s cost=%sms" % (probe.get("samples"), probe.get("cost_ms")))

    # ---------- 汇总 ----------
    n_pass = sum(1 for c in CASES if c["ok"])
    n_fail = len(CASES) - n_pass
    dur = round(time.time() - t0, 2)
    common.hr("汇总")
    print("  用例通过 %d / %d（耗时 %.2fs）" % (n_pass, len(CASES), dur))
    result = {
        "pass": n_pass, "total": len(CASES), "cost_s": dur,
        "signature_samples": {"page1": sig1[:20] + "...", "page2": sig2[:20] + "..."},
        "cases": CASES,
    }
    path = save_json("_pipeline_result.json", result)
    print("  结果落盘: %s" % path)
    common.hr("PIPELINE %s" % ("PASS" if n_fail == 0 else "FAIL"))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
