# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
01_提取Charles抓包请求.py
目标：从 Charles Auto Save 导出的会话文件(.chls, xstream 二进制序列化格式)中，
      提取车智赢 App 登录请求(login.ashx)的 URL 与请求体参数，重点观察 pwd 字段。
用法：python 01_提取Charles抓包请求.py [会话文件路径]
      缺省读取 ../capture/车智赢登录抓包会话.chls
"""
import re
import sys
from urllib.parse import unquote, parse_qs

DEFAULT_CHLS = "../capture/车智赢登录抓包会话.chls"
LOGIN_PATH = "/tradercloud/sealed/login/login.ashx"
LOGIN_HOST = "dealercloudapi.che168.com"


def extract_login_request(raw: bytes) -> dict:
    """.chls 中字符串段未压缩，直接按 UTF-8 解码后正则定位 login.ashx 请求体"""
    text = raw.decode("utf-8", errors="ignore")
    result = {}
    idx = text.find(LOGIN_PATH)
    if idx < 0:
        return result
    near = text[idx: idx + 6000]
    # 请求体形如 appid=atc.android&_sign=xxx&...&pwd=xxx&username=18953675221
    m = re.search(r"([a-zA-Z0-9_%\-\.=&]+username=[0-9]{6,})", near)
    if not m:
        return result
    body = m.group(1)
    # xstream 二进制分隔符可能残留在首个参数名前(如 "_appid"), 从真实字段处截断
    pos = body.find("appid=")
    if pos > 0:
        body = body[pos:]
    result["host"] = LOGIN_HOST
    result["path"] = LOGIN_PATH
    result["method"] = "POST"
    result["body"] = body
    result["params"] = parse_qs(unquote(body))
    # 响应体形如 {"returncode":2040007,"message":"账号或密码错误"}
    r = re.search(r'(\{"returncode":\d+,"message":"[^"]*"\})', text)
    if r:
        result["response"] = r.group(1)
    return result


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CHLS
    with open(path, "rb") as f:
        raw = f.read()
    info = extract_login_request(raw)
    if not info:
        print("未在会话文件中找到 login.ashx 请求")
        sys.exit(1)
    print("=" * 66)
    print(f"[请求] POST https://{info['host']}{info['path']}")
    print(f"[请求体] {info['body']}")
    print("-" * 66)
    print("[参数明细]")
    for k, v in info["params"].items():
        val = v[0] if len(v) == 1 else v
        if k == "udid":
            val = val[:20] + "...(截断)"
        print(f"  {k:14s} = {val}")
    print("-" * 66)
    print("[响应体]", info.get("response", "(未捕获到响应体)"))
    print("=" * 66)
    pwd = info["params"].get("pwd", [""])[0]
    print(f"[关键观察] pwd={pwd}  -> 32位十六进制, 疑似 MD5 摘要")
    print("下一步: jadx 反编译 apk, 搜索 'pwd' 定位加密函数(见 02_验证MD5.py)")


if __name__ == "__main__":
    main()
