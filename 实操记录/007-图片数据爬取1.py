# -*- coding: utf-8 -*-

import requests

### https://www.douyin.com/note/7150188465496263977


url = 'https://preview.qiantucdn.com/58pic/37/Jp/9N/eC/yzkj10w3a4bf56ehvtudrxpic7s8oml9_PIC2018_png_aiys_PIC2018.jpg%21w1024_new_small_1'
response = requests.get(url=url)

img_data = response.content

with open('1.jpg', 'wb') as fp:
    fp.write(img_data)