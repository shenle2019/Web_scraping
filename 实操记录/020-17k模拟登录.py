import requests
from lxml import etree

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer':'https://passport.17k.com/login/'
}

###          https://passport.17k.com/login
### login_url = 'https://passport.17k.com/login/'
login_url = 'https://passport.17k.com/login/'
data = {
    'user':'18665975275',
    'pass':'sl881010',
    'imgcode':'',
    'protocol':'on'
}

### https://passport.17k.com/login/?user=18665975275&pass=sl881010&imgcode=&protocol=on
session = requests.Session()
#请求的目的是为了获取cookie将其保存到session对象中
session.get(url=login_url,headers=headers,params=data)

#携带cookie向书架的页面进行请求发送，获取书架信息
#书架中的数据是动态加载的数据
### https://user.17k.com/ck/author2/shelf?page=1&appKey=2406394919
book_url = 'https://user.17k.com/ck/author2/shelf?page=1&appKey=2406394919'
page_text = session.get(url=book_url,headers=headers).json()

#解析书架信息
print(page_text)