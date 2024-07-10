# -*- coding: utf-8 -*-

import requests

# User-Agent:请求载体（浏览器，爬虫程序）的身份表示
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    # Referer
    'Referer': 'https://www.sogou.com/'
}

### 指定url
url = 'https://sogou.com/web'

title = input('请输入搜索项：')

### 实际这里只需要一个query名称就行了 。
params = {
    'query': title,
    '_asf': 'www.sogou.com',
    '_ast':'',
    'w': '01019900',
    'p': '40040100',
    'ie': 'utf8',
    'from': 'index-nologin',
    's_from': 'index',
    'sut': '1093',
    'sst0': '1720614807035',
    'lkt': '0,0,0',
    'sugsuv': '1720610823004892',
    'sugtime': '1720614807035'
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

