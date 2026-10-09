# -*- coding: utf-8 -*-
"""ks.wangxiao.cn 爬虫本地配置模板

使用方法：
    1. 复制本文件为同目录下的 ks_config_local.py
    2. 在浏览器登录 https://ks.wangxiao.cn/ 后（微信扫码或账号登录），
       F12 -> 网络(Network) -> 刷新页面 -> 任选一个请求 -> 复制请求头中的 Cookie 整串
    3. 将 Cookie 粘贴到 COOKIE 变量中

注意：ks_config_local.py 已被 .gitignore 排除，不会提交到仓库。
"""

# 登录后的 Cookie 字符串（必须带 token 和 userInfo 两个关键项）
COOKIE = "在此粘贴浏览器里复制出来的完整Cookie"

# MySQL 数据库连接配置
MYSQL = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "db": "wangxiao",
    "charset": "utf8mb4",
}
