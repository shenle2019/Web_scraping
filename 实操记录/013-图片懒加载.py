import requests
from lxml import etree
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
url = 'https://sc.chinaz.com/tupian/meinvtupian.html'
page_text = requests.get(url=url,headers=headers).text

tree = etree.HTML(page_text)

### /html/body/div[3]/div[2]
div_list = tree.xpath('/html/body/div[3]/div[2]/div')
for div in div_list:
    src = 'https:'+div.xpath('./img/@data-original')[0]
    print(src)