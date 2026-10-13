# -*- coding: utf-8 -*-
"""
common.py —— 交付目录公共辅助（20 管线共用）
=========================================================
职责：
  1. LocalSite 上下文管理器 —— subprocess 启动/停止本地模拟站（10_mock_server.py）
  2. node_sign() —— subprocess 调 02_sign_engine.js 生成 a_bogus
  3. gen_sig() / get_with_sig() —— 签名与"按站点口径发送"的原语
     （先签名后请求，便于反例用例：无签名/伪造/篡改/重放）
  4. hr() / check() —— 日志与断言辅助

设计约定：
  - 端口 18990 为本交付目录专属；
  - 签名 UA 必须与请求头 User-Agent 一致（mock 侧用请求头 UA 复算校验）；
  - a_bogus 含 /+= 等字符，URL 拼接时整体 percent-encode。
"""
import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = "127.0.0.1", 18990
URL_HOME = "http://%s:%d/" % (HOST, PORT)
URL_API = "http://%s:%d/api/aweme/post" % (HOST, PORT)
URL_HEALTH = "http://%s:%d/api/health" % (HOST, PORT)

NODE = "node"
SIGN_CLI = os.path.join(BASE, "02_sign_engine.js")

# 与 01_env_mini.js 的 UA_PC / 10_mock_server.py 的 UA_DEFAULT 保持一致
UA_DEFAULT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

CREATIONFLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0


def build_query(params):
    """有序 dict -> urlencode query 串（与签名输入、URL 拼接三方一致）"""
    return urllib.parse.urlencode(params)


# ---------- 1. 本地模拟站 ----------
def _port_ready(host=HOST, port=PORT, timeout=0.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_port(timeout=30.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if _port_ready():
            return True
        time.sleep(0.3)
    return False


class LocalSite(object):
    """with LocalSite() as site: ... —— 启动本地模拟站，退出时自动关闭

    子进程输出重定向到 output/_mock_server.log：启动失败时打印日志尾部
    （stdout=PIPE 不消费易难排查；日志文件也能沉淀服务端拒绝记录）。
    """

    def __init__(self, quiet=False):
        self.proc = None
        self.quiet = quiet
        self.logf = None
        self.log_path = os.path.join(BASE, "output", "_mock_server.log")

    def __enter__(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self.logf = open(self.log_path, "w", encoding="utf-8")
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        self.proc = subprocess.Popen(
            [sys.executable, "-X", "utf8", os.path.join(BASE, "10_mock_server.py")],
            stdout=self.logf, stderr=subprocess.STDOUT,
            creationflags=CREATIONFLAGS, env=env)
        if not wait_port(timeout=60.0):
            self._kill()
            self._dump_log()
            raise RuntimeError("本地模拟站启动失败：端口 %d 未就绪（日志: %s）" % (PORT, self.log_path))
        print("[site] 本地模拟站已就绪: %s" % URL_HOME)
        return self

    def _kill(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except Exception:
                self.proc.kill()

    def _dump_log(self):
        try:
            self.logf.flush()
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                tail = f.read()[-1500:]
            if tail.strip():
                print("[site] mock 站日志尾部：\n" + tail)
        except Exception:
            pass

    def __exit__(self, *exc):
        self._kill()
        if self.logf:
            self.logf.close()
            self.logf = None
        print("[site] 本地模拟站已停止")


# ---------- 2. Node 签名桥 ----------
def node_sign(query_str, ua=None, timeout=90):
    """调 02_sign_engine.js，返回 JSON dict（含 a_bogus/len/cost_ms）"""
    b64 = base64.b64encode(query_str.encode("utf-8")).decode("ascii")
    args = [NODE, SIGN_CLI, "--query-b64", b64]
    if ua:
        args += ["--ua", ua]
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       cwd=BASE, env=env, timeout=timeout)
    out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
    if r.returncode != 0 or not out:
        err = (r.stderr or b"").decode("utf-8", "replace")
        raise RuntimeError("node 签名失败 exit=%s stderr=%s" % (r.returncode, err[:400]))
    return json.loads(out[-1])


# ---------- 3. 签名与发送原语 ----------
def gen_sig(params, ua=None):
    """生成签名，返回 (sig, query_str)"""
    q = build_query(params)
    return node_sign(q, ua)["a_bogus"], q


def _do_get(url, ua=None, timeout=30):
    import requests   # 延迟导入：仅发送环节需要
    resp = requests.get(url, headers={"User-Agent": ua or UA_DEFAULT}, timeout=timeout)
    try:
        return resp.status_code, resp.json()
    except ValueError:
        return resp.status_code, {"raw": resp.text[:200]}


def get_with_sig(params, sig, ua=None, timeout=30):
    """携带指定签名请求 API（供篡改/重放等反例用例）"""
    q = build_query(params)
    url = URL_API + "?" + q + "&a_bogus=" + urllib.parse.quote(sig, safe="")
    return _do_get(url, ua=ua, timeout=timeout)


def signed_get(params, ua=None, timeout=30):
    """签名 + 请求一体化；返回 (status, body, sig)"""
    sig, _ = gen_sig(params, ua=ua)
    st, body = get_with_sig(params, sig, ua=ua, timeout=timeout)
    return st, body, sig


def get_no_sig(params, ua=None, timeout=30):
    """不带 a_bogus 请求（反例：缺签名）"""
    return _do_get(URL_API + "?" + build_query(params), ua=ua, timeout=timeout)


def get_health(timeout=10):
    return _do_get(URL_HEALTH, timeout=timeout)


# ---------- 4. 日志 / 断言 ----------
def hr(title):
    print("=" * 68)
    print(title)
    print("=" * 68)


def check(name, cond, extra=""):
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("   " + extra) if extra else ""))
    return bool(cond)
