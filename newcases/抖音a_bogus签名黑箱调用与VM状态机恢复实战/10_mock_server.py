# -*- coding: utf-8 -*-
"""
10_mock_server.py —— 抖音接口形态本地模拟站（a_bogus 复算校验）
=========================================================
对真实抖音服务端校验机制的黑箱近似：mock 站只做"本地能自洽验证"的校验，
三层风控：
  1) 形态护栏：len==164 / idx16-17=="5-" / 末位"=" / 字符集合法
  2) 复算比对（核心）：服务端用 02 引擎以"请求的 query（剥除 a_bogus）+
     请求的 UA"复算签名，与请求签名逐位比对——差异位置必须 ⊆ 启动时探测
     出的白名单（随机位 + 跨进程位）。已实证：同输入复算的差异只有随机位。
  3) Replay 检测：同一签名重复提交拒绝（演示性一次性凭证语义）
  4) 媒体直链：/video/<id>.mp4 与 /cover/<id>.jpg 返回确定性自造字节，
     供爬虫提取视频 URL 后做真实访问与下载验证（不参与签名校验）

白名单探测：启动时 12 个独立 Node 进程 × 1 样本（覆盖"进程级副本位"——
实测此类位取值空间极小、低样本量会漏，如 pos44 在 3 进程探测中漏掉、
12+ 进程才稳定暴露）+ 同进程 6 样本（覆盖"每次调用随机位"），
全部样本两两 diff 取并集。
实测样本（30 进程实验）：跨进程摆动位全集 22 位 =
  [0-15, 44, 45, 50, 51, 160, 161]；同进程随机位 19 位 = [0-15, 51, 160, 161]。

用法：
  python 10_mock_server.py            # 启动服务（默认端口 18990）
  python 10_mock_server.py --selftest # 内部用例自检（6 用例，不起 HTTP）

合规说明：本服务仅监听 127.0.0.1，用于课件案例的本地端到端验证，
不对任何真实站点发起请求；演示数据为自造内容。
"""
import base64
import json
import os
import random
import socketserver
import subprocess
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = "127.0.0.1", 18990

NODE = "node"
SIGN_CLI = os.path.join(BASE, "02_sign_engine.js")
ENV_PROBE = os.path.join(BASE, "04_env_probe_worker.js")

# 与 01_env_mini.js 的 UA_PC 保持一致（签名 UA 必须与请求头 UA 一致）
UA_DEFAULT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# 探测/复算用固定 query（与 20 管线、03 自检同款简化版）
FIXED_QUERY = ("device_platform=webapp&aid=6383&channel=channel_pc_web&pc_client_type=1"
               "&version_code=170400&cookie_enabled=true&screen_width=1496&screen_height=967"
               "&browser_language=zh-CN&platform=PC&webid=7371422219199055371&msToken=XBPLACEHOLDER")

SIG_LEN = 164
ALLOWED_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/-=")

# 运行时状态
WHITELIST = set()      # 允许摇摆的位（随机位+跨进程位），启动时探测
USED_SIGS = set()      # 已通过校验的签名（replay 检测）
PROBE_INFO = {}        # 探测摘要（health 展示）

CORPUS = None          # 12 条演示数据

# 媒体直链基础地址（指向本 mock 站自身）
MEDIA_BASE = "http://%s:%d" % (HOST, PORT)


# ---------------- Node 桥 ----------------
def run_node(args, timeout=120):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([NODE] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       cwd=BASE, env=env, timeout=timeout)
    out = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
    if r.returncode != 0 or not out:
        err = (r.stderr or b"").decode("utf-8", "replace")
        raise RuntimeError("node 调用失败 exit=%s stderr=%s" % (r.returncode, err[:300]))
    return json.loads(out[-1])


def sign_query(query_str, ua=None, count=None):
    """调 02 签名引擎（count>1 时返回统计+全量样本）"""
    b64 = base64.b64encode(query_str.encode("utf-8")).decode("ascii")
    args = [SIGN_CLI, "--query-b64", b64]
    if ua:
        args += ["--ua", ua]
    if count and count > 1:
        args += ["--count", str(count)]
    return run_node(args)


def diff_pos(a, b):
    return [i for i in range(min(len(a), len(b))) if a[i] != b[i]]


