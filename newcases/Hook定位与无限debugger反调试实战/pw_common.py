# -*- coding: utf-8 -*-
"""
pw_common.py：Playwright 验证脚本公共辅助
=========================================================
职责：
  1. LocalSite 上下文管理器 —— subprocess 启动/停止本地模拟站（10_local_server.py）
  2. launch_browser()     —— 启动系统自带 Edge（免下载 Playwright 浏览器）
  3. inject()             —— 向页面注入 hook/对抗脚本（文档创建前，add_init_script）
  4. 日志/断言辅助
"""
import os
import socket
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = "127.0.0.1", 18888
URL_HOME = "http://%s:%d/" % (HOST, PORT)

CREATIONFLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0


def _port_ready(host=HOST, port=PORT, timeout=0.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_port(timeout=15.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if _port_ready():
            return True
        time.sleep(0.2)
    return False


class LocalSite(object):
    """with LocalSite() as site: ... —— 启动本地模拟站，退出时自动关闭"""

    def __init__(self, quiet=False):
        self.proc = None
        self.quiet = quiet

    def __enter__(self):
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        self.proc = subprocess.Popen(
            [sys.executable, "-X", "utf8", os.path.join(BASE, "10_local_server.py")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            creationflags=CREATIONFLAGS, env=env)
        if not wait_port():
            raise RuntimeError("本地模拟站启动失败：端口 %d 未就绪" % PORT)
        print("[site] 本地模拟站已就绪: %s" % URL_HOME)
        return self

    def __exit__(self, *exc):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except Exception:
                self.proc.kill()
        print("[site] 本地模拟站已停止")


def launch_browser(p):
    """启动系统 Edge（无头）。用 channel=msedge 复用系统浏览器，免 playwright install"""
    return p.chromium.launch(channel="msedge", headless=True)


def inject(page, *script_rel_paths):
    """把 hook_scripts/*.js 注入到页面文档创建之前（最早的执行时机）"""
    for rel in script_rel_paths:
        page.add_init_script(path=os.path.join(BASE, rel))


def read_script(rel):
    with open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return f.read()


def hr(title):
    print("=" * 64)
    print(title)
    print("=" * 64)


def check(name, cond):
    print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
    return bool(cond)
