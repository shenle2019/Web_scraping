# -*- coding: utf-8 -*-
"""巨量IP 代理配置模板（可提交到 Git 仓库）

使用方法：
    1. 复制本文件为同目录下的 proxy_config_local.py
    2. 把下面三项替换为你在巨量IP会员中心的真实信息
    3. proxy_config_local.py 已在 .gitignore 中排除，不会被提交

凭证获取：巨量IP会员中心 -> 动态代理产品管理 -> 生成提取链接
"""

# 业务编号（会员中心产品管理页可见）
TRADE_NO = "你的业务编号 trade_no"

# API 密钥
API_KEY = "你的API密钥 key"

# 提取链接：在会员中心"生成提取链接"工具中生成后，整体粘贴到此处
# 建议参数：result_type=text、split=1、num 按需（1~100）
EXTRACT_URL = (
    "http://v2.api.juliangip.com/company/postpay/getips"
    "?auto_white=1&num=10&pt=1&result_type=text&split=1"
    "&trade_no=你的业务编号&sign=会员中心生成的签名"
)
