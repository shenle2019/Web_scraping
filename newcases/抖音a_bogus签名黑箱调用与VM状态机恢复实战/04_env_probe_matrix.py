# -*- coding: utf-8 -*-
"""
04_env_probe_matrix.py —— 补环境完整度影响矩阵（编排 04_env_probe_worker.js）
=========================================================
背景：签名长度/主体由"补环境字段完整度"决定（黑箱实测谱系）：
  残环境 base（navigator 空/screen 缺 width）→ 144；
  +screen8（宽/pixelDepth）→ 152；+inner（视口尺寸）→ 160；full → 164。
  （注意：修复 navigator 的 defineProperty 坑后，base 由 140 变为 144——
   普通赋值静默失败时 navigator={} 实际从未生效。）

本编排器逐变体起独立 Node 进程（环境互不污染），收集 len 与签名，
按长度分组定位"哪个补环境字段改变了签名形态"。

用法：python 04_env_probe_matrix.py
"""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.join(BASE, "04_env_probe_worker.js")

VARIANTS = ["base", "keepbuf", "inner", "navi", "screen8", "doc", "loc", "storage", "full"]

# 跨环境共同段（140/144/152/160/164 各形态签名均包含，证明同源 bdms 模板）
COMMON_SEG = "xow7zvMIubZsQJI"


def run_worker(variant):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(["node", WORKER, variant], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, cwd=BASE, env=env, timeout=120)
    out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
    if r.returncode != 0 or not out:
        err = (r.stderr or b"").decode("utf-8", "replace")
        return {"v": variant, "len": -1, "sig": "", "err": err[:200]}
    return json.loads(out[-1])


def main():
    print("=" * 78)
    print("04 补环境完整度影响矩阵（每变体独立 Node 进程）")
    print("=" * 78)
    print("%-10s %5s %10s  %s" % ("变体", "len", "含共同段", "sig(前64位)"))
    print("-" * 78)

    lens = {}
    for v in VARIANTS:
        r = run_worker(v)
        lens[v] = r["len"]
        sig = r.get("sig") or ""
        print("%-10s %5s %10s  %s" % (
            v, r["len"],
            bool(COMMON_SEG in sig),
            sig[:64] + ("  [ERR] " + r["err"] if r.get("err") else "")))

    print("-" * 78)
    groups = {}
    for k, ln in lens.items():
        groups.setdefault(ln, []).append(k)
    print("结论（按长度分组；每项±1 字段都改变长度/主体）：")
    for ln in sorted(groups):
        print("  len=%-4s : %s" % (ln, ", ".join(groups[ln])))

    base_len = lens.get("base")
    print("  逐项对照 base(%s)：" % base_len)
    for v in VARIANTS[1:-1]:
        tag = "★ 改变长度" if lens.get(v) != base_len else "无影响"
        print("    + %-8s -> len=%s  %s" % (v, lens.get(v), tag))
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
