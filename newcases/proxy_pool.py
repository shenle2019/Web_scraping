# -*- coding: utf-8 -*-
"""高匿代理池通用模块（巨量IP · 动态代理 · 按量付费 · 3分钟时效）

本项目所有本地爬虫统一通过本模块获取代理后发起请求，不使用本机 IP 直连。

准备配置：
    复制同目录 proxy_config_example.py 为 proxy_config_local.py，填入真实凭证
    （proxy_config_local.py 已被 .gitignore 排除，不会提交到仓库）

用法：
    from proxy_pool import get_proxies, ProxyPool

    # 便捷用法：随机取一个可用代理
    proxies = get_proxies()
    response = requests.get(url, headers=headers, proxies=proxies)

    # 自定义池（可选）
    pool = ProxyPool(pool_size=20)
    proxies = pool.get_proxies()

    # Playwright 用法
    proxy = pool.get_playwright_proxy()
    browser = p.chromium.launch(proxy=proxy)
"""

import random
import re
import threading
import time

import requests

try:
    from proxy_config_local import EXTRACT_URL, TRADE_NO, API_KEY
except ImportError:
    raise SystemExit(
        "未找到本地代理配置 proxy_config_local.py\n"
        "请复制 proxy_config_example.py 为 proxy_config_local.py 并填写巨量IP凭证"
    )

# ---------------- 默认参数 ----------------
DEFAULT_POOL_SIZE = 10          # 每次补货提取的 IP 数量（1~100）
IP_TTL = 180                    # 单批 IP 存活时长（秒），本套餐为 3 分钟
IP_TTL_MARGIN = 10              # 过期余量（秒），提前丢弃即将过期的 IP
REQUEST_TIMEOUT = 10            # 普通请求超时
FETCH_TIMEOUT = 20              # 提取接口超时

# 出口 IP 检测地址（按顺序尝试，返回内容含当前出口 IP）
IP_CHECK_URLS = (
    "https://myip.ipip.net",
    "http://www.cip.cc/",
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
}


class ProxyPool:
    """线程安全的高匿代理池"""

    def __init__(self, pool_size=DEFAULT_POOL_SIZE, extract_url=None):
        self.pool_size = pool_size
        self.extract_url = extract_url or EXTRACT_URL
        self._ips = []          # [(ip:port, 提取时间), ...]
        self._lock = threading.Lock()

    # ---------------- 提取 ----------------
    def _build_url(self, num):
        """把提取链接中的 num 参数替换为指定数量（其余参数保持原样）"""
        return re.sub(r"num=\d+", "num=%d" % num, self.extract_url)

    def fetch_ips(self, num=None):
        """调用巨量IP接口提取一批新 IP，返回 ["ip:port", ...]"""
        num = num or self.pool_size
        url = self._build_url(num)
        response = requests.get(url, headers=_HEADERS, timeout=FETCH_TIMEOUT)
        text = response.text.strip()
        if response.status_code != 200 or not text or text.startswith("ERROR"):
            raise RuntimeError("提取代理失败：%s" % text[:200])

        ips = [line.strip() for line in text.splitlines() if line.strip()]
        with self._lock:
            now = time.time()
            self._ips = [(ip, now) for ip in ips]
        return ips

    # ---------------- 取用 ----------------
    def _get_one(self):
        """取一个未过期的 ip:port，池空时自动补货"""
        with self._lock:
            now = time.time()
            self._ips = [
                (ip, t) for ip, t in self._ips
                if now - t < IP_TTL - IP_TTL_MARGIN
            ]
            if self._ips:
                return random.choice(self._ips)[0]

        # 池子空了：提取新一批再取
        self.fetch_ips()
        with self._lock:
            if not self._ips:
                raise RuntimeError("代理池补货失败：未提取到任何 IP")
            return random.choice(self._ips)[0]

    def get_proxies(self):
        """随机取一个代理，返回 requests 可直接使用的 proxies 字典"""
        proxy_url = "http://" + self._get_one()
        return {"http": proxy_url, "https": proxy_url}

    def get_playwright_proxy(self):
        """返回 Playwright launch(proxy=...) 可用的代理配置（白名单模式无需账密）"""
        return {"server": "http://" + self._get_one()}

    # ---------------- 验证 ----------------
    def verify(self, ip_port, timeout=REQUEST_TIMEOUT):
        """通过指定代理访问出口检测服务

        返回出口 IP 信息文本；代理不可用时返回 None。
        """
        proxy_url = "http://" + ip_port
        proxies = {"http": proxy_url, "https": proxy_url}
        for check_url in IP_CHECK_URLS:
            try:
                response = requests.get(
                    check_url, headers=_HEADERS, proxies=proxies, timeout=timeout
                )
                if response.status_code == 200 and response.text.strip():
                    return _parse_ip_text(response.text.strip())
            except requests.RequestException:
                continue
        return None

    def verify_all(self):
        """批量验证当前池中的 IP，返回 {ip:port: 出口信息或 None}"""
        with self._lock:
            ips = [ip for ip, _ in self._ips]
        return {ip: self.verify(ip) for ip in ips}


def _parse_ip_text(text):
    """规整出口检测结果：HTML 页面提取 IP，纯文本截取关键行"""
    if len(text) > 200:
        match = re.search(r"\d{1,3}(?:\.\d{1,3}){3}", text)
        return match.group(0) if match else text[:100]
    return text


# 模块级默认池（便捷函数使用）
_default_pool = None
_default_lock = threading.Lock()


def get_proxies():
    """便捷函数：从默认代理池随机取一个 requests 代理字典"""
    global _default_pool
    if _default_pool is None:
        with _default_lock:
            if _default_pool is None:
                _default_pool = ProxyPool()
    return _default_pool.get_proxies()