# ---------------- 白名单探测 ----------------
def probe_whitelist(procs=12, inproc_samples=6):
    """多进程采样 → 两两 diff 并集 = 允许摇摆位集合

    12 个独立进程：覆盖"进程级副本位"（pos 44/45/50/161 类，取值空间极小、
    低样本量会漏——3 进程探测实测漏掉过 pos44）；
    同进程 6 样本：覆盖"每次调用随机位"（pos 0-15/51/160/161 类）。
    """
    t0 = time.time()
    samples = []
    for _ in range(procs):
        samples.append(sign_query(FIXED_QUERY)["a_bogus"])
    samples += sign_query(FIXED_QUERY, count=inproc_samples)["samples"]
    wl = set()
    for i in range(len(samples)):
        for j in range(i + 1, len(samples)):
            wl |= set(diff_pos(samples[i], samples[j]))
    return sorted(wl), len(samples), round((time.time() - t0) * 1000)


# ---------------- 三层校验 ----------------
def check_format(sig):
    if not sig or len(sig) != SIG_LEN:
        return False, "长度不符(%s!=%d)" % (len(sig) if sig else 0, SIG_LEN)
    if sig[16:18] != "5-":
        return False, "结构段 idx16-17 不符(%r)" % sig[16:18]
    if sig[-1] != "=":
        return False, "末位非 '='"
    bad = [c for c in sig if c not in ALLOWED_CHARS]
    if bad:
        return False, "非法字符 %r" % bad[:5]
    return True, "ok"


def verify_a_bogus(query_rest, ua, sig):
    """返回 (ok, reason, detail)"""
    # 1) 形态护栏
    ok, reason = check_format(sig)
    if not ok:
        return False, "格式校验失败: " + reason, {}
    if not ua:
        return False, "缺少 User-Agent（签名 UA 必须与请求头一致）", {}
    # 2) replay
    if sig in USED_SIGS:
        return False, "签名已被使用（replay 防护）", {}
    # 3) 复算比对
    try:
        rec = sign_query(query_rest, ua)["a_bogus"]
    except Exception as e:
        return False, "复算失败: %s" % str(e)[:120], {}
    d = diff_pos(sig, rec)
    bad = [p for p in d if p not in WHITELIST]
    detail = {"diff": d, "unexpected": bad}
    if bad:
        return False, "复算比对失败: %d 处非随机位差异 %s" % (len(bad), bad[:10]), detail
    USED_SIGS.add(sig)
    return True, "ok(diff=%d 全在随机位)" % len(d), detail


# ---------------- 演示数据 ----------------
# 1×1 PNG 基底（封面占位）
PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
# 伪 mp4 头（ftyp box 占位，非真实编码）
V_HEAD = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"

_MEDIA_CACHE = {}


def mock_media(kind, name):
    """按直链名确定性生成占位媒体字节（同一 URL 恒定产出同样字节）。

    video → 伪 mp4 头 + 16~48KB 伪随机字节；cover → 1px PNG + 512B 扩展。
    内容为自造数据，不依赖网络与真实素材，便于爬虫侧校验下载完整性。
    """
    key = (kind, name)
    if key in _MEDIA_CACHE:
        return _MEDIA_CACHE[key]
    rnd = random.Random("mock-media:%s:%s" % (kind, name))
    if kind == "video":
        size = rnd.randint(16 * 1024, 48 * 1024)
        body, ctype = V_HEAD + bytes(rnd.getrandbits(8) for _ in range(size)), "video/mp4"
    else:
        body, ctype = PNG_1PX + bytes(rnd.getrandbits(8) for _ in range(512)), "image/jpeg"
    _MEDIA_CACHE[key] = (body, ctype)
    return body, ctype


