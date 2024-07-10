# -*- coding: utf-8 -*-

import requests
import json
# User-Agent:请求载体（浏览器，爬虫程序）的身份表示
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    # Referer
    'Referer': 'https://www.icve.com.cn/portal_new/course/course.html?keyvalue=%E6%97%85%E6%B8%B8'
}

### 指定url
url = 'https://www.icve.com.cn/portal/course/getNewCourseInfo'
data = {
    "kczy": "",
    "order": "",
    "printstate": "",
    "keyvalue": "旅游"
}

# 伪装了浏览器的请求头
response = requests.post(url=url, headers=header, data=data)
response.encoding = 'utf-8'
### 获取响应数据
page_text = response.json()

formatted_json = json.dumps(page_text, indent=4)
### print(formatted_json)

for dic in page_text['list']:
    title = dic['Title']
    name = dic['TeacherDisplayname']
    print(title, name)

