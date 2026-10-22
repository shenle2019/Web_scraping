# -*- coding: utf-8 -*-
"""
用 Frida 拉起复刻 App、挂上 hook、点一次登录，把链路上每个方法的入参/出参打出来。
仅限学习研究，目标是自己编译的本地 App。
用法：python scripts/02_frida_hook.py
"""
import os
import subprocess
import sys
import time

import frida

PKG = "com.autohome.chezhiying.repl"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS_PATH = os.path.join(BASE, "scripts", "hook_sign.js")
LOG_PATH = os.path.join(BASE, "frida_hook.log")
TAP = ("540", "669")  # 登录按钮中心，竖屏


def main():
    with open(JS_PATH, encoding="utf-8") as fp:
        js = fp.read()

    lines = []

    def on_message(message, data):
        if message.get("type") == "send":
            line = str(message.get("payload", ""))
        elif message.get("type") == "log":
            line = str(message.get("payload", ""))
        elif message.get("type") == "error":
            line = "[error] " + message.get("stack", "")
        else:
            line = "[other] " + str(message)
        print(line, flush=True)
        lines.append(line)

    device = frida.get_usb_device(timeout=10)
    pid = device.spawn([PKG])
    session = device.attach(pid)
    script = session.create_script(js)
    script.on("message", on_message)
    script.load()
    device.resume(pid)
    time.sleep(4)

    subprocess.run(["adb", "shell", "input", "tap", TAP[0], TAP[1]], check=False)
    time.sleep(6)

    session.detach()
    with open(LOG_PATH, "w", encoding="utf-8") as out:
        out.write("\n".join(lines) + "\n")
    print("hook log -> %s (%d lines)" % (LOG_PATH, len(lines)))


if __name__ == "__main__":
    sys.exit(main())
