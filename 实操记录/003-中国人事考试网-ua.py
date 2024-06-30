# -*- coding: utf-8 -*-

import requests

### 指定url
url = 'http://www.cpta.com.cn/'

# User-Agent:请求载体（浏览器，爬虫程序）的身份表示
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
# 伪装了浏览器的请求头
response = requests.get(url=url, headers=header)
response.encoding = 'utf-8'
### 获取响应数据
page_text = response.text

### 保存数据
with open('renshi.html','w',encoding='utf-8') as fp:
    fp.write(page_text)
