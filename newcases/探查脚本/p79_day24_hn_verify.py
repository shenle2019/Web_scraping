# -*- coding: utf-8 -*-
"""p79：Day24 课件（惠农网 huiNong）签名算法离线验证 —— Python 复刻路线
对照 p78（Node 原版路线）生成的 _day24_hn_node_result.json：
  1) 固定样本分段值 L/B/N/C15/D 与最终 sign 逐项比对
  2) 动态请求头（随机 nonce）输入下的 sign 复算比对
  3) Python 侧独立复核各字段格式断言
运行：python p79_day24_hn_verify.py
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NODE_RESULT = os.path.join(HERE, "_day24_hn_node_result.json")


def md5_hex(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def sha1_hex(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def sha384_hex(s):
    return hashlib.sha384(s.encode("utf-8")).hexdigest()


def compute_sign(nonce, timestamp, device_id, secret):
    """纯 Python 复刻课件 get_sign 算法，返回 (segments, sign)"""
    seg_l = md5_hex(nonce)                                 # L = MD5(nonce)
    seg_b = sha1_hex(timestamp)                            # B = SHA1(timestamp)
    seg_n = md5_hex(nonce + device_id)                     # N = MD5(nonce + deviceId)
    sha1_s = sha1_hex(secret + timestamp)                  # SHA1(secret + timestamp)
    seg_c = sha1_s[-16:-1]                                 # substring(len-16, len-1) 即后 15 位
    seg_d = str(int(seg_c, 16))                            # 15 位 hex -> 十进制大整数
    seg_f = "!".join([seg_l, seg_b, seg_n, seg_d])         # "!" 拼接
    return (
        {"L": seg_l, "B": seg_b, "N": seg_n, "C15": seg_c, "D": seg_d, "F": seg_f},
        sha384_hex(seg_f),                                 # sign = SHA384(F)
    )


def main():
    with open(NODE_RESULT, "r", encoding="utf-8") as f:
        node_data = json.load(f)

    print("=" * 72)
    print("p79 Python 复刻路线 —— 与 p78 Node 原版路线逐项对照")
    print("=" * 72)

    all_ok = True

    # ---------------- 1) 固定样本 ----------------
    fs = node_data["fixed_sample"]
    sample = fs["input"]
    node_seg = fs["segments_recomputed"]
    py_seg, py_sign = compute_sign(sample["nonce"], sample["timestamp"],
                                   sample["deviceId"], sample["secret"])
    print("\n[1] 固定样本（课件 get_sign 内硬编码样本）")
    print("    nonce=%s… timestamp=%s deviceId=%s" % (
        sample["nonce"][:8], sample["timestamp"], sample["deviceId"]))
    for k in ["L", "B", "N", "C15", "D"]:
        ok = py_seg[k] == node_seg[k]
        all_ok &= ok
        print("    %-4s 一致=%-5s py=%s" % (k, str(ok), py_seg[k]))
    ok_f = py_seg["F"] == node_seg["F"]
    all_ok &= ok_f
    print("    F    一致=%-5s (len=%d)" % (str(ok_f), len(py_seg["F"])))
    print("    Python sign =", py_sign)
    ok_sign = (py_sign == fs["sign_from_original_get_sign"]
               == fs["sign_from_segments"])
    all_ok &= ok_sign
    print("    三方 sign 一致（Python / 课件原版 get_sign / 分段复算）= %s" % ok_sign)

    # ---------------- 2) 动态请求头 ----------------
    dh = node_data["dynamic_header"]
    h = dh["header"]
    py_seg2, py_sign2 = compute_sign(h["X-CLIENT-NONCE"], h["X-CLIENT-TIME"],
                                     h["X-CLIENT-ID"], sample["secret"])
    print("\n[2] 动态请求头（课件 get_header 随机生成）")
    print("    nonce=%s… time=%s" % (h["X-CLIENT-NONCE"][:8], h["X-CLIENT-TIME"]))
    ok_dyn = (py_sign2 == h["X-Client-Sign"] == dh["sign_recomputed"])
    all_ok &= ok_dyn
    print("    动态输入复算 sign 一致（Python / 课件原版 header / Node 复算）= %s" % ok_dyn)

    # ---------------- 3) 格式断言（Python 侧独立复核） ----------------
    traceid = h["X-B3-TRACEID"]
    sid = h["X-CLIENT-SID"]
    checks = {
        "nonce 32hex": bool(re.fullmatch(r"[0-9a-f]{32}", h["X-CLIENT-NONCE"])),
        "nonce 保留位在 8-b": all(
            h["X-CLIENT-NONCE"][i] in "89ab" for i in dh["nonce_y_positions"]),
        "sign 96hex": bool(re.fullmatch(r"[0-9a-f]{96}", h["X-Client-Sign"])),
        "traceid 16位36进制": bool(re.fullmatch(r"[0-9A-Z]{16}", traceid)),
        "sid 格式 S_+16位": bool(re.fullmatch(r"S_[0-9A-Z]{16}", sid)),
    }
    ts_trace = int(traceid[:9], 36)
    ts_sid = int(sid[2:11], 36)
    ts_time = int(h["X-CLIENT-TIME"])
    checks["traceid 前9位可还原时间戳(±5s)"] = abs(ts_trace - ts_time) < 5000
    checks["sid 内嵌时间为 time-1000(±5s)"] = abs(ts_sid - (ts_time - 1000)) < 5000
    print("\n[3] Python 侧格式断言复核")
    for k, v in checks.items():
        all_ok &= v
        print("    %-34s %s" % (k, v))

    print("\n" + "=" * 72)
    print("最终结论：Python 复刻与 Node 原版双路线%s" % ("完全一致 [PASS]" if all_ok else "存在差异 [FAIL]"))
    print("=" * 72)


if __name__ == "__main__":
    main()
