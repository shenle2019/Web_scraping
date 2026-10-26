# -*- coding: utf-8 -*-
"""本地 mock 服务端：独立验证复刻 App 的签名/加密是否与课件算法一致。

仅限学习研究使用，不连接任何线上服务：
  - /x/report/click/android2      校验 AES-256-CBC 解密 + sha256(明文+盐)
  - /x/report/heartbeat/mobile    校验 md5(明文+四段盐)
  - /summary                      返回累计校验统计
"""
import hashlib
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from Crypto.Cipher import AES

KEY = b"fd6b639dbcff0c2a1b03b389ec763c4b"
IV = b"77b07a672d57d64c"
SHA256_SALT = b"9cafa6466a028bfb"
MD5_SALTS = ["560c52cc", "d288fed0", "45859ed1", "8bffd973"]
REQUIRED_HEADERS = ["Buvid", "Device-ID", "fp_local", "fp_remote"]

BASE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE, "verification_log.jsonl")
STATS = {"click": 0, "heartbeat": 0, "failed": 0}


def log_event(event):
    event["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def verify_click(raw):
    """解密 + 校验 sha256 签名，返回 (ok, detail, params)"""
    try:
        padded = AES.new(KEY, AES.MODE_CBC, IV).decrypt(raw)
        pad = padded[-1]
        if pad < 1 or pad > 16:
            raise ValueError("bad padding")
        text = padded[:-pad].decode("utf-8")
    except Exception as exc:
        return False, {"reason": "aes_decrypt_failed", "error": str(exc)}, {}

    if "&sign=" not in text:
        return False, {"reason": "sign_missing", "plain_head": text[:120]}, {}

    plain, sign = text.rsplit("&sign=", 1)
    expect = hashlib.sha256(plain.encode("utf-8") + SHA256_SALT).hexdigest()
    params = {}
    for kv in plain.split("&"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            params[k] = v
    detail = {
        "plain": plain,
        "sign": sign,
        "expect": expect,
        "sign_match": sign == expect,
        "param_count": len(params),
        "did": params.get("did", ""),
        "aid": params.get("aid"),
        "cid": params.get("cid"),
    }
    return sign == expect, detail, params


def verify_heartbeat(raw):
    """校验 md5(明文+四段盐) 与 session 形态，返回 (ok, detail, params)"""
    try:
        text = raw.decode("utf-8")
    except Exception as exc:
        return False, {"reason": "decode_failed", "error": str(exc)}, {}

    if "&sign=" not in text:
        return False, {"reason": "sign_missing"}, {}

    plain, sign = text.rsplit("&sign=", 1)
    expect = hashlib.md5(
        plain.encode("utf-8") + "".join(MD5_SALTS).encode("utf-8")
    ).hexdigest()

    params = {}
    for kv in plain.split("&"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            params[k] = v

    session = params.get("session", "")
    session_ok = len(session) == 40 and all(c in "0123456789abcdef" for c in session)
    detail = {
        "plain": plain,
        "sign": sign,
        "expect": expect,
        "sign_match": sign == expect,
        "session": session,
        "session_shape_ok": session_ok,
        "played_time": params.get("played_time"),
        "total_time": params.get("total_time"),
        "paused_time": params.get("paused_time"),
    }
    return sign == expect and session_ok, detail, params


class Handler(BaseHTTPRequestHandler):
    server_version = "BiliMock/1.0"

    def log_message(self, fmt, *args):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _headers_of_interest(self):
        return {h: self.headers.get(h, "") for h in REQUIRED_HEADERS + ["session_id", "User-Agent"]}

    def do_GET(self):
        if self.path == "/summary":
            self._send({"code": 0, "stats": STATS, "log": LOG_PATH})
        elif self.path == "/health":
            self._send({"code": 0, "ok": True})
        else:
            self._send({"code": 404}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        headers = self._headers_of_interest()
        missing = [h for h in REQUIRED_HEADERS if not headers.get(h)]

        if self.path.endswith("/click/android2"):
            ok, detail, params = verify_click(raw)
            if missing:
                ok = False
                detail["reason"] = "missing_headers"
            STATS["click" if ok else "failed"] += 1
            log_event({"endpoint": "click", "ok": ok, "bytes": len(raw),
                       "missing_headers": missing, "headers": headers, "detail": detail})
            print("[click] ok=%s sign=%s.. cipher=%dB" % (ok, detail.get("sign", "")[:12], len(raw)))
            self._send({"code": 0 if ok else -1, "verified": ok, "endpoint": "click",
                        "missing_headers": missing,
                        "sign": detail.get("sign"), "param_count": detail.get("param_count")})
            return

        if self.path.endswith("/heartbeat/mobile"):
            ok, detail, params = verify_heartbeat(raw)
            if missing:
                ok = False
                detail["reason"] = "missing_headers"
            STATS["heartbeat" if ok else "failed"] += 1
            log_event({"endpoint": "heartbeat", "ok": ok, "bytes": len(raw),
                       "missing_headers": missing, "headers": headers, "detail": detail})
            print("[heartbeat] ok=%s sign=%s.. session=%s.."
                  % (ok, detail.get("sign", "")[:12], detail.get("session", "")[:12]))
            self._send({"code": 0 if ok else -1, "verified": ok, "endpoint": "heartbeat",
                        "missing_headers": missing,
                        "sign": detail.get("sign"), "session_shape_ok": detail.get("session_shape_ok")})
            return

        self._send({"code": 404}, 404)


class MockServer(ThreadingHTTPServer):
    allow_reuse_address = True

    def server_bind(self):
        # 跳过 HTTPServer.server_bind 里的 socket.getfqdn()：
        # 本机主机名为中文时 Windows 会抛 UnicodeDecodeError
        from socketserver import TCPServer
        TCPServer.server_bind(self)
        self.server_name = "localhost"
        self.server_port = self.server_address[1]


if __name__ == "__main__":
    srv = MockServer(("0.0.0.0", 8899), Handler)
    print("mock server listening on 0.0.0.0:8899, log ->", LOG_PATH)
    srv.serve_forever()
