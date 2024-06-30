# -*- coding: utf-8 -*-

import requests

### 指定url
url = 'https://www.eastmoney.com/'

### 发起请求
response = requests.get(url=url)
response.encoding = 'utf-8'
### 获取响应数据
page_text = response.text

### 保存数据
with open('dongfangcaifu.html','w',encoding='utf-8') as fp:
    fp.write(page_text)
