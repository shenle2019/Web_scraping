import requests
from lxml import etree

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = 'https://www.aqistudy.cn/historydata/'
page_text = requests.get(url=url, headers=headers).text

tree = etree.HTML(page_text)
# 解析热门城市
hot_cities = tree.xpath('//div[@class="bottom"]/ul/li/a/text()')
# 解析全部城市
all_cities = tree.xpath('//div[@class="bottom"]/ul/div[2]/li/a/text()')
print('热门城市：', hot_cities)
print('全部城市：', all_cities)

# xpath(表达式1 | 表达式2)：满足表达式1或者表达式2的所有数据都会被定位提取到
cities = tree.xpath('//div[@class="bottom"]/ul/li/a/text() | //div[@class="bottom"]/ul/div[2]/li/a/text()')
print(cities)