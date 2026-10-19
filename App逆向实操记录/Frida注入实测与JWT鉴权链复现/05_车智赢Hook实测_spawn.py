# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""车智赢 spawn 方案实测（对应课件 3-hook车智赢的密码-spawn方案.py）。

流程：spawn 包名 -> attach(pid) -> load hook -> resume(pid)，随后观察 15 秒。
课件原脚本用 sys.stdin.read() 挂住进程；这里改为定时观察并输出存活状态，
便于自动化记录结果。

实测结论（2026-10）：spawn 后 resume 成功返回，但 15 秒内进程退出（ALIVE False），
未收到任何 Java 层 hook 消息，同样与应用的 Frida 检测有关。
"""
import sys
import time

import frida

HOOK_JS = """
Java.perform(function () {
    var SecurityUtil = Java.use("com.autohome.ahkit.utils.SecurityUtil");
    SecurityUtil.encodeMD5.implementation = function (str) {
        console.log("[HOOK] encodeMD5 input=" + str);
        var res = this.encodeMD5(str);
        console.log("[HOOK] encodeMD5 output=" + res);
        return res;
    };
    console.log("[READY] hook installed in spawn mode");
});
"""


def main():
    rdev = frida.get_remote_device()
    pid = rdev.spawn(["com.che168.autotradercloud"])
    print("[SPAWN] pid=%s" % pid, flush=True)

    session = rdev.attach(pid)
    script = session.create_script(HOOK_JS)
    script.on("message", lambda msg, data: (print("[MSG]", msg), sys.stdout.flush()))
    script.load()
    rdev.resume(pid)
    print("[RESUME] app resumed, observing 15s...", flush=True)

    time.sleep(15)

    alive = False
    try:
        alive = any(p.pid == pid for p in rdev.enumerate_processes())
    except Exception as exc:
        print("[CHECK-ERR] %s" % exc, flush=True)
    print("[ALIVE-AFTER-15S] %s" % alive, flush=True)


if __name__ == "__main__":
    main()
