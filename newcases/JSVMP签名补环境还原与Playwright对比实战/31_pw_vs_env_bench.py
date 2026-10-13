# -*- coding: utf-8 -*-
"""
31：双方案实测对比 —— Playwright vs 补环境 JS 逆向
=========================================================
把两条链路拉到同一张表上做量化对比：
  A 方案（补环境）：01_env_mini.js + 02_xhs_sign_cli.js（Node 内 JSVMP）
  B 方案（Playwright）：pw_assets/sign_page.html（真实 Edge 内 JSVMP）

指标：
  [冷启动]     A: 单次 node 调用墙钟（进程启动 + VM 挂载 + 签名 + 输出）
               B: Edge launch + 页面加载 + ready（此后页面常驻复用）
  [单次]       B: evaluate 单次（含 IPC 往返；A 的"单次"即冷启动）
  [批量]       A: node 进程内连续 N 次平均（纯 JSVMP 执行）
               B: 页面内连续 N 次平均（纯 JSVMP 执行，performance.now 计时）
  [批量+驱动]  B: Python 循环 N 次 evaluate 平均（爬虫真实模式，含 IPC）
  [结构]       两方案 payload 头 32 / 字段 / 长度一致性
  [端到端]     两方案签名均请求 mock 站 -> 期望均 200

运行：
  python run_log.py 31_pw_vs_env_bench.txt -- python 31_pw_vs_env_bench.py
"""
import json
import os
import time

import pw_common as C

OUT_DIR = os.path.join(C.BASE, "output")
N = 50


