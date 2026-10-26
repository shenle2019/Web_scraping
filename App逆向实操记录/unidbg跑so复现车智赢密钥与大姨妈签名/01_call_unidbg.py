# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

Python 调用 unidbg 打包出来的 jar（day27 的"jar + Python 参数化调用"做法）。
Java 侧只负责跑 so，Python 侧负责传参、校验和留证。

用法：python 01_call_unidbg.py [--expect 期望密钥] [--out 结果日志]
"""
import argparse
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JAVA = r"C:\Program Files\Java\jdk-1.8\bin\java.exe"
WORKDIR = os.path.join(HERE, "unidbg", "unidbg-0.9.7")
JAR = "che-sign.jar"


def run_jar():
    p = subprocess.run([JAVA, "-jar", JAR], cwd=WORKDIR, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=600)
    return (p.stdout or "") + (p.stderr or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect", default="appapiche168comappapiche168comap")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    logs = []

    def log(line):
        line = line if isinstance(line, str) else str(line)
        print(line)
        logs.append(line)

    log("java = %s" % JAVA)
    log("cwd  = %s" % WORKDIR)
    out = run_jar()
    for line in out.splitlines():
        if line.startswith("[unidbg]"):
            log(line)
    m = re.search(r"get3desKey = (\S+)", out)
    key = m.group(1) if m else None
    log("解析出的 key = %r" % key)
    ok = bool(key) and re.fullmatch(r"[A-Za-z0-9]{24,32}", key) is not None
    if args.expect:
        log("与期望值比对：%s" % ("一致" if key == args.expect else "不一致（期望 %s）" % args.expect))
        ok = ok and key == args.expect
    log("结论：%s" % ("PASS Python 调用 unidbg 成功且结果稳定" if ok else "FAIL 调用失败或结果不符"))
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(logs) + "\n")
        print("已写入 %s" % os.path.abspath(args.out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
