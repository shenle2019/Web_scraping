import requests
from lxml import etree
import time
import random

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 构建一个代理池（有很多不同的代理服务器），直接从网页读取下来。
proxy_url = 'http://webapi.http.zhimacangku.com/getip?num=80&type=3&pro=&city=0&yys=0&port=11&pack=337730&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
page_text = requests.get(url=proxy_url, headers=headers).text
proxy_list = []  # 代理池
for ips in page_text.split('\n')[0:-1]:
    dic = {}
    dic['https'] = ips.strip()
    proxy_list.append(dic)

for page in range(1, 5001):
    print('正在爬取第%d页的ip数据......' % page)
    # 生成不同页码对应的url
    url = 'https://www.kuaidaili.com/free/inha/%d/' % page
    ### random.choice(proxy_list) 随机获取一个代理ip来做这个事情。
    page_text = requests.get(url=url, headers=headers, proxies=random.choice(proxy_list)).text
    time.sleep(0.5)
    tree = etree.HTML(page_text)
    ip = tree.xpath('//*[@id="list"]/div[1]/table/tbody/tr[1]/td[1]/text()')[0]
    print(ip)