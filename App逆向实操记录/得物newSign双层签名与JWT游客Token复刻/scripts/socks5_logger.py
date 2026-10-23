# -*- coding: utf-8 -*-
"""socks5_logger.py —— 极简 SOCKS5 代理（无认证，带日志），配合 SocksDroid 验证旁路抓包。

SocksDroid 在手机上建 VPN，把 App 的 TCP 连接转发到本机 1080，即使 App 写了 Proxy.NO_PROXY
也逃不掉 socket 层。本脚本只打印目标地址并转发字节流，不记录任何内容。

用法：python socks5_logger.py
手机 SocksDroid 配置：SOCKS5 服务器 192.168.31.220，端口 1080。

仅限学习研究，禁止商用。
"""
import socket
import struct
import threading

LISTEN = ("0.0.0.0", 1080)


def log(msg):
    print("[socks] " + msg, flush=True)


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


def read_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("closed")
        buf += chunk
    return buf


def handle(conn, addr):
    try:
        head = read_exact(conn, 2)
        nmethods = head[1]
        read_exact(conn, nmethods)
        conn.sendall(b"\x05\x00")
        ver_cmd = read_exact(conn, 2)
        if ver_cmd[1] != 1:
            conn.close()
            return
        # SOCKS5 请求头是 VER CMD RSV ATYP，RSV 占一字节，漏读会把后面的
        # ATYP 当成 RSV，导致握手卡死（本次踩过）
        read_exact(conn, 1)
        atyp = read_exact(conn, 1)[0]
        if atyp == 1:
            host = socket.inet_ntoa(read_exact(conn, 4))
        elif atyp == 3:
            length = read_exact(conn, 1)[0]
            host = read_exact(conn, length).decode("utf-8", "ignore")
        else:
            host = socket.inet_ntop(socket.AF_INET6, read_exact(conn, 16))
        port = struct.unpack("!H", read_exact(conn, 2))[0]
        log("CONNECT %s:%d <- %s" % (host, port, addr[0]))
        remote = socket.create_connection((host, port), timeout=10)
        conn.sendall(b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack("!H", 0))
        threading.Thread(target=pipe, args=(remote, conn), daemon=True).start()
        pipe(conn, remote)
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
    log("SOCKS5 已监听 %s:%d" % LISTEN)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
