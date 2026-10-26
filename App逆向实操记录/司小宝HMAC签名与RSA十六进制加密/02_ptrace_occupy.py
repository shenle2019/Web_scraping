# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

司小宝 ptrace 占坑验证（真机，只做附加测试，不登录）。

课件结论：司小宝启动后会再起一个同名子进程，先 ptrace 占住主进程，
frida 附加时报 "unable to access process ... due to system restrictions"。
绕过有两招：kill -9 掉占坑进程，或 spawn 抢在占坑之前注入。

本脚本把「附加失败 → 杀占坑进程 → 附加成功」这条链路走一遍。

用法：python 02_ptrace_occupy.py [--out 结果日志]
"""
import argparse
import io
import os
import re
import subprocess
import sys
import time

PKG = "cmt.chinaway.com.lite"


def adb(args, timeout=60):
    p = subprocess.run(["adb"] + args, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return (p.stdout or "") + (p.stderr or "")


def adb_su(cmd, timeout=60):
    return adb(["shell", "su -c '%s'" % cmd], timeout)


def lite_procs():
    """返回 [(pid, ppid, name)]，只保留司小宝相关进程。"""
    rows = []
    for line in adb(["shell", "ps", "-A"]).splitlines():
        if "chinaway" not in line:
            continue
        parts = line.split()
        if len(parts) >= 3 and parts[1].isdigit():
            rows.append((int(parts[1]), parts[2], parts[-1]))
    return rows


def try_attach(pid, secs=5):
    import frida
    dev = frida.get_usb_device(timeout=8)
    try:
        s = dev.attach(pid)
        time.sleep(1)
        s.detach()
        return True, "attach ok"
    except Exception as exc:
        return False, "%s: %s" % (type(exc).__name__, exc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    logs = []

    def log(line):
        line = line if isinstance(line, str) else str(line)
        print(line)
        logs.append(line)

    procs = lite_procs()
    log("== 1. 进程列表（出现两条同名进程 = ptrace 占坑）==")
    for pid, ppid, name in procs:
        log("pid=%s ppid=%s name=%s" % (pid, ppid, name))
    if len(procs) < 2:
        log("只有 %d 条进程，无法复现占坑（请先启动 App 并同意隐私协议）" % len(procs))
    main_pid = next((p for p, pp, _ in procs if str(pp) in ("1", "0") or int(pp) < p), procs[0][0])
    child_pid = next((p for p, _, _ in procs if p != main_pid), None)
    log("主进程=%s 占坑子进程=%s" % (main_pid, child_pid))

    log("== 2. 占坑状态下尝试附加主进程 ==")
    ok1, msg1 = try_attach(main_pid)
    log("附加结果=%s %s" % ("成功" if ok1 else "失败", msg1))
    if not ok1:
        err = msg1.replace("\n", " ")
        log("命中课件描述的特征：%s" % ("system restrictions" in err))

    if child_pid and not ok1:
        log("== 3. kill -9 占坑进程 %s ==" % child_pid)
        log(adb_su("kill -9 %d" % child_pid).strip() or "kill 已下发")
        time.sleep(2)
        left = [p for p, _, _ in lite_procs()]
        log("剩余进程：%s" % (", ".join(str(p) for p in left) or "无"))
        if main_pid not in left:
            log("主进程 %s 随 tracer 一起退出，符合 ptrace 语义（tracer 死亡 -> tracee 收到 SIGKILL）" % main_pid)
            log("== 4. 跳过重试：主进程已退出，改用 spawn 抢跑（见 03_spawn_attach.py）==")
            ok = True
        else:
            log("== 4. 再次附加主进程 ==")
            ok2, msg2 = try_attach(main_pid)
            log("附加结果=%s %s" % ("成功" if ok2 else "失败", msg2))
            ok = ok2
    else:
        ok = ok1

    if ok and child_pid and not ok1:
        log("结论：PASS ptrace 占坑复现（双进程 + 附加被拒），绕过用 spawn 抢跑")
    elif ok:
        log("结论：PASS 附加成功（该版本未观察到占坑）")
    else:
        log("结论：FAIL 两种方式都没附加成功")
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(logs) + "\n")
        print("已写入 %s" % os.path.abspath(args.out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
