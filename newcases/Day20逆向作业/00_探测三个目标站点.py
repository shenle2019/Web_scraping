# -*- coding: utf-8 -*-
"""Day20 作业：三个目标站点接口探测（第一轮摸底）"""
import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA}


def probe(name, method, url, **kw):
    print("=" * 72)
    print("[%s] %s %s" % (name, method, url))
    try:
        if method == "GET":
            r = requests.get(url, headers=HEADERS, timeout=20, **kw)
        else:
            r = requests.post(url, headers=HEADERS, timeout=20, **kw)
    except Exception as e:
        print("  请求异常:", type(e).__name__, e)
        return None
    print("  HTTP %s | %d bytes | Content-Type: %s"
          % (r.status_code, len(r.content), r.headers.get("Content-Type", "")))
    print("  响应前 400 字符:")
    print("  " + r.text[:400].replace("\n", " "))
    return r


# 案例1：建设库（页码对应页面数据）
probe("案例1-建设库搜索页", "GET",
      "https://www.jiansheku.com/search/enterprise/p3/")

# 案例2：招标网（数据加密接口，解密）
probe("案例2-招标网搜索页", "GET",
      "https://search.bidcenter.com.cn/search?keywords=%e6%9c%8d%e5%8a%a1%e5%99%a8")

# 案例3：企名片（推荐信息接口）
probe("案例3-企名片接口", "POST",
      "https://vipapi.qimingpian.cn/HomePage/recommendInfo",
      data={"page": "1", "num": "10"})
