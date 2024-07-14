import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = 'https://bixuejian.5000yan.com/'
# 获取了首页对应的页面源码数据
response = requests.get(url=url, headers=headers)
response.encoding = 'utf-8'
page_text = response.text

# 在首页页面源码数据中进行数据解析（章节的标题）
soup = BeautifulSoup(page_text, 'lxml')

# 所有的a标签定位保存到了a_list这个列表中
### print(soup)
li_tags = soup.find_all('li', class_='p-2')
a_list = [tag.find('a') for tag in li_tags]
### print(a_list)

### a_list = soup.select('.mx-auto  row row-cols-1 row-cols-sm-2 row-cols-lg-3> li > a')

for a in a_list:
    # 章节的标题
    title = a.string
    print(title)
    detail_url = a['href']  # 章节详情页的url
    # 对详情页的url进行请求，为了获取详情页的页面源码数据，将章节内容进行解析
    detail_response = requests.get(url=detail_url, headers=headers)
    detail_response.encoding = 'utf-8'
    detail_page_text = detail_response.text
    # 解析详情页，将章节内容进行提取
    detail_soup = BeautifulSoup(detail_page_text, 'lxml')
    div_tag = detail_soup.find('div', class_='grap')
    # 章节内容
    content = div_tag.text

    fileName = 'xiaoshuo/' + title + '.txt'  # xiaoshuo/章节1.txt
    with open(fileName, 'w', encoding='utf-8') as fp:
        fp.write(title + '\n' + content)
    print(title, ':爬取保存成功！')