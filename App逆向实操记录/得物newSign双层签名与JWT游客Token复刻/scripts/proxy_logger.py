# -*- coding: utf-8 -*-
"""proxy_logger.py —— 极简 HTTP 正向代理（带日志），用于验证 App 是否走了系统代理。

仅监听本机 8899，转发到内网自建服务和本机可达主机；不记录任何凭证。
用法：python proxy_logger.py
然后在手机上设置：设置 → WLAN → 修改网络 → 代理 手动 → 192.168.31.220:8899

仅限学习研究，禁止商用。
"""
import socket
import threading

LISTEN = ("0.0.0.0", 8899)


def log(msg):
    print("[proxy] " + msg, flush=True)


def pipe(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass


def handle(conn, addr):
    conn.settimeout(15)
    buf = b""
    try:
        while b"\r\n\r\n" not in buf:
            chunk = conn.recv(65536)
            if not chunk:
                return
            buf += chunk
        head, _, rest = buf.partition(b"\r\n\r\n")
        lines = head.decode("iso-8859-1", "replace").split("\r\n")
        method, target, version = lines[0].split(" ", 2)
        log("%s %s <- %s" % (method, target, addr[0]))

        if method.upper() == "CONNECT":
            host, _, port = target.partition(":")
            remote = socket.create_connection((host, int(port or 443)), timeout=10)
            conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            threading.Thread(target=pipe, args=(remote, conn), daemon=True).start()
            pipe(conn, remote)
            remote.close()
            return

        # 绝对 URI 形式：GET http://host:port/path HTTP/1.1
        without_scheme = target.split("://", 1)[-1]
        hostport, _, path = without_scheme.partition("/")
        host, _, port = hostport.partition(":")
        port = int(port or 80)
        remote = socket.create_connection((host, port), timeout=10)
        forward = ["%s /%s %s" % (method, path, version)]
        for line in lines[1:]:
            if line.lower().startswith(("proxy-connection", "connection", "keep-alive")):
                continue
            forward.append(line)
        remote.sendall(("\r\n".join(forward) + "\r\n\r\n").encode("iso-8859-1") + rest)
        pipe(remote, conn)
        remote.close()
    except Exception as exc:
        log("出错 %s: %s" % (addr, exc))
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(LISTEN)
    srv.listen(50)
    log("HTTP 代理已监听 %s:%d" % LISTEN)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
