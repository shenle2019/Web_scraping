# -*- coding: utf-8 -*-
"""
pw_common.py：交付目录公共辅助（补环境爬虫 / Playwright 方案 / 对比实测共用）
=========================================================
职责：
  1. LocalSite 上下文管理器 —— subprocess 启动/停止本地模拟站（10_mock_server.py）
  2. node_sign() —— subprocess 调 02_xhs_sign_cli.js（补环境 + JSVMP 签名引擎）
  3. post_signed() —— 按真实站点口径发送请求（紧凑 JSON + X-s/X-t 头）
  4. launch_browser() / inject() —— Playwright 相关（供 30/31 使用）
  5. hr() / check() —— 日志与断言辅助

设计约定：
  - 顶层不 import playwright：补环境链路（20）仅依赖「#1~#3」，保持轻依赖；
  - 端口 18999 为本交付目录专属（避免与 Day25 反调试案例的 18888 冲突）。
"""
import base64
import json
import os
import socket
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = "127.0.0.1", 18999
URL_HOME = "http://%s:%d/" % (HOST, PORT)
URL_API = "http://%s:%d/api/sns/web/v1/homefeed" % (HOST, PORT)

NODE = "node"
SIGN_CLI = os.path.join(BASE, "02_xhs_sign_cli.js")

CREATIONFLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0

# 与课件抓包一致的演示请求体（num=35 那套，指纹 4509d8ed...）
COURSE_BODY = {
    "cursor_score": "", "num": 35, "refresh_type": 1, "note_index": 27,
    "unread_begin_note_id": "", "unread_end_note_id": "", "unread_note_count": 0,
    "category": "homefeed.food_v3", "search_key": "", "need_num": 10,
    "image_formats": ["jpg", "webp", "avif"], "need_filter_image": False,
}
API_PATH = "/api/sns/web/v1/homefeed"


def compact(obj):
    """紧凑 JSON（与前端 JSON.stringify 口径一致）"""
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


# ---------- 1. 本地模拟站 ----------
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
            [sys.executable, "-X", "utf8", os.path.join(BASE, "10_mock_server.py")],
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


# ---------- 2. Node 签名引擎桥 ----------
def node_sign(path_val, body_obj, count=1, timeout=90):
    """调 02_xhs_sign_cli.js，返回其 stdout 最后一行的 JSON dict。

    count=1 -> {"ok":true,"X-s":...,"X-t":...,"cost_ms":...}
    count>1 -> {"ok":true,"count":N,"ok_count":N,"total_ms":...,"avg_ms":...}
    """
    payload = compact(body_obj)
    b64 = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    args = [NODE, SIGN_CLI, "--path", path_val, "--body-b64", b64]
    if count > 1:
        args += ["--count", str(count)]
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       cwd=BASE, env=env, timeout=timeout)
    out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
    if r.returncode != 0 or not out:
        err = (r.stderr or b"").decode("utf-8", "replace")
        raise RuntimeError("node 签名失败 exit=%s stderr=%s" % (r.returncode, err[:400]))
    return json.loads(out[-1])


# ---------- 3. 按站点口径发送 ----------
def decode_xs(xs):
    """解码 X-s：返回 {"fields":[...], "payload_len":N, "payload_head":"32hex", "obj":{...}}"""
    seg = xs[4:] if xs.startswith("XYW_") else xs
    seg += "=" * (-len(seg) % 4)
    obj = json.loads(base64.b64decode(seg).decode("utf-8"))
    payload = str(obj.get("payload", ""))
    return {
        "fields": list(obj.keys()),
        "payload_len": len(payload),
        "payload_head": payload[:32],
        "obj": obj,
    }


def post_signed(body_obj, xs=None, xt=None, url=URL_API, timeout=15):
    """紧凑 JSON body + X-s/X-t 头 POST。返回 (status_code, resp_json)"""
    import requests  # 延迟导入：仅发送环节需要
    data = compact(body_obj).encode("utf-8")
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    if xs is not None:
        headers["X-s"] = xs
    if xt is not None:
        headers["X-t"] = str(xt)
    resp = requests.post(url, data=data, headers=headers, timeout=timeout)
    try:
        return resp.status_code, resp.json()
    except ValueError:
        return resp.status_code, {"raw": resp.text[:200]}


# ---------- 4. Playwright 相关（30/31 使用） ----------
def launch_browser(p):
    """启动系统 Edge（无头）。用 channel=msedge 复用系统浏览器，免 playwright install"""
    return p.chromium.launch(channel="msedge", headless=True)


def inject(page, *script_rel_paths):
    """把脚本注入到页面文档创建之前（最早的执行时机）"""
    for rel in script_rel_paths:
        page.add_init_script(path=os.path.join(BASE, rel))


def read_script(rel):
    with open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return f.read()


# ---------- 5. 日志 / 断言 ----------
def hr(title):
    print("=" * 64)
    print(title)
    print("=" * 64)


def check(name, cond):
    print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
    return bool(cond)
