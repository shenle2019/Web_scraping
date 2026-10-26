# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

day30 扩展案例复刻：smali 修改 + 重打包 + 重签名 + 安装验证。
课件里用 MT 管理器在手机上改 smali，本脚本用命令行等价实现（思路完全一致）：
  1) 解出 classes.dex -> baksmali 反汇编成 smali
  2) 改 MainActivity$1.onClick 里的日志 TAG（"测试" -> "调试已修改"）
  3) smali 汇编回 dex -> 塞回 apk -> zipalign -> apksigner 重签名
  4) 卸载原签名版本 -> 安装改包 -> 点按钮 -> logcat 看到新 TAG 即通过

被测 App 是课件自带的 SoDebug 自建工程，不涉及线上账号。

用法：python 02_smali_patch.py [--out evidence_02_smali_patch.log]
"""
import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile

PKG = "com.nb.sodebug"
ACT = "com.nb.sodebug/com.nb.sodebug.MainActivity"
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_APK = (r"e:\路飞学城\课件\APP逆向(12期)\day31-动态调试-下\SoDebug"
           r"\app\build\outputs\apk\debug\app-debug.apk")
JADX_LIB = r"e:\路飞学城\课件\APP逆向(12期)\day01-开班\软件\jadx\jadx-1.4.1\lib"
# jadx 自带的是瘦 jar（无 Main-Class），需要把依赖一起放到 -cp 里，再指定 Main 类
SMALI_CP = ";".join(os.path.join(JADX_LIB, name) for name in [
    "baksmali-2.5.2.jar", "smali-2.5.2.jar", "dexlib2-2.5.2.jar", "util-2.5.2.jar",
    "guava-30.1.1-jre.jar", "failureaccess-1.0.1.jar", "jsr305-3.0.2.jar",
    "antlr-3.5.2.jar", "antlr-runtime-3.5.2.jar", "ST4-4.0.8.jar",
    "stringtemplate-3.2.1.jar", "jcommander-1.82.jar",
])
JAVA = r"C:\Program Files\Java\jdk-1.8\bin\java.exe"
KEYTOOL = r"C:\Program Files\Java\jdk-1.8\bin\keytool.exe"
BUILD_TOOLS = r"D:\AndroidSdk\build-tools\30.0.3"
ZIPALIGN = os.path.join(BUILD_TOOLS, "zipalign.exe")
APKSIGNER = os.path.join(BUILD_TOOLS, "apksigner.bat")
WORK = os.path.join(ROOT, "smali_work")
OLD_TAG = "测试"
# baksmali 会把非 ASCII 字符串转义成 \uXXXX，所以两种形式都要匹配
OLD_TAG_PATTERNS = [OLD_TAG, "\\u6d4b\\u8bd5"]
NEW_TAG = "PATCHED_BY_SMALI"
LOGS = []


def log(line=""):
    line = line if isinstance(line, str) else str(line)
    print(line)
    LOGS.append(line)


def run(cmd, cwd=None, timeout=180, env=None):
    log("[cmd] " + " ".join(cmd) if isinstance(cmd, list) else "[cmd] " + cmd)
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace", env=env, shell=isinstance(cmd, str))
    out = (p.stdout or "") + (p.stderr or "")
    for line in out.strip().splitlines()[-25:]:
        log("  " + line)
    return p.returncode, out


def adb(args, timeout=120):
    p = subprocess.run(["adb"] + args, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return (p.stdout or "") + (p.stderr or "")


def tap_by_text(text):
    for _ in range(3):
        adb(["shell", "uiautomator", "dump", "/sdcard/ui_smali.xml"])
        local = os.path.join(WORK, "ui_smali.xml")
        adb(["pull", "/sdcard/ui_smali.xml", local])
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(local)
        except Exception:
            time.sleep(1)
            continue
        for node in tree.iter("node"):
            if node.get("text") == text:
                x1, y1, x2, y2 = map(int, re.findall(r"\d+", node.get("bounds")))
                adb(["shell", "input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2)])
                return True
        time.sleep(1)
    return False


def repack(src, dst, new_dex, dex_name):
    """保持原压缩方式，只替换带着目标类的那个 dex，去掉旧签名文件。"""
    with zipfile.ZipFile(src) as zin:
        items = zin.infolist()
        with zipfile.ZipFile(dst, "w") as zout:
            for info in items:
                name = info.filename
                if name.startswith("META-INF/") and (name.endswith((".RSA", ".SF", ".MF", ".EC"))):
                    continue
                if name == dex_name:
                    continue
                data = zin.read(name)
                ctype = info.compress_type
                # targetSdk 30+ 要求 resources.arsc 不压缩存放
                if name == "resources.arsc":
                    ctype = zipfile.ZIP_STORED
                zout.writestr(zipfile.ZipInfo(name, info.date_time), data, compress_type=ctype)
            zout.writestr(zipfile.ZipInfo(dex_name, (2024, 11, 19, 22, 9, 26)),
                          open(new_dex, "rb").read(), compress_type=zipfile.ZIP_STORED)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="evidence_02_smali_patch.log")
    args = ap.parse_args()
    verdict = {}

    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    env = dict(os.environ)
    env["JAVA_HOME"] = r"C:\Program Files\Java\jdk-1.8"

    log("== 步骤 1：找到装着 App 自身类的 dex 并 baksmali 反汇编 ==")
    src = os.path.join(WORK, "sodebug_orig.apk")
    shutil.copy2(SRC_APK, src)
    dex_name = ""
    with zipfile.ZipFile(src) as z:
        dex_members = [n for n in z.namelist() if re.match(r"classes\d*\.dex$", n)]
        log("[1] apk 内 dex：%s" % ", ".join(dex_members))
        for name in dex_members:
            if b"Lcom/nb/sodebug/MainActivity;" in z.read(name):
                dex_name = name
                break
        log("[1] 目标类 Lcom/nb/sodebug/MainActivity; 在 %s" % dex_name)
        z.extract(dex_name, WORK)
    verdict["dex_located"] = bool(dex_name)
    if not dex_name:
        return report(args, verdict)
    dex_path = os.path.join(WORK, dex_name)
    log("[1] %s 大小 = %d" % (dex_name, os.path.getsize(dex_path)))
    smali_dir = os.path.join(WORK, "smali")
    rc, _ = run([JAVA, "-cp", SMALI_CP, "org.jf.baksmali.Main", "d", dex_path, "-o", smali_dir])
    verdict["baksmali_ok"] = rc == 0 and os.path.isdir(smali_dir)
    if not verdict["baksmali_ok"]:
        log("[!] baksmali 反汇编失败，结束")
        return report(args, verdict)

    log("")
    log("== 步骤 2：定位并修改 smali 中的日志 TAG ==")
    target = os.path.join(smali_dir, "com", "nb", "sodebug", "MainActivity$1.smali")
    text = io.open(target, encoding="utf-8").read()
    m = None
    for old in OLD_TAG_PATTERNS:
        m = re.search(r'const-string (v\d+), "%s"' % re.escape(old), text)
        if m:
            break
    log("[2] 命中的原指令：%s" % (m.group(0) if m else "未找到"))
    verdict["found_tag"] = bool(m)
    if m:
        patched = text.replace(m.group(0), 'const-string %s, "%s"' % (m.group(1), NEW_TAG), 1)
        io.open(target, "w", encoding="utf-8", newline="\n").write(patched)
        for line in patched.splitlines():
            if NEW_TAG in line or "Log;->e" in line:
                log("  [smali] " + line.strip())

    log("")
    log("== 步骤 3：smali 汇编回 dex ==")
    new_dex = os.path.join(WORK, "classes_patched.dex")
    rc, _ = run([JAVA, "-cp", SMALI_CP, "org.jf.smali.Main", "a", smali_dir, "-o", new_dex])
    verdict["smali_ok"] = rc == 0 and os.path.isfile(new_dex)
    log("[3] 新 dex 大小 = %d" % (os.path.getsize(new_dex) if os.path.exists(new_dex) else -1))

    log("")
    log("== 步骤 4：塞回 apk -> zipalign -> apksigner 重签名 ==")
    unsigned = os.path.join(WORK, "sodebug_unsigned.apk")
    repack(src, unsigned, new_dex, dex_name)
    aligned = os.path.join(WORK, "sodebug_aligned.apk")
    rc, _ = run([ZIPALIGN, "-f", "-p", "4", unsigned, aligned])
    verdict["zipalign_ok"] = rc == 0

    ks = os.path.join(WORK, "demo.keystore")
    if not os.path.exists(ks):
        run([KEYTOOL, "-genkeypair", "-keystore", ks, "-storepass", "android",
             "-keypass", "android", "-alias", "demo", "-keyalg", "RSA", "-keysize", "2048",
             "-validity", "3650", "-dname", "CN=Demo, OU=Study, O=Study, L=SH, S=SH, C=CN"])
    signed = os.path.join(WORK, "sodebug_signed.apk")
    rc, _ = run([APKSIGNER, "sign", "--ks", ks, "--ks-pass", "pass:android",
                 "--key-pass", "pass:android", "--out", signed, aligned], env=env)
    verdict["signed"] = rc == 0 and os.path.isfile(signed)
    if verdict["signed"]:
        run([APKSIGNER, "verify", "--print-certs", signed], env=env)

    log("")
    log("== 步骤 5：卸载原版 -> 安装改包 -> 点击按钮 -> 看 logcat ==")
    log(adb(["uninstall", PKG]).strip())
    log(adb(["install", "-r", "-t", "--no-incremental", signed]).strip())
    verdict["patched_installed"] = "package:" in adb(["shell", "pm", "path", PKG])
    adb(["logcat", "-c"])
    adb(["shell", "am", "force-stop", PKG])
    log(adb(["shell", "am", "start", "-n", ACT]).strip())
    time.sleep(4)
    verdict["tapped"] = tap_by_text("点我")
    time.sleep(3)
    cat = adb(["logcat", "-d", "-v", "brief"])
    hits = [ln for ln in cat.splitlines() if NEW_TAG in ln]
    for ln in hits[-5:]:
        log("[logcat] " + ln)
    verdict["new_tag_logged"] = any(NEW_TAG in ln and "3" in ln for ln in hits)

    return report(args, verdict)


def report(args, verdict):
    log("")
    log("== 判定 ==")
    for k, v in verdict.items():
        log("  %-22s %s" % (k, "PASS" if v else "FAIL"))
    log("总判定：%s" % ("PASS" if all(verdict.values()) else "FAIL"))

    with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(LOGS) + "\n")
    print("已写入 %s" % os.path.abspath(args.out))
    return 0 if all(verdict.values()) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
