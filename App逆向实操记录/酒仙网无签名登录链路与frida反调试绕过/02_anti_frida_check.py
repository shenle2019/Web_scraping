# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

酒仙网 frida 反调试验证：普通 frida-server vs hluda(strongR-frida) 的差异。

课件结论：酒仙会在运行期检测 frida 特征（进程名 / 线程名 / 端口 / 文件），
检测到就自杀或让 hook 失效；hluda 是打过反检测补丁的 frida-server，换掉就能 hook。

本脚本做两件事：
  1) 本地静态对比两个二进制里的 frida 特征字符串（gum-js-loop / re.frida.server 等）
  2) 设备上分别用 frida-server / hluda 对酒仙 spawn + 注入脚本，看进程是否存活、脚本是否执行
     普通 frida-server 用系统 python(frida 16.3.3)，hluda 用 frida1621 venv(frida 16.2.1)

用法：
  python 02_anti_frida_check.py static
  python 02_anti_frida_check.py device --mode frida
  python 02_anti_frida_check.py device --mode hluda
"""
import argparse
import os
import re
import subprocess
import sys
import time

PKG = "com.jiuxianapk.ui"
HLUDA_LOCAL = "hluda-server-16.2.1-android-arm64"
MARKS = [b"gum-js-loop", b"re.frida.server", b"linjector", b"frida-server", b"pool-spawner"]

SCR = """
setImmediate(function () {
    Java.perform(function () {
        var n = Java.enumerateLoadedClassesSync().length;
        send({tag: "hook", msg: "loaded classes = " + n});
    });
});
"""


def adb(args, timeout=60):
    """直接以参数列表调 adb，避免 Windows cmd 吃掉单引号和管道符。"""
    p = subprocess.run(["adb"] + args, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return (p.stdout or "") + (p.stderr or "")


def adb_su(cmd, timeout=60):
    return adb(["shell", "su -c '%s'" % cmd], timeout)


def find_procs():
    """拉全量进程表，在本地过滤，避免设备端 grep 依赖。"""
    out = adb(["shell", "ps", "-A"])
    return [ln for ln in out.splitlines() if "frida" in ln or "hluda" in ln]


def static_check():
    print("== 1. 二进制特征字符串对比 ==")
    targets = [HLUDA_LOCAL]
    for extra in [r"..\..\_tmp_day05_repl\frida-server-16.3.3-android-arm64",
                  r"..\..\_tmp_day22\frida-server-16.3.3-android-arm64"]:
        if os.path.exists(extra):
            targets.append(extra)
    for path in targets:
        data = open(path, "rb").read()
        counts = {m.decode(): data.count(m) for m in MARKS}
        print("%-46s %s" % (os.path.basename(path), counts))
    print("说明：hluda 里 gum-js-loop / re.frida.server 这些常见检测点已被抹掉，frida-server 里还在。")


def device_check(mode):
    print("== 2. 设备侧验证 mode=%s ==" % mode)
    adb(["push", HLUDA_LOCAL, "/data/local/tmp/hluda"], timeout=180)
    adb_su("chmod 777 /data/local/tmp/hluda")
    adb_su("pkill -f frida-server")
    adb_su("pkill -f hluda")
    time.sleep(1)
    if mode == "hluda":
        adb_su("nohup /data/local/tmp/hluda -D >/dev/null 2>&1 &")
    else:
        adb_su("nohup /data/local/tmp/frida-server -D >/dev/null 2>&1 &")
    time.sleep(4)
    procs = find_procs()
    print("进程：\n%s" % ("\n".join(procs).strip() or "(未发现 frida/hluda 进程)"))

    import frida
    print("客户端 frida 版本：%s" % frida.__version__)
    dev = frida.get_usb_device(timeout=10)
    pid = dev.spawn([PKG])
    print("spawn ok, pid=%s" % pid)
    session = dev.attach(pid)
    script = session.create_script(SCR)
    got = {"hook": False}

    def on_message(msg, data):
        print("消息：", msg)
        if msg.get("type") == "send":
            got["hook"] = True

    script.on("message", on_message)
    script.load()
    dev.resume(pid)
    time.sleep(6)
    alive = adb(["shell", "pidof", PKG]).strip()
    print("6 秒后进程：%r" % alive)
    ok = bool(alive) and got["hook"]
    print("结论：%s" % ("PASS hook 生效且进程存活" if ok else "FAIL 被反调试干掉或 hook 未执行"))
    try:
        session.detach()
    except Exception:
        pass
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["static", "device"])
    ap.add_argument("--mode", default="hluda", choices=["frida", "hluda"])
    args = ap.parse_args()
    if args.action == "static":
        static_check()
    else:
        device_check(args.mode)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
