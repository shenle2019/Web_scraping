# -*- coding: utf-8 -*-
"""巨量IP 高匿代理池 · 可行性测试脚本

测试内容：
  1. 提取接口 —— 能否从巨量IP拿到高匿 IP 列表
  2. 直连对照 —— 记录本机真实出口 IP 作为对照
  3. 逐个验证 —— 提取到的 IP 能否转发请求、能否隐藏本机 IP

运行方式（任选其一）：
    python newcases/01_test_proxy.py
    cd newcases && python 01_test_proxy.py
"""
import requests

from proxy_pool import IP_CHECK_URLS, ProxyPool


def direct_ip():
    """直连检测本机真实出口 IP，作为对照"""
    try:
        resp = requests.get(IP_CHECK_URLS[0], timeout=15)
        return resp.text.strip()
    except requests.RequestException as exc:
        return "检测失败：%s" % exc


def main():
    pool = ProxyPool()

    print("=" * 64)
    print("步骤 1/3：调用巨量IP提取接口")
    print("=" * 64)
    ips = pool.fetch_ips()
    print("提取成功，共 %d 个 IP：" % len(ips))
    for ip in ips:
        print("   " + ip)

    print()
    print("=" * 64)
    print("步骤 2/3：直连对照（本机真实出口 IP）")
    print("=" * 64)
    print("本机直连：" + direct_ip())

    print()
    print("=" * 64)
    print("步骤 3/3：逐个验证代理连通性与匿名性")
    print("=" * 64)
    ok = 0
    for ip in ips:
        info = pool.verify(ip)
        if info:
            ok += 1
            print("[可用] %-21s 出口：%s" % (ip, info))
        else:
            print("[失败] %s" % ip)
    print("-" * 64)
    print("结果：%d/%d 个代理可用" % (ok, len(ips)))

    print()
    print("=" * 64)
    print("测试完成。日常用法示例：")
    print("    from proxy_pool import get_proxies")
    print("    proxies = get_proxies()")
    print("    requests.get(url, headers=headers, proxies=proxies)")
    print("=" * 64)


if __name__ == "__main__":
    main()
