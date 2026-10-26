# -*- coding: utf-8 -*-
"""抓一次干净的真机自检日志（避免 PowerShell 重定向写出 UTF-16）。

流程：清 logcat -> force-stop -> 冷启动 -> 等自检跑完 -> 导出 tag=BiliReplica 的行。

仅限学习研究使用，禁止商用。
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = "com.example.bililike"
OUT = os.path.join(ROOT, "server", "device_selftest.log")


def adb(*args):
    return subprocess.run(["adb"] + list(args), capture_output=True)


def main():
    adb("reverse", "tcp:8899", "tcp:8899")
    adb("logcat", "-c")
    adb("shell", "am", "force-stop", PKG)
    r = adb("shell", "am", "start", "-n", PKG + "/.MainActivity")
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode("utf-8", "replace"))
        return 1
    time.sleep(15)
    dump = adb("logcat", "-d", "-s", "BiliReplica:I")
    with open(OUT, "wb") as f:
        f.write(dump.stdout)
    text = dump.stdout.decode("utf-8", "replace")
    for line in text.splitlines():
        if "SELFTEST|99" in line or "SELFTEST|02" in line:
            print(line.strip())
    print("[*] written:", OUT, len(dump.stdout), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