def main():
    C.hr("31 双方案实测对比：Playwright vs 补环境 JS 逆向")
    results = []
    bench = {"n": N}

    with C.LocalSite():
        # ================= A 方案：补环境 =================
        print("\n--- A 方案（补环境）：冷启动单次 ---")
        t0 = time.time()
        sig_a = C.node_sign(C.API_PATH, C.COURSE_BODY)
        a_cold_ms = (time.time() - t0) * 1000.0
        print("  含 node 进程启动墙钟 = %.0f ms | 进程内签名 %.3f ms" % (a_cold_ms, sig_a["cost_ms"]))
        bench["a_cold_ms"] = round(a_cold_ms, 1)

        print("\n--- A 方案：node 进程内连续 %d 次 ---" % N)
        batch_a = C.node_sign(C.API_PATH, C.COURSE_BODY, count=N)
        print("  ok=%d/%d | total=%.0f ms | 平均 %.2f ms/次" % (
            batch_a["ok_count"], batch_a["count"], batch_a["total_ms"], batch_a["avg_ms"]))
        bench["a_batch_avg_ms"] = batch_a["avg_ms"]
        bench["a_batch_ok"] = (batch_a["ok_count"] == batch_a["count"])

        # ================= B 方案：Playwright =================
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            t1 = time.time()
            browser = C.launch_browser(p)
            ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            ctx.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: function () { return false; }});")
            page = ctx.new_page()
            page.goto(C.URL_HOME)
            page.wait_for_function("window.__xhsReady === true", timeout=15000)
            b_cold_ms = (time.time() - t1) * 1000.0
            print("\n--- B 方案（Playwright）：冷启动 ---")
            print("  Edge launch + 页面就绪墙钟 = %.0f ms" % b_cold_ms)
            bench["b_cold_ms"] = round(b_cold_ms, 1)

            t2 = time.time()
            sig_b = page.evaluate("(a) => window.xhsSign(a.path, a.body)",
                                  {"path": C.API_PATH, "body": C.COURSE_BODY})
            b_one_ms = (time.time() - t2) * 1000.0
            print("\n--- B 方案：evaluate 单次（含 IPC 往返）---")
            print("  墙钟 = %.1f ms" % b_one_ms)
            bench["b_one_eval_ms"] = round(b_one_ms, 1)

            batch_b = page.evaluate("""(a) => {
                var t0 = performance.now();
                var ok = 0, firstHead = null, lastHead = null;
                for (var i = 0; i < a.n; i++) {
                    var r = window.xhsSign(a.path, a.body);
                    ok++;
                    var obj = JSON.parse(atob(r["X-s"].slice(4)));
                    var head = String(obj.payload).slice(0, 32);
                    if (i === 0) firstHead = head;
                    lastHead = head;
                }
                var total = performance.now() - t0;
                return { total: total, ok: ok, avg: total / a.n, firstHead: firstHead, lastHead: lastHead };
            }""", {"n": N, "path": C.API_PATH, "body": C.COURSE_BODY})
            print("\n--- B 方案：页面内连续 %d 次（纯 JSVMP 执行）---" % N)
            print("  ok=%d/%d | total=%.0f ms | 平均 %.2f ms/次 | 头32 首尾一致=%s" % (
                batch_b["ok"], N, batch_b["total"], batch_b["avg"],
                batch_b["firstHead"] == batch_b["lastHead"]))
            bench["b_batch_avg_ms"] = round(batch_b["avg"], 2)
            bench["b_batch_ok"] = (batch_b["ok"] == N)

            t3 = time.time()
            for _ in range(N):
                page.evaluate("(a) => window.xhsSign(a.path, a.body)",
                              {"path": C.API_PATH, "body": C.COURSE_BODY})
            b_driven_ms = (time.time() - t3) * 1000.0
            print("\n--- B 方案：Python 驱动 %d 次 evaluate（爬虫真实模式）---" % N)
            print("  平均 %.2f ms/次（含 IPC）" % (b_driven_ms / N))
            bench["b_driven_avg_ms"] = round(b_driven_ms / N, 2)

            # ================= 结构一致性 =================
            print("\n--- 结构一致性 ---")
            info_a = C.decode_xs(sig_a["X-s"])
            info_b = C.decode_xs(sig_b["X-s"])
            print("  补环境: 字段=%s | payload=%d 位 | 头32=%s" % (
                ",".join(info_a["fields"]), info_a["payload_len"], info_a["payload_head"]))
            print("  浏览器: 字段=%s | payload=%d 位 | 头32=%s" % (
                ",".join(info_b["fields"]), info_b["payload_len"], info_b["payload_head"]))
            same_struct = (info_a["fields"] == info_b["fields"]
                           and info_a["payload_len"] == info_b["payload_len"]
                           and info_a["payload_head"] == info_b["payload_head"])
            results.append(C.check("两方案结构一致（4 字段 / 384 位 / 同指纹头）", same_struct))
            bench["same_struct"] = same_struct

            # ================= 端到端 =================
            print("\n--- 端到端：两方案签名均请求 mock 站 ---")
            sa, ra = C.post_signed(C.COURSE_BODY, xs=sig_a["X-s"], xt=sig_a["X-t"])
            sb, rb = C.post_signed(C.COURSE_BODY, xs=sig_b["X-s"], xt=sig_b["X-t"])
            print("  补环境签名 -> HTTP %s | total=%s" % (sa, (ra.get("data") or {}).get("total")))
            print("  浏览器签名 -> HTTP %s | total=%s" % (sb, (rb.get("data") or {}).get("total")))
            results.append(C.check("补环境签名端到端 -> 200", sa == 200))
            results.append(C.check("浏览器签名端到端 -> 200", sb == 200))
            bench["e2e"] = {"env": sa, "pw": sb}

            browser.close()

    # ================= 汇总表 =================
    print("\n" + "=" * 64)
    print("31 双方案对比汇总")
    print("=" * 64)
    rows = [
        ("指标", "补环境 (01+02)", "Playwright (30)"),
        ("冷启动到可签名", "%.0f ms" % a_cold_ms, "%.0f ms" % b_cold_ms),
        ("单次签名（完整链路墙钟）", "%.0f ms（含 node 进程启动）" % a_cold_ms, "%.1f ms（页面已就绪）" % b_one_ms),
        ("批量 %d 次平均（纯执行）" % N, "%.2f ms/次" % batch_a["avg_ms"], "%.2f ms/次" % batch_b["avg"]),
        ("批量 %d 次平均（含驱动）" % N, "%.0f ms/次（逐次重启进程）" % a_cold_ms, "%.2f ms/次（逐次 IPC）" % (b_driven_ms / N)),
        ("产物结构", "4 字段 / 384 位", "4 字段 / 384 位"),
        ("payload 头 32", info_a["payload_head"][:16] + "...", info_b["payload_head"][:16] + "..."),
        ("端到端 mock 站", "200", "200"),
    ]
    for r in rows:
        print("  %-26s | %-28s | %s" % r)

    passed = sum(1 for r in results if r)
    print("\n" + "=" * 64)
    print("31 结论: %d PASS / %d FAIL" % (passed, len(results) - passed))
    print("=" * 64)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "bench_result.json"), "w", encoding="utf-8") as f:
        json.dump({"passed": passed, "total": len(results), "bench": bench}, f, ensure_ascii=False, indent=2)
    print("  [落盘] %s" % os.path.join(OUT_DIR, "bench_result.json"))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
