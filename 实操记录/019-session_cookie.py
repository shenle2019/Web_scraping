import requests

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}
# param = {
#     # 如果遇到了动态变化的请求参数？必须经过测试才知道需不需要处理
#     "since_id": "-1",
#     "max_id": "553059",  # 动态变化的请求参数
#     "size": "25"
# }

# url = 'https://xueqiu.com/statuses/hot/listV2.json'
url = 'https://xueqiu.com/'

# session对象会实时保存跟踪服务器端给客户端创建的cookie
# 创建一个session对象
session = requests.Session()  # 空白的session对象
first_url = 'https://xueqiu.com/'
# 使用session对象进行请求发送：如果该次请求时，服务器端给客户端创建cookie的话，则该cookie就会被保存seesion对象中
session.get(url=first_url, headers=headers)
# 使用保存了cookie的session对象进行后续请求发送
ret = session.get(url=url, headers=headers)
ret.encoding = 'utf-8'
### print(ret.text)

### 保存数据
with open('XUEQIU.html','w',encoding='utf-8') as fp:
    fp.write(ret.text)
