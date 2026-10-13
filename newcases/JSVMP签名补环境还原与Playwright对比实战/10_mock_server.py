# -*- coding: utf-8 -*-
"""
10：本地模拟站服务（小红书 X-s 签名校验 · 模拟真实站风控）
=========================================================
路由：
  GET  /                          -> 签名演示页（pw_assets/sign_page.html）
  GET  /sign_page.html            -> 同上（Playwright 方案在浏览器内加载 source.js 产出签名）
  GET  /js_asset/source.js        -> JSVMP 资产静态服务（补环境与 Playwright 两方案共用同一份）
  GET  /api/health                -> 健康检查
  POST /api/sns/web/v1/homefeed   -> 数据接口（服务端三层签名校验）：
        ① 结构：X-s 以 XYW_ 开头，base64 解码含四字段 signSvn/signType/appId/payload，
                 appId == "xhs-pc-web"，payload 为 384 位十六进制
        ② 时效：X-t 与服务器时间偏差 ≤ ±300 秒
        ③ 指纹：payload 前 32 位命中"已知合法请求指纹白名单"
          （真实站服务端持有密钥、可对签名严验；本 mock 站无密钥，
            用离线实测的合法指纹库做近似校验——局限说明见 README.md）
        任一不匹配 -> 406 + 原因；全部通过 -> 200 + 自造 feed 数据

用法：
  python 10_mock_server.py             # 前台启动，人工浏览 http://127.0.0.1:18999/
  python 10_mock_server.py --selftest  # 自测 5 种签名组合（生成作业验证日志）
  爬虫 / Playwright 脚本内：subprocess 启动本脚本，等待端口就绪后再访问

合规声明：本地模拟站点，数据全部自造，无任何真实站点请求。
"""
import base64
import json
import os
import re
import socketserver
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST, PORT = "127.0.0.1", 18999
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

API_PATH = "/api/sns/web/v1/homefeed"   # 与课件签名目标一致的接口路径
TIME_WINDOW_MS = 300000                 # X-t 时间窗 ±300 秒

# 服务端"已知合法请求指纹库"（payload 前 32 位 hex）
# 来源：离线实测——课件同构 body（num=35）在"补环境复刻"与"课件原件"两条链路上
#       产出同一指纹 4509d8ed...（证据见 _run_03_sign_selftest.txt；非真实凭证）
KNOWN_FINGERPRINTS = {
    "4509d8ed4632e9b986d8805a964765e4": "homefeed 演示请求（课件同构 body，num=35）",
}

# 自造 feed 数据（演示用，非任何真实平台内容）
FEED_ITEMS = [
    {"note_id": "mock_1001", "title": "本地 mock 站的第 1 条演示笔记", "author": "mock_author_01", "likes": 128, "collected": 33, "comments": 7},
    {"note_id": "mock_1002", "title": "补环境方案的签名请求已通过服务端校验", "author": "mock_author_02", "likes": 256, "collected": 66, "comments": 14},
    {"note_id": "mock_1003", "title": "X-s 结构：四字段 + 384 位 payload", "author": "mock_author_03", "likes": 512, "collected": 99, "comments": 21},
    {"note_id": "mock_1004", "title": "JSVMP 解释执行的平均单次耗时实测", "author": "mock_author_04", "likes": 64, "collected": 12, "comments": 3},
    {"note_id": "mock_1005", "title": "Playwright 方案与补环境方案的对比数据", "author": "mock_author_05", "likes": 384, "collected": 77, "comments": 18},
    {"note_id": "mock_1006", "title": "X-t 时间窗校验的 406 反例演示", "author": "mock_author_06", "likes": 96, "collected": 8, "comments": 2},
    {"note_id": "mock_1007", "title": "请求指纹白名单如何挡下伪造签名", "author": "mock_author_07", "likes": 210, "collected": 41, "comments": 9},
    {"note_id": "mock_1008", "title": "从 3 字段简化签名到 4 字段完整签名", "author": "mock_author_08", "likes": 175, "collected": 52, "comments": 11},
    {"note_id": "mock_1009", "title": "cookie 字段完整性驱动签名完整度", "author": "mock_author_09", "likes": 420, "collected": 88, "comments": 16},
    {"note_id": "mock_1010", "title": "Node 21+ navigator 只读全局的坑", "author": "mock_author_10", "likes": 88, "collected": 19, "comments": 5},
    {"note_id": "mock_1011", "title": "undici 惰性物化的修复思路", "author": "mock_author_11", "likes": 142, "collected": 27, "comments": 6},
    {"note_id": "mock_1012", "title": "本地 mock 站合规声明：数据全部自造", "author": "mock_author_12", "likes": 33, "collected": 4, "comments": 1},
]


