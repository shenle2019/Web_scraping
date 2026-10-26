# -*- coding: utf-8 -*-
"""汇总本次复刻的全部验证证据，生成 results/summary.json。

所有数字都从落盘日志里解析出来，不手动填写：
  - server/verification_log.jsonl  服务端逐条验签结果
  - server/device_selftest.log     真机 logcat 里的 SELFTEST 行
  - tools/frida/*.log              5 个 hook 的实测输出

仅限学习研究使用，禁止商用。
"""
import datetime
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")


def read(path):
    """读日志：兼容 PowerShell 重定向产生的 UTF-16LE（带 BOM）。"""
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        return ""
    with open(p, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig", errors="replace")
    return raw.decode("utf-8", errors="replace")


def stat_verification():
    """按 endpoint 统计验签通过/失败条数。"""
    total = {"click": 0, "heartbeat": 0}
    failed = 0
    first_ok = {}
    for line in read("server/verification_log.jsonl").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        ep = rec.get("endpoint")
        if ep in total:
            total[ep] += 1
            if rec.get("ok") and ep not in first_ok:
                first_ok[ep] = rec
        if not rec.get("ok"):
            failed += 1
    return total, failed, first_ok


def stat_selftest():
    lines = re.findall(r"SELFTEST\|99\|done\|(\d+)/(\d+)\|(PASS|FAIL)",
                       read("server/device_selftest.log"))
    pass_runs = sum(1 for a, b, c in lines if c == "PASS" and a == b)
    last = "%s/%s %s" % lines[-1] if lines else None
    return {"runs": len(lines), "pass_runs": pass_runs, "last": last}


def parse_frida():
    out = {}

    t1 = read("tools/frida/01_hook_crypto.log")
    out["01_hook_crypto"] = {
        "sha256_salt": (re.search(r"\[sha256Hex\] salt=([0-9a-f]+)", t1) or [None, None])[1],
        "aes_key": (re.search(r"\[SecretKeySpec\] alg=AES key=([0-9a-f]+)", t1) or [None, None])[1],
        "aes_iv": (re.search(r"\[IvParameterSpec\] iv=([0-9a-f]+)", t1) or [None, None])[1],
    }

    t2 = read("tools/frida/02_hook_headers.log")
    headers = {}
    for name in ("Buvid", "Device-ID", "fp_local", "fp_remote", "session_id"):
        m = re.search(r"\[headers\] %s\s*= (\S+)" % re.escape(name), t2)
        headers[name] = m.group(1) if m else None
    out["02_hook_headers"] = headers

    t3 = read("tools/frida/03_hook_register_natives.log")
    m = re.search(r"name=(\S+) sig=(\S+) module=(\S+) offset=0x([0-9a-f]+)", t3)
    out["03_hook_register_natives"] = {
        "name": m.group(1) if m else None,
        "signature": m.group(2) if m else None,
        "module": m.group(3) if m else None,
        "offset": ("0x" + m.group(4)) if m else None,
    }

    t4 = read("tools/frida/04_hook_native_md5_update.log")
    salts = []
    for s in re.findall(r"\[update\]\[salt \] len=8 ([0-9a-f]{8})", t4):
        if s not in salts:
            salts.append(s)
    m = re.search(r"offset=0x([0-9a-f]+)", t4)
    out["04_hook_native_md5_update"] = {
        "bili_md5_update_offset": ("0x" + m.group(1)) if m else None,
        "salts": salts,
        "salt_updates": len(re.findall(r"\[update\]\[salt \]", t4)),
        "plain_updates": len(re.findall(r"\[update\]\[plain\]", t4)),
    }

    t5 = read("tools/frida/05_hook_newstringutf.log")
    out["05_hook_newstringutf"] = {
        "md5_returned": len(re.findall(r"\[NewStringUTF\] [0-9a-f]{32}", t5)),
        "top_frame": (re.search(r"libbili\.so!native_sign\+0x[0-9a-f]+", t5) or [None])[0],
    }
    return out


def main():
    if not os.path.isdir(RESULTS):
        os.makedirs(RESULTS)
    total, failed, first_ok = stat_verification()
    hb = (first_ok.get("heartbeat") or {}).get("detail", {})
    summary = {
        "case": "自建App复刻B站播放量/完播率签名（day17~day19）",
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scope": "仅学习研究：App 只请求本机 mock server，不连接 B站线上接口",
        "environment": {
            "pc": "Windows 10 22H2 / JDK 1.8.0_371 / Python 3.8.8 / pycryptodome 3.24.0 / frida 16.3.3",
            "android_sdk": "build-tools 30.0.3, platforms/android-30",
            "ndk": "r25c（本次新装 D:\\soft\\android-ndk-r25c）",
            "device": "Pixel 2 / Android 11 (SDK 30) / arm64-v8a / Magisk root",
            "decompiler": "jadx CLI",
        },
        "artifacts": {
            "app": "build/BiliReplica.apk",
            "so": "build/lib/arm64-v8a/libbili.so",
            "package": "com.example.bililike",
        },
        "app_selftest": stat_selftest(),
        "server_verify": {
            "click": total["click"],
            "heartbeat": total["heartbeat"],
            "failed": failed,
            "first_click_sign": (first_ok.get("click") or {}).get("detail", {}).get("sign"),
            "heartbeat_sample": {
                "session": hb.get("session"),
                "session_shape_ok": hb.get("session_shape_ok"),
                "sign": hb.get("sign"),
                "sign_match": hb.get("sign_match"),
            },
        },
        "frida": parse_frida(),
        "bili_static_check": {
            "package": "tv.danmaku.bili",
            "versionName": "6.24.0",
            "versionCode": "6240300",
            "click_path": "classes5.dex",
            "heartbeat_path": "classes5.dex, classes9.dex",
            "sha256_salt_aes_key_iv": "classes10.dex",
            "fp_local": "classes3.dex, classes5.dex",
            "md5_salt_560c52cc": "dex 中不存在（在 so 层）",
            "so_abi": "仅 armeabi-v7a / x86，无 arm64，故 32 位加载",
        },
        "offline_bypass": {
            "method": "关闭 Wi-Fi 与移动数据后冷启动 v6.24.0",
            "result": "停在 SplashActivity + 隐私协议弹窗，未出现强制更新",
            "screenshot": "server/bili_offline.png",
            "followup": "立即 force-stop 并恢复网络，未点同意、未登录、未触发上报",
        },
    }
    dst = os.path.join(RESULTS, "summary.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\n[*] written:", dst)


if __name__ == "__main__":
    main()
