# -*- coding: utf-8 -*-

import requests
import json
# User-Agent:请求载体（浏览器，爬虫程序）的身份表示
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    # Referer
    'Referer': 'http://www.kfc.com.cn/kfccda/storelist/index.aspx'
}

### city = input('请输入城市：')
keywords = input('请输入关键字：')

for page in range(1,5):
    ### 指定url
    url = 'http://www.kfc.com.cn/kfccda/ashx/GetStoreList.ashx?op=keyword'
    data = {
    "cname": '杭州',
    "pid": "",
    "keyword": keywords,
    "pageIndex": page,
    "pageSize":10
    }

    # 伪装了浏览器的请求头
    response = requests.post(url=url, headers=header, data=data)
    response.encoding = 'utf-8'
    ### 获取响应数据

    # print(response.text)
    page_text = response.json()
    formatted_json = json.dumps(page_text, indent=4)
    ### print(formatted_json)

    for dic in page_text['Table1']:
        storeName = dic['storeName']
        addressDetail = dic['addressDetail']
        print(storeName, addressDetail)