def make_corpus():
    """12 条演示数据：video 字段复刻真实 API 形态（play_addr/download_addr/cover），
    URL 均为指向本 mock 站的自造直链，可真实访问与下载。"""
    items = []
    for i in range(1, 13):
        aid = "736600000000000000%02d" % i
        items.append({
            "aweme_id": aid,
            "desc": "演示视频 #%02d｜a_bogus 签名联调数据" % i,
            "create_time": 1716290000 + i * 3600,
            "author": {"nickname": "演示作者%02d" % i, "sec_uid": "MS4wLjABAAAA_demo_%02d" % i},
            "statistics": {"digg_count": 1000 + i * 37, "comment_count": 10 + i, "share_count": i * 3},
            "video": {
                "duration": 15000 + i * 1000,
                "play_addr": {
                    "uri": "v0300fg10000mock%012d" % i,
                    "url_list": ["%s/video/%s.mp4" % (MEDIA_BASE, aid),
                                 "%s/video/%s.mp4?backup=1" % (MEDIA_BASE, aid)],
                },
                "download_addr": {"url_list": ["%s/video/%s.mp4?dl=1" % (MEDIA_BASE, aid)]},
                "cover": {"url_list": ["%s/cover/%s.jpg" % (MEDIA_BASE, aid)]},
            },
        })
    return items


def strip_param(raw_query, name):
    """从原始 query 串剥离指定参数（保持其余段原样顺序拼接）"""
    segs = raw_query.split("&")
    rest, val = [], None
    for s in segs:
        if s.startswith(name + "="):
            val = urllib.parse.unquote(s[len(name) + 1:])
        elif s:
            rest.append(s)
    return "&".join(rest), val


PAGE_SIZE = 6


def feed_page(query_rest):
    qs = urllib.parse.parse_qs(query_rest)
    try:
        cursor = int((qs.get("max_cursor") or ["0"])[0])
    except ValueError:
        cursor = 0
    if cursor < 0:
        cursor = 0
    start = cursor if cursor < len(CORPUS) else len(CORPUS)
    page = CORPUS[start:start + PAGE_SIZE]
    nxt = start + len(page)
    return {
        "status_code": 0,
        "aweme_list": page,
        "has_more": 1 if nxt < len(CORPUS) else 0,
        "max_cursor": nxt,
    }


