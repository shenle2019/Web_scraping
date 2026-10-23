# -*- coding: utf-8 -*-
"""Frida 驱动：解决 frida CLI 在非交互终端里 spawn 后立刻退出、脚本随之卸载的问题。

用法：
    python driver.py spawn  <script.js> [持续秒数]
    python driver.py attach <script.js> [持续秒数]

输出：脚本里的 console.log 会带 [script] 前缀实时打印，进程被反调试杀掉时打印 detached 原因。
仅限学习研究，禁止商用。
"""
import subprocess
import sys
import time

import frida

PKG = "com.repl.shihuo"


def adb_pid(serial, pkg):
    """用 adb 拿 pid，frida 的 get_process 按名称查新版本 Android 上不可靠。"""
    try:
        out = subprocess.check_output(
            ["adb", "-s", serial, "shell", "pidof", pkg],
            stderr=subprocess.DEVNULL,
        ).decode("utf-8", "ignore").strip()
        return int(out.split()[0]) if out else 0
    except Exception:
        return 0


def on_message(message, data):
    if message.get("type") == "log":
        print("[script] " + str(message.get("payload")), flush=True)
    elif message.get("type") == "send":
        print("[script-send] " + str(message.get("payload")), flush=True)
    elif message.get("type") == "error":
        print("[script-error] " + str(message.get("description")), flush=True)
    else:
        print("[script-other] " + str(message), flush=True)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    mode, script_path = sys.argv[1], sys.argv[2]
    duration = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
    pkg = sys.argv[4] if len(sys.argv) > 4 else PKG

    device = frida.get_usb_device(timeout=15)
    pid = None
    if mode == "spawn":
        pid = device.spawn([pkg])
        session = device.attach(pid)
        print("[driver] spawn %s pid=%d" % (pkg, pid), flush=True)
    else:
        # 新版 frida 枚举出来的进程名是应用 label（识货复刻），包名 attach 会找不到
        session = None
        for target in (pkg, PKG, "识货复刻", "识货"):
            try:
                session = device.attach(target)
                print("[driver] attach %s" % target, flush=True)
                break
            except frida.ProcessNotFoundError:
                continue
        if session is None:
            print("[driver] 找不到进程，请先启动 App", flush=True)
            return 2

    detached = {}

    def on_detached(reason, *args):
        detached["reason"] = str(reason)
        print("[driver] detached: %s" % reason, flush=True)

    session.on("detached", on_detached)

    with open(script_path, "r", encoding="utf-8") as fp:
        source = fp.read()
    script = session.create_script(source)
    script.on("message", on_message)
    script.load()
    print("[driver] script loaded: %s" % script_path, flush=True)

    if mode == "spawn":
        device.resume(pid)
        print("[driver] resumed", flush=True)

    time.sleep(duration)

    alive = bool(adb_pid(device.id, pkg))
    print("[driver] alive=%s detached=%s" % (alive, detached.get("reason")), flush=True)

    try:
        session.detach()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
