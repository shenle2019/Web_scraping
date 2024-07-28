import requests
from lxml import etree

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer':'https://passport.17k.com/login/',
    'Upgrade-Insecure-Requests':'1',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Connection':'keep-alive',
    'Host':'passport.17k.com',
    'Sec-Ch-Ua-Mobile':'?0',
    'Sec-Ch-Ua-Platform':'"Windows"',
    'Sec-Fetch-Dest':'document',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-Site':'same-origin',
    'Sec-Fetch-User':'?1'
}

###          https://passport.17k.com/login
### login_url = 'https://passport.17k.com/login/'
login_url = 'https://passport.17k.com/login/'
params = {
    'user':'18665975275',
    'pass':'sl881010',
    'imgcode':'',
    'protocol':'on'
}

### 17k 网站已经不能用了，2024.07.21 mark。
### https://passport.17k.com/login/?user=18665975275&pass=sl881010&imgcode=&protocol=on
session = requests.Session()
#请求的目的是为了获取cookie将其保存到session对象中
response = session.get(url=login_url,headers=headers,params=params)
print(response.content.decode("utf-8"))

#携带cookie向书架的页面进行请求发送，获取书架信息
#书架中的数据是动态加载的数据
### https://user.17k.com/ck/author2/shelf?page=1&appKey=2406394919
book_url = 'https://user.17k.com/ck/author2/shelf?page=1&appKey=2406394919'
page_text = session.get(url=book_url,headers=headers).json()

#解析书架信息
print(page_text)