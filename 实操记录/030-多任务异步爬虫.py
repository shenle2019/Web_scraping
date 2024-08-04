import asyncio
import time
import requests
# pip install aiohttp
import aiohttp  # 支持异步的网络请求模块
from lxml import etree

start = time.time()
urls = [
    'http://127.0.0.1:5000/bobo',
    'http://127.0.0.1:5000/jay',
    'http://127.0.0.1:5000/tom'
]

# 用于发起网络请求获取页面源码数据
# async def get_request(url):
#     #requests是不支持异步，使用一个可以支持异步的网络请求模块替换reqeusts就可以
#     response = requests.get(url=url)
#     page_text = response.text
#     return page_text

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

async def get_request(url):
    # 第一步：创建一个请求对象
    async with aiohttp.ClientSession() as sess:
        # 发起请求
        # sess.get(url=url,headers=headers,params=params,proxy='https://ip:port')
        # sess.post(url=url,headers=headers,data=data,proxy='https://ip:port')
        async with await sess.get(url=url) as response:
            # 获取响应数据:字符串的响应数据text()，二进制的响应数据read(),json()
            page_text = await response.text()
            return page_text

def parse(t):  # 用于数据解析
    page_text = t.result()
    tree = etree.HTML(page_text)
    ret = tree.xpath('//img/@src')[0]
    print(ret)

tasks = []
for url in urls:
    c = get_request(url)
    task = asyncio.ensure_future(c)
    task.add_done_callback(parse)
    tasks.append(task)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))

print('总耗时:', time.time() - start)