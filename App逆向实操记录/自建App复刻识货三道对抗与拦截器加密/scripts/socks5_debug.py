# -*- coding: utf-8 -*-
"""socks5_debug.py —— 带逐步日志的 SOCKS5 代理，用来定位握手卡在哪一步。

用法：python socks5_debug.py [port]
仅限学习研究，禁止商用。
"""
import socket
import struct
import sys
import threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 1081


def log(msg):
    print("[dbg] " + msg, flush=True)


def read_exact(sock, n, step):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        log("%s recv %d bytes: %s" % (step, len(chunk), chunk.hex()))
        if not chunk:
            raise ConnectionError("closed at " + step)
        buf += chunk
    return buf


def handle(conn, addr):
    log("accept from %s" % (addr,))
    try:
        head = read_exact(conn, 2, "greeting")
        nmethods = head[1]
        read_exact(conn, nmethods, "methods")
        conn.sendall(b"\x05\x00")
        log("sent method selection")
        ver_cmd = read_exact(conn, 2, "request")
        log("ver_cmd=%s" % ver_cmd.hex())
        atyp = read_exact(conn, 1, "atyp")[0]
        if atyp == 1:
            host = socket.inet_ntoa(read_exact(conn, 4, "ipv4"))
        elif atyp == 3:
            length = read_exact(conn, 1, "domain-len")[0]
            host = read_exact(conn, length, "domain").decode("utf-8", "ignore")
        else:
            host = socket.inet_ntop(socket.AF_INET6, read_exact(conn, 16, "ipv6"))
        port = struct.unpack("!H", read_exact(conn, 2, "port"))[0]
        log("CONNECT %s:%d" % (host, port))
        remote = socket.create_connection((host, port), timeout=10)
        conn.sendall(b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack("!H", 0))
        while True:
            data = conn.recv(65536)
            if not data:
                break
            remote.sendall(data)
        remote.close()
    except Exception as exc:
        log("出错 %s: %s" % (addr, exc))
    finally:
        conn.close()


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT))
    srv.listen(50)
    log("listening %d" % PORT)
    while True:
        c, a = srv.accept()
        threading.Thread(target=handle, args=(c, a), daemon=True).start()


if __name__ == "__main__":
    main()
