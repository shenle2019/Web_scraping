# -*- coding: utf-8 -*-
"""
20：爬虫主流程 —— 补环境 JSVMP 签名链路（端到端）
=========================================================
流程（全本地闭环，无任何真实站点请求）：
  1. 启动本地 mock 站（10_mock_server.py，端口 18999）
  2. 调 Node 签名引擎（02_xhs_sign_cli.js = 补环境 01 + JSVMP js_asset/source.js）
     生成 X-s / X-t（模拟"爬虫客户端"）
  3. 用签名请求 mock 站 homefeed 接口，验证 200 + 落盘数据到 output/
  4. 反例断言（服务端三层风控）：
       B 无签名            -> 406（缺少 X-s 签名头）
       C 伪造结构合法签名   -> 406（指纹不在合法库）
       D 签名过期（改旧 X-t）-> 406（超出时间窗）
  5. 汇总 PASS/FAIL，落盘 output/_pipeline_result.json

运行：
  python run_log.py 20_spider_pipeline.txt -- python 20_spider_sign_pipeline.py
"""
import base64
import json
import os
import time

import pw_common as C

OUT_DIR = os.path.join(C.BASE, "output")


def save_json(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    fp = os.path.join(OUT_DIR, name)
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print("  [落盘] %s" % fp)
    return fp


def main():
    C.hr("20 爬虫主流程：补环境签名 -> 请求本地 mock 站（端到端）")
    results = []

    with C.LocalSite():
        # ---------- 用例 A：正常流（真实签名） ----------
        print("\n--- 用例 A：Node 补环境引擎签名 -> 请求 mock 站 ---")
        t0 = time.time()
        sig = C.node_sign(C.API_PATH, C.COURSE_BODY)
        wall_ms = (time.time() - t0) * 1000.0
        print("  签名成功: X-s=%s... (len=%d)" % (sig["X-s"][:24], len(sig["X-s"])))
        print("  X-t=%s | 进程内签名耗时=%.3f ms | 含进程启动墙钟=%.0f ms"
              % (sig["X-t"], sig["cost_ms"], wall_ms))

        status, resp = C.post_signed(C.COURSE_BODY, xs=sig["X-s"], xt=sig["X-t"])
        ok_a = (status == 200 and resp.get("success") is True)
        results.append(C.check("A 正常流：真实签名 + 紧凑 JSON -> 200", ok_a))
        print("  HTTP %s | total=%s | 首条=《%s》"
              % (status, (resp.get("data") or {}).get("total"),
                 ((resp.get("data") or {}).get("items") or [{}])[0].get("title", "")))
        if ok_a:
            save_json("homefeed_page1.json", {
                "path": C.API_PATH,
                "request_body": C.COURSE_BODY,
                "X-s_head": sig["X-s"][:32] + "...",
                "X-t": sig["X-t"],
                "sign_cost_ms": sig["cost_ms"],
                "sign_wall_ms": round(wall_ms, 1),
                "response": resp,
            })

        # ---------- 用例 B：无签名 ----------
        print("\n--- 用例 B：不带签名头 ---")
        status_b, resp_b = C.post_signed(C.COURSE_BODY)
        results.append(C.check("B 无签名 -> 406（%s）" % resp_b.get("msg"), status_b == 406))

        # ---------- 用例 C：伪造结构合法签名 ----------
        print("\n--- 用例 C：伪造结构合法签名（payload 全 0） ---")
        fake_obj = {"signSvn": "51", "signType": "x1", "appId": "xhs-pc-web", "payload": "0" * 384}
        fake_xs = "XYW_" + base64.b64encode(
            json.dumps(fake_obj, separators=(",", ":")).encode("utf-8")).decode("ascii")
        status_c, resp_c = C.post_signed(C.COURSE_BODY, xs=fake_xs, xt=int(time.time() * 1000))
        results.append(C.check("C 伪造指纹 -> 406（%s）" % resp_c.get("msg"), status_c == 406))

        # ---------- 用例 D：签名过期 ----------
        print("\n--- 用例 D：真签名但 X-t 改为 10 分钟前 ---")
        old_xt = int(time.time() * 1000) - 600000
        status_d, resp_d = C.post_signed(C.COURSE_BODY, xs=sig["X-s"], xt=old_xt)
        results.append(C.check("D 签名过期 -> 406（%s）" % resp_d.get("msg"), status_d == 406))

    # ---------- 汇总 ----------
    passed = sum(1 for r in results if r)
    print("\n" + "=" * 64)
    print("20 结论: %d PASS / %d FAIL" % (passed, len(results) - passed))
    print("=" * 64)
    save_json("_pipeline_result.json", {
        "passed": passed,
        "total": len(results),
        "all_ok": passed == len(results),
        "ran_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
