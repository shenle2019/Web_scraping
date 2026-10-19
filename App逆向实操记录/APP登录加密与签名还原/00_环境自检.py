# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""day05 复刻环境自检：本机工具 + 手机端工具 + 三款 APP 版本。

手机需已用 USB 连接并开启 adb 调试，frida-server 已启动。
"""
import os
import subprocess
import sys

PACKAGES = [
    ("com.iqilu.app137", "爱安丘", "1.0.5"),
    ("com.uulife.medical.activity", "尿大夫", "4.1.11.230417"),
    ("com.yltx.oil.partner", "合伙人", "1.4"),
]


def run(cmd):
    """执行命令并返回 (退出码, 输出)，不抛异常。"""
    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        out, _ = proc.communicate(timeout=25)
        return proc.returncode, out.decode("utf-8", "ignore").strip()
    except Exception as exc:
        return -1, "<执行失败: %s>" % exc


def check(label, ok, detail=""):
    print("[%s] %s%s" % ("OK" if ok else "!!", label, ("  " + detail) if detail else ""))
    return ok


def main():
    print("=" * 72)
    print("day05 反编译案例 - 环境自检")
    print("=" * 72)
    all_ok = True

    code, out = run("adb devices")
    lines = [line for line in out.splitlines() if line.strip() and "List of devices" not in line]
    devices = [line for line in lines if "\tdevice" in line]
    all_ok &= check("adb 设备", bool(devices), devices[0] if devices else out)

    if not devices:
        print("\n未发现设备，后续检查跳过。请连接手机并开启 USB 调试。")
        return 1

    code, out = run("adb shell getprop ro.product.model")
    code2, out2 = run("adb shell getprop ro.build.version.release")
    check("手机型号 / Android", bool(out), "%s / Android %s" % (out, out2))

    # frida-server 进程可能被系统隐藏，直接通过 frida 枚举进程更可靠
    try:
        import frida

        procs = frida.get_remote_device().enumerate_processes()
        all_ok &= check("frida-server 可用", True, "枚举到 %d 个进程" % len(procs))
    except Exception as exc:
        all_ok &= check("frida-server 可用", False, str(exc))
        print("   启动命令：adb shell su -c 'nohup /data/local/tmp/frida-server >/dev/null 2>&1 &'")

    code, out = run("adb forward --list")
    all_ok &= check("adb 端口转发", "27042" in out and "27043" in out, out or "无")

    code, out = run("frida --version")
    all_ok &= check("本机 frida", code == 0, out)

    for path in [r"D:\soft\jadx\jadx-gui-1.4.7.exe", r"D:\soft\jadx-cli\bin\jadx.bat"]:
        check("jadx: %s" % path, os.path.exists(path))

    print("-" * 72)
    print("目标 APP 安装情况")
    installed = 0
    for pkg, name, expect in PACKAGES:
        code, out = run("adb shell dumpsys package %s" % pkg)
        versions = [line.strip() for line in out.splitlines() if "versionName=" in line]
        version = versions[0].split("versionName=")[-1] if versions else "未安装"
        ok = expect in version
        installed += 1 if ok else 0
        check("%s (%s)" % (name, pkg), ok, "期望 %s，实际 %s" % (expect, version))

    print("-" * 72)
    if installed == len(PACKAGES):
        print("三款 APP 均为课件版本，未升级。")
    else:
        print("存在版本不一致的 APP，请安装课件 APK，勿升级到最新版。")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
