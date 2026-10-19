# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""金树林接口探测：DNS 解析、TCP 端口、HTTPS 接口与 robots.txt 可达性。

课件案例（2023 年录制）的目标域名是 miappshop.jshulin.com。
本脚本用于复刻前先确认目标当前是否在线；探测失败时如实记录，不伪造结果。
"""
import socket
import ssl
import datetime

import requests
import urllib3

urllib3.disable_warnings()

HOST = "miappshop.jshulin.com"
URL_PHONE_CODE = "https://%s/memberLogin/phoneCode" % HOST
URL_ROBOTS = "https://%s/robots.txt" % HOST


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def dns_lookup():
    print("\n=== 1. DNS 解析 %s ===" % HOST)
    try:
        infos = socket.getaddrinfo(HOST, 443)
        ips = sorted({item[4][0] for item in infos})
        print("解析结果:", ", ".join(ips))
        return ips
    except Exception as exc:
        print("[DNS 失败] %s" % exc)
        return []


def tcp_check(ips, port):
    print("\n=== 2. TCP %s:%s ===" % (HOST, port))
    for ip in ips:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((ip, port))
            print("[%s] %s:%s 连接成功" % (now(), ip, port))
        except Exception as exc:
            print("[%s] %s:%s 连接失败 -> %s" % (now(), ip, port, exc))
        finally:
            sock.close()


def http_probe(url, params=None, label=""):
    print("\n=== 3. HTTPS 请求 %s %s ===" % (label, url))
    try:
        res = requests.get(url, params=params, verify=False, timeout=15,
                           headers={"user-agent": "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36"})
        print("[%s] HTTP %s" % (now(), res.status_code))
        print("响应片段:", res.text[:300].replace("\n", " "))
        return True
    except Exception as exc:
        print("[%s] 请求失败 -> %s" % (now(), exc))
        return False


def main():
    print("[%s] 开始探测金树林案例目标站点" % now())
    ips = dns_lookup()
    if ips:
        tcp_check(ips, 443)
        tcp_check(ips, 80)
    http_probe(URL_PHONE_CODE, params={"phone": "13800000000", "serviceType": 6}, label="phoneCode")
    http_probe(URL_ROBOTS, label="robots.txt")


if __name__ == "__main__":
    main()
