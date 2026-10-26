# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

司小宝 ptrace 占坑绕过方案二：spawn 抢跑。
先让 frida 把进程挂起在 zygote fork 之后、App 代码运行之前，注入脚本后再 resume，
占坑进程还没起来，附加就已经完成。

用法：python 03_spawn_attach.py [--out 结果日志]
"""
import argparse
import io
import os
import subprocess
import sys
import time

PKG = "cmt.chinaway.com.lite"
SCR = """
setImmediate(function () {
    Java.perform(function () {
        send({tag: "hook", msg: "loaded classes = " + Java.enumerateLoadedClassesSync().length});
    });
});
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    logs = []

    def log(line):
        line = line if isinstance(line, str) else str(line)
        print(line)
        logs.append(line)

    subprocess.run(["adb", "shell", "am", "force-stop", PKG], capture_output=True)
    import frida
    dev = frida.get_usb_device(timeout=8)
    pid = dev.spawn([PKG])
    log("spawn pid=%s" % pid)
    session = dev.attach(pid)
    script = session.create_script(SCR)
    got = []
    script.on("message", lambda m, d: (log("消息：%s" % m), got.append(m)))
    script.load()
    dev.resume(pid)
    time.sleep(6)
    alive = subprocess.run(["adb", "shell", "pidof", PKG], capture_output=True,
                           text=True).stdout.strip()
    log("6 秒后进程：%r" % alive)
    ok = bool(alive) and bool(got)
    log("结论：%s" % ("PASS spawn 抢跑注入成功" if ok else "FAIL 注入未生效或进程被杀"))
    try:
        session.detach()
    except Exception:
        pass
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(logs) + "\n")
        print("已写入 %s" % os.path.abspath(args.out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