# ---------- 服务端校验逻辑（三层） ----------
def validate_xs(xs):
    """① 结构校验。返回 (ok, reason, payload_head)"""
    if not xs:
        return False, "缺少 X-s 签名头", ""
    if not xs.startswith("XYW_"):
        return False, "X-s 缺少 XYW_ 前缀", ""
    seg = xs[4:]
    seg += "=" * (-len(seg) % 4)   # 容错补齐 base64 padding
    try:
        obj = json.loads(base64.b64decode(seg).decode("utf-8"))
    except Exception as e:
        return False, "X-s base64/JSON 解码失败: %s" % e, ""
    for field in ("signSvn", "signType", "appId", "payload"):
        if field not in obj:
            return False, "X-s 缺少字段 %s" % field, ""
    if obj["appId"] != "xhs-pc-web":
        return False, "appId 非法: %r" % obj["appId"], ""
    payload = str(obj.get("payload", ""))
    if not re.match(r"^[0-9a-f]{384}$", payload):
        return False, "payload 非 384 位十六进制（实际 %d 位）" % len(payload), ""
    return True, "", payload[:32]


def validate_xt(xt_str, now_ms=None):
    """② 时效校验。返回 (ok, reason)"""
    try:
        xt = int(xt_str)
    except (TypeError, ValueError):
        return False, "X-t 缺失或非整数"
    now = now_ms if now_ms is not None else int(time.time() * 1000)
    delta = abs(now - xt)
    if delta > TIME_WINDOW_MS:
        return False, "X-t 超出 ±%d 秒时间窗（偏差 %.1f 秒）" % (TIME_WINDOW_MS // 1000, delta / 1000.0)
    return True, ""


class DemoServer(ThreadingHTTPServer):
    """修复：Windows 中文主机名下 HTTPServer.server_bind 内 socket.getfqdn
    会抛 UnicodeDecodeError，这里跳过 FQDN 解析、直接用监听地址。"""

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = host
        self.server_port = port


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stdout.write("[server] " + (fmt % args) + "\n")
        sys.stdout.flush()

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _serve_file(self, fp, ctype):
        if not os.path.isfile(fp):
            self._send_json(404, {"code": 404, "msg": "asset missing: " + os.path.basename(fp)})
            return
        with open(fp, "rb") as f:
            self._send(200, f.read(), ctype)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/sign_page.html"):
            self._serve_file(os.path.join(BASE_DIR, "pw_assets", "sign_page.html"), "text/html; charset=utf-8")
        elif path == "/js_asset/source.js":
            self._serve_file(os.path.join(BASE_DIR, "js_asset", "source.js"), "application/javascript; charset=utf-8")
        elif path == "/api/health":
            self._send_json(200, {"code": 0, "msg": "ok"})
        else:
            self._send_json(404, {"code": 404, "msg": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == API_PATH:
            self._api_homefeed()
        else:
            self._send_json(404, {"code": 404, "msg": "not found"})

    def _reject(self, reason):
        print("[server] 406 拒绝: %s" % reason)
        self._send_json(406, {"code": 406, "success": False, "msg": reason})

    def _api_homefeed(self):
        # 读请求体
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        if not raw:
            self._send_json(400, {"code": 400, "msg": "empty body"})
            return
        try:
            json.loads(raw.decode("utf-8"))
        except Exception as e:
            self._send_json(400, {"code": 400, "msg": "body 非合法 JSON: %s" % e})
            return

        # ① 结构校验
        xs = self.headers.get("X-s", "")
        ok, reason, head = validate_xs(xs)
        if not ok:
            self._reject(reason)
            return

        # ② 时效校验
        ok, reason = validate_xt(self.headers.get("X-t", ""))
        if not ok:
            self._reject(reason)
            return

        # ③ 指纹白名单（近似绑定校验，局限见文件头说明）
        if head not in KNOWN_FINGERPRINTS:
            self._reject("请求指纹 %s... 不在合法指纹库" % head[:8])
            return

        print("[server] 200 校验通过 指纹=%s... (%s)" % (head[:8], KNOWN_FINGERPRINTS[head]))
        self._send_json(200, {
            "code": 0,
            "success": True,
            "msg": "ok",
            "data": {
                "total": len(FEED_ITEMS),
                "cursor": "mock_cursor_next_page",
                "items": FEED_ITEMS,
            },
        })


# ---------- 自测：5 种签名组合 ----------
COURSE_BODY = {
    "cursor_score": "", "num": 35, "refresh_type": 1, "note_index": 27,
    "unread_begin_note_id": "", "unread_end_note_id": "", "unread_note_count": 0,
    "category": "homefeed.food_v3", "search_key": "", "need_num": 10,
    "image_formats": ["jpg", "webp", "avif"], "need_filter_image": False,
}


def fake_xs(payload=None, app_id="xhs-pc-web"):
    """构造"结构合法"的伪造签名（默认 payload 全 0，指纹必然不在白名单）"""
    obj = {"signSvn": "51", "signType": "x1", "appId": app_id, "payload": payload or ("0" * 384)}
    seg = base64.b64encode(json.dumps(obj, separators=(",", ":")).encode("utf-8")).decode("ascii")
    return "XYW_" + seg


def _node_sign_real():
    """调 02_xhs_sign_cli.js 生成一条真实签名（供 selftest 用例 5 使用）"""
    compact = json.dumps(COURSE_BODY, separators=(",", ":"), ensure_ascii=False)
    b64 = base64.b64encode(compact.encode("utf-8")).decode("ascii")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(
        ["node", os.path.join(BASE_DIR, "02_xhs_sign_cli.js"), "--path", API_PATH, "--body-b64", b64],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR, env=env, timeout=90)
    out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
    if r.returncode != 0 or not out:
        raise RuntimeError("node 签名失败 exit=%s stderr=%s" % (r.returncode, (r.stderr or b"")[:300]))
    return json.loads(out[-1])


def selftest():
    """--selftest：后台线程启动服务，5 种签名组合请求接口，打印风控校验结果

    预期：无签名 406 / 结构非法 406 / 签名过期 406 / 伪造指纹 406 / 真实签名 200
    """
    import threading
    import urllib.request
    import urllib.error

    srv = DemoServer((HOST, PORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("[selftest] 服务已启动: http://%s:%d/" % (HOST, PORT))

    url = "http://%s:%d%s" % (HOST, PORT, API_PATH)
    body_bytes = json.dumps(COURSE_BODY, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    now_ms = int(time.time() * 1000)

    def post(xs=None, xt=None):
        req = urllib.request.Request(url, data=body_bytes, method="POST")
        req.add_header("Content-Type", "application/json;charset=UTF-8")
        if xs is not None:
            req.add_header("X-s", xs)
        if xt is not None:
            req.add_header("X-t", str(xt))
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    print("\n----- 服务端三层签名校验（5 种组合） -----")
    cases = []
    s1, b1 = post()
    cases.append(("1 无任何签名头                -> HTTP %s %s" % (s1, b1.get("msg")), s1 == 406))
    print("  [%s] %s" % ("PASS" if cases[-1][1] else "FAIL", cases[-1][0]))

    s2, b2 = post(xs="ABC_" + fake_xs()[4:], xt=now_ms)
    cases.append(("2 伪造前缀（非 XYW_）        -> HTTP %s %s" % (s2, b2.get("msg")), s2 == 406))
    print("  [%s] %s" % ("PASS" if cases[-1][1] else "FAIL", cases[-1][0]))

    s3, b3 = post(xs=fake_xs(), xt=now_ms - 600000)
    cases.append(("3 结构合法但 X-t 过期 10 分钟 -> HTTP %s %s" % (s3, b3.get("msg")), s3 == 406))
    print("  [%s] %s" % ("PASS" if cases[-1][1] else "FAIL", cases[-1][0]))

    s4, b4 = post(xs=fake_xs(), xt=now_ms)
    cases.append(("4 结构合法+时间正确但指纹伪造 -> HTTP %s %s" % (s4, b4.get("msg")), s4 == 406))
    print("  [%s] %s" % ("PASS" if cases[-1][1] else "FAIL", cases[-1][0]))

    try:
        sig = _node_sign_real()
        s5, b5 = post(xs=sig["X-s"], xt=sig["X-t"])
        detail = "HTTP %s total=%s" % (s5, (b5.get("data") or {}).get("total"))
        cases.append(("5 真实签名（补环境引擎生成）  -> " + detail, s5 == 200))
    except Exception as e:
        cases.append(("5 真实签名 -> 执行异常: %s" % e, False))
    print("  [%s] %s" % ("PASS" if cases[-1][1] else "FAIL", cases[-1][0]))

    all_ok = all(ok for _, ok in cases)
    print("\n[selftest] 结论: " + ("全部通过（406/406/406/406/200 符合预期）" if all_ok else "存在失败项"))
    srv.shutdown()
    return 0 if all_ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    srv = DemoServer((HOST, PORT), Handler)
    print("[server] 小红书签名 mock 站已启动: http://%s:%d/  (Ctrl+C 退出)" % (HOST, PORT))
    print("[server] 校验规则：X-s 结构 + X-t 时间窗(±300s) + 请求指纹白名单")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
