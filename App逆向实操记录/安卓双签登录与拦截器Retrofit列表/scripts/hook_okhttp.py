# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

把 hook_okhttp.js 注入到已运行的 App，实时打印 OkHttp 真正发出的请求头与表单体。
用法：
    python hook_okhttp.py                 # 默认连 127.0.0.1:27043（adb forward 出来的口）
    python hook_okhttp.py --host usb       # 直连 USB 上的 frida-server
    python hook_okhttp.py --seconds 25    # 采集 25 秒后退出
需要：电脑端 frida（16.3.3）+ 手机端 frida-server 已启动。
"""
import argparse
import os
import subprocess
import sys
import time

import frida

JS_PATH = "hook_okhttp.js"


def adb_binary():
    """adb 不一定在 PATH 里，按常见安装位置兜底。"""
    env = os.environ.get("ADB")
    if env:
        return env
    guess = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Android", "Sdk", "platform-tools", "adb.exe")
    return guess if os.path.exists(guess) else "adb"


def resolve_pid(package, adb):
    """remote 设备上按包名 attach 会挂住，先用 adb 拿 pid 再 attach(pid) 更稳。"""
    out = subprocess.run([adb, "shell", "pidof", package],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         universal_newlines=True).stdout.strip()
    if not out:
        raise SystemExit("App 未运行，先启动一次：%s" % package)
    return int(out.split()[0])


def open_device(host):
    """host=usb 走 adb 直连；否则按 host:port 连（先 adb forward tcp:27043 tcp:27043）。"""
    if host == "usb":
        return frida.get_usb_device(timeout=15)
    device = frida.get_device_manager().add_remote_device(host)
    device.enumerate_processes()          # 预热一次，连不上会立刻报错
    return device


def on_message(message, data):
    if message.get("type") == "send":
        print(message["payload"])
    elif message.get("type") == "error":
        print("[js-error] " + message.get("stack", message.get("description", "")))
    else:
        print("[msg] " + str(message))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", default="com.shenjiahang.netapp")
    parser.add_argument("--host", default="127.0.0.1:27043")
    parser.add_argument("--seconds", type=int, default=30)
    args = parser.parse_args()

    device = open_device(args.host)
    print("[*] device:", device)

    pid = resolve_pid(args.package, adb_binary())
    print("[*] pid:", pid)
    session = device.attach(pid)
    print("[*] attached:", args.package)

    with open(JS_PATH, "r", encoding="utf-8") as f:
        source = f.read()

    script = session.create_script(source)
    script.on("message", on_message)
    script.load()
    print("[*] hook loaded, 请在手机上点一次登录 / 进列表页，%ds 后自动退出" % args.seconds)

    time.sleep(args.seconds)
    session.detach()
    print("[*] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
