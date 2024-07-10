# -*- coding: utf-8 -*-

import requests
import json
# User-Agent:请求载体（浏览器，爬虫程序）的身份表示
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

### 指定url
url = 'https://www.xiachufang.com/search/'

title = input('请输入菜名：')
params = {
    "keyword": title,
    "cat": "1001"
}

# 伪装了浏览器的请求头
response = requests.get(url=url, headers=header, params=params)
response.encoding = 'utf-8'
### 获取响应数据
page_text = response.text

### 保存数据
filename = title + '.html'
with open(filename,'w',encoding='utf-8') as fp:
    fp.write(page_text)