# ---------------- HTTP ----------------
def log(msg):
    print("[mock] " + msg, flush=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "DouyinMock/1.0"
    protocol_version = "HTTP/1.1"

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path, _, raw_query = self.path.partition("?")
        if path == "/api/health":
            self._send(200, {"ok": True, "whitelist_size": len(WHITELIST),
                             "probe": PROBE_INFO, "used_sigs": len(USED_SIGS)})
        elif path == "/api/aweme/post":
            self.handle_feed(raw_query)
        elif path.startswith("/video/") or path.startswith("/cover/"):
            self.handle_media(path)
        elif path == "/":
            self._send(200, {"service": "douyin-mock", "api": "/api/aweme/post",
                             "health": "/api/health",
                             "media": ["/video/<id>.mp4", "/cover/<id>.jpg"],
                             "note": "本地演示站：三层校验=形态+复算比对+replay"})
        else:
            self._send(404, {"status_code": 404})

    def handle_feed(self, raw_query):
        ua = self.headers.get("User-Agent", "")
        rest, sig = strip_param(raw_query, "a_bogus")
        if sig is None:
            log("拒绝: 无 a_bogus 参数")
            self._send(406, {"status_code": 406, "status_msg": "缺少 a_bogus 签名"})
            return
        ok, reason, detail = verify_a_bogus(rest, ua, sig)
        if not ok:
            log("拒绝(%s): sig=%.16s... ua=%.12s..." % (reason, sig, ua))
            self._send(406, {"status_code": 406, "status_msg": reason})
            return
        page = feed_page(rest)
        log("通过(%s): cursor=%s 返回%d条" % (reason, raw_query.count("max_cursor"),
                                           len(page["aweme_list"])))
        self._send(200, page)

    def handle_media(self, path):
        """媒体直链（模拟 CDN 直链，无签名要求）：/video/<id>.mp4、/cover/<id>.jpg"""
        kind = "video" if path.startswith("/video/") else "cover"
        name = path.split("/", 2)[2]
        body, ctype = mock_media(kind, name)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        self.wfile.write(body)
        log("媒体直链: %s %s (%d bytes)" % (kind, name, len(body)))

    def log_message(self, fmt, *args):   # 压掉默认 stderr 噪音
        pass


class MockHTTPServer(ThreadingHTTPServer):
    """覆写 server_bind 绕过 http.server 默认的 socket.getfqdn() 调用。

    实测坑（中文 Windows + Python 3.8）：默认的 HTTPServer.server_bind 会执行
    socket.getfqdn(host) → gethostbyaddr 返回 GBK 字节的主机名 → Python 3.8 用
    UTF-8 解码抛 UnicodeDecodeError，服务在绑定前直接崩溃（子进程 exit=1）。
    本地 mock 不需要 FQDN，直接用 IP 作为 server_name。
    """
    daemon_threads = True

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = host
        self.server_port = port


def start_http():
    httpd = MockHTTPServer((HOST, PORT), Handler)
    log("模拟站已启动 http://%s:%d/ （白名单 %d 位）" % (HOST, PORT, len(WHITELIST)))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


# ---------------- selftest ----------------
def selftest():
    global WHITELIST
    print("=" * 72)
    print("10 selftest —— a_bogus 校验机制自检（6 用例）")
    print("=" * 72)
    wl, n_sample, ms = probe_whitelist()
    WHITELIST = set(wl)
    print("白名单探测：%d 样本 / %dms → %d 位摇摆 = %s" % (n_sample, ms, len(wl), wl))
    print("-" * 72)

    n_pass, n_fail = 0, 0

    def case(name, want_ok, got_ok, reason):
        nonlocal n_pass, n_fail
        good = (want_ok == got_ok)
        if good:
            n_pass += 1
        else:
            n_fail += 1
        print("  [%s] %-28s 期望=%s 实际=%s (%s)" % (
            "PASS" if good else "FAIL", name,
            "通过" if want_ok else "拒绝", "通过" if got_ok else "拒绝", reason))

    # T1 真签名
    sig1 = sign_query(FIXED_QUERY, UA_DEFAULT)["a_bogus"]
    ok1, why1, _ = verify_a_bogus(FIXED_QUERY, UA_DEFAULT, sig1)
    case("T1 真签名", True, ok1, why1)

    # T2 篡改稳定位（idx100，位于主体区）
    tampered = sig1[:100] + ("A" if sig1[100] != "A" else "B") + sig1[101:]
    ok2, why2, _ = verify_a_bogus(FIXED_QUERY, UA_DEFAULT, tampered)
    case("T2 篡改稳定位", False, ok2, why2)

    # T3 随机假串
    ok3, why3, _ = verify_a_bogus(FIXED_QUERY, UA_DEFAULT, "A" * SIG_LEN)
    case("T3 随机假串", False, ok3, why3)

    # T4 残环境签名（04 worker base：navigator 空对象环境，144 字符）
    env_out = run_node([ENV_PROBE, "base"])
    sig4 = env_out["sig"]
    ok4, why4, _ = verify_a_bogus(FIXED_QUERY, UA_DEFAULT, sig4)
    case("T4 残环境签名(len=%s)" % env_out["len"], False, ok4, why4)

    # T5 重放 T1 的签名
    ok5, why5, _ = verify_a_bogus(FIXED_QUERY, UA_DEFAULT, sig1)
    case("T5 重放真签名", False, ok5, why5)

    # T6 变 query（翻页 cursor=6）新签名 → 通过（复算机制与输入一致）
    q2 = FIXED_QUERY.replace("&channel=", "&max_cursor=6&channel=")
    sig6 = sign_query(q2, UA_DEFAULT)["a_bogus"]
    ok6, why6, _ = verify_a_bogus(q2, UA_DEFAULT, sig6)
    case("T6 翻页query新签名", True, ok6, why6)

    print("-" * 72)
    print("SELFTEST %s  (%d/%d)" % ("PASS" if n_fail == 0 else "FAIL", n_pass, n_pass + n_fail))
    print("=" * 72)
    return 0 if n_fail == 0 else 1


def main():
    global WHITELIST, PROBE_INFO, CORPUS
    CORPUS = make_corpus()
    if "--selftest" in sys.argv:
        return selftest()
    wl, n_sample, ms = probe_whitelist()
    WHITELIST = set(wl)
    PROBE_INFO = {"samples": n_sample, "whitelist": wl, "cost_ms": ms}
    start_http()
    return 0


if __name__ == "__main__":
    sys.exit(main())
