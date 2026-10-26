# -*- coding: utf-8 -*-
"""Frida 运行器：spawn 目标 App -> 加载 hook 脚本 -> 等自检跑完 -> 落盘日志。

仅限学习研究使用。目标是自己构建的 com.example.bililike，不涉及任何线上应用。

用法:
    python run_hook.py 04_hook_native_md5_update.js --seconds 15
"""
import argparse
import os
import sys
import time

import frida

PKG = "com.example.bililike"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--seconds", type=int, default=15)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    script_path = os.path.abspath(args.script)
    out_path = args.out
    # 先攒内存，结束时一次性落盘：
    # Frida 的消息回调跑在独立线程，若在回调里直接写文件，
    # 主线程 kill 进程时容易丢掉未 flush 的内容。
    buf = []

    def log(line):
        buf.append(line)
        try:
            print(line)
        except Exception:
            # 控制台编码异常不能影响日志收集
            print(line.encode("ascii", "replace").decode("ascii"))
        sys.stdout.flush()

    device = frida.get_usb_device(timeout=10)
    pid = device.spawn([PKG])
    session = device.attach(pid)

    with open(script_path, "r", encoding="utf-8") as f:
        source = f.read()
    script = session.create_script(source)

    def on_message(message, data):
        if message.get("type") == "send":
            log(str(message.get("payload")))
        elif message.get("type") == "error":
            log("[script-error] " + message.get("stack", message.get("description", "")))

    # 注意：frida-python 的 type=log 消息只走 log handler，不会 emit message 事件，
    # 必须用 set_log_handler 才能收到 console.log 的内容。
    script.on("message", on_message)
    script.set_log_handler(lambda level, text: log(text))
    script.load()
    device.resume(pid)
    log("[*] spawned %s pid=%d, script=%s" % (PKG, pid, os.path.basename(script_path)))
    time.sleep(args.seconds)

    # 先落盘再 kill：kill 之后 Frida 会话断开，回调线程里未处理的消息会丢
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(buf) + "\n")

    try:
        device.kill(pid)
    except Exception:
        pass

    print("[*] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
