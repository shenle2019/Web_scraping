# -*- coding: utf-8 -*-
"""
对课件附带的真实车智赢 3.56.0 apk 做只读静态核验，产出 evidence/real_apk_static_verify.txt：
1) lib/arm64-v8a/libnative-lib.so 里 3DES 全量 key 与 JNI 导出符号的字节级偏移
2) classes*.dex 里四个签名盐值的明文命中情况（判断哪个 dex 装着 SignManager）
3) jadx 产物里 SignManager / SecurityUtil / AHAPIHelper 的关键行摘录

仅限学习研究，不修改、不重打包任何 apk，不向官方服务端发请求。
用法：python scripts/00_apk_static.py [apk路径]
"""
import glob
import hashlib
import io
import os
import sys
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_APK = r"E:\路飞学城\课件\APP逆向(12期)\day14-车智赢app\软件\车智赢-v3.56.0.apk"
OUT_PATH = os.path.join(BASE, "evidence", "real_apk_static_verify.txt")

KEY_FULL = b"appapiche168comappapiche168comap"
SALTS = {
    "KEY_V1": b"com.che168.www",
    "KEY_V2": b"W@oC!AH_6Ew1f6%8",
    "KEY_SHARE": b"moc.861ehc.relaed.bup.wyfv",
    "KEY_AUTOHOME": b"@7U$aPOE@$",
}
JNI_SYMBOLS = [
    b"Java_com_autohome_ahkit_jni_CheckSignUtil_get3desKey",
    b"Java_com_autohome_ahkit_jni_CheckSignUtil_checkState",
]

# jadx 产物里要摘录的关键文件（先找归档副本，再找工程里的反编译目录）
JADX_HINTS = [
    ("SignManager.java", ("KEY_", "signByType", "append(str)")),
    ("SecurityUtil.java", ("iv =", "encode3Des", "desede/CBC")),
    ("AHAPIHelper.java", ("getUDID", "nanoTime", "getDeviceId")),
    ("LaunchModel.java", ("lambda$initRequestCommonParams$0", "KEY_SIGN", "signByType")),
]


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_all(data, needle):
    offsets, start = [], 0
    while True:
        idx = data.find(needle, start)
        if idx < 0:
            return offsets
        offsets.append(idx)
        start = idx + 1


def context(data, offset, span=48):
    lo = max(0, offset - span)
    hi = min(len(data), offset + span)
    return data[lo:hi].decode("utf-8", "replace").replace("\x00", "\\0")


def locate_java(name):
    """关键类优先读 evidence/jadx_key_classes 下的归档副本，其次找 jadx 输出目录。"""
    direct = os.path.join(BASE, "evidence", "jadx_key_classes", name)
    if os.path.exists(direct):
        return direct
    for pattern in ("real_jadx/sources/**/" + name, "real_jadx1/sources/**/" + name):
        hits = glob.glob(os.path.join(BASE, pattern), recursive=True)
        if hits:
            return hits[0]
    return None


def main():
    apk = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_APK
    lines = []

    def out(text=""):
        lines.append(text)

    out("=== 目标 apk ===")
    out("path   : " + apk)
    out("size   : %d bytes" % os.path.getsize(apk))
    out("md5    : " + md5_of(apk))

    with zipfile.ZipFile(apk) as zf:
        names = zf.namelist()
        so_names = [n for n in names if n.startswith("lib/arm64-v8a/") and n.endswith(".so")]
        dex_names = sorted(n for n in names if n.startswith("classes") and n.endswith(".dex"))
        out("")
        out("=== apk 内容概览 ===")
        out("arm64 so 数量 : %d" % len(so_names))
        out("dex 文件      : " + ", ".join(dex_names))

        out("")
        out("=== lib/arm64-v8a/libnative-lib.so ===")
        so = zf.read("lib/arm64-v8a/libnative-lib.so")
        out("size : %d bytes" % len(so))
        hits = find_all(so, KEY_FULL)
        out("KEY_FULL(\"appapiche168comappapiche168comap\") 命中 %d 次，偏移 %s" % (len(hits), hits))
        for off in hits:
            out("  0x%06x 上下文: %s" % (off, context(so, off)))
        for sym in JNI_SYMBOLS:
            offs = find_all(so, sym)
            out("符号 %s : %s" % (sym.decode(), offs if offs else "未命中"))
        yes = find_all(so, b"yes")
        out("checkState 缓存常量 \"yes\" 偏移数量 : %d" % len(yes))
        out("前若干处: %s" % [hex(x) for x in yes[:8]])

        out("")
        out("=== classes*.dex 明文盐值命中 ===")
        for dex in dex_names:
            blob = zf.read(dex)
            found = [name for name, salt in SALTS.items() if salt in blob]
            full = KEY_FULL in blob
            if found or full:
                out("%-14s %s%s" % (dex, found, " + KEY_FULL" if full else ""))

    out("")
    out("=== jadx 产物关键行摘录 ===")
    for name, keywords in JADX_HINTS:
        path = locate_java(name)
        out("")
        out("--- %s ---" % name)
        if not path:
            out("(未找到归档副本与 jadx 产物，跳过)")
            continue
        out("source: %s" % os.path.relpath(path, BASE))
        with io.open(path, encoding="utf-8", errors="replace") as fp:
            for no, text in enumerate(fp, 1):
                if any(k in text for k in keywords):
                    out("%4d: %s" % (no, text.rstrip()))

    body = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with io.open(OUT_PATH, "w", encoding="utf-8") as fp:
        fp.write(body)
    print(body)
    print("报告 -> " + OUT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
