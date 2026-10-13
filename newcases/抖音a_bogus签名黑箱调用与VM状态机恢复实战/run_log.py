# -*- coding: utf-8 -*-
"""
run_log.py —— 运行脚本并把 UTF-8 输出记录到 _run_*.txt
=========================================================
用法：
  python run_log.py 03_sign_selftest.txt -- node 03_sign_selftest.js
  python run_log.py 20_spider_sign_pipeline.txt -- python 20_spider_sign_pipeline.py

说明：Windows 终端直接重定向（`*>`）得到的是 UTF-16LE 文本，入库会乱码；
本工具统一用 Python subprocess 捕获并按 UTF-8 落盘，日志文件名自动加 _run_ 前缀。
"""
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))


def main():
    if "--" not in sys.argv or len(sys.argv) < 4:
        print("用法: python run_log.py <日志名.txt> -- <命令...>")
        return 2
    idx = sys.argv.index("--")
    log_name = sys.argv[1]
    cmd = sys.argv[idx + 1:]
    if not log_name.startswith("_run_"):
        log_name = "_run_" + log_name
    log_path = os.path.join(BASE, log_name)

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, cwd=BASE, env=env)
    dur = time.time() - t0

    out = r.stdout.decode("utf-8", errors="replace")
    err = r.stderr.decode("utf-8", errors="replace")
    body = out
    if err.strip():
        body += "\n[stderr]\n" + err
    body += "\n[exit=%d, %.2fs]" % (r.returncode, dur)

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(body)
    print("日志已写入: %s (exit=%d, %.2fs)" % (log_path, r.returncode, dur))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
