# -*- coding: utf-8 -*-

import requests

game_title = input('enter a game key:')
# 字典需要存放请求携带的所有的请求参数
params = {
    'q': game_title
}  # 请求参数的数量和字典的键值对的数量保持一致

# 指定url
url = 'https://game.51.com/search/action/game/'

### 发起请求
response = requests.get(url=url,params=params)
response.encoding = 'utf-8'
### 获取响应数据
page_text = response.text

### 保存数据
with open('games.html','w',encoding='utf-8') as fp:
    fp.write(page_text)
