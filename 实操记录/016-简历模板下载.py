from lxml import etree
import requests
import os

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
url = 'https://sc.chinaz.com/jianli/free.html'
response = requests.get(url=url,headers=headers)
response.encoding = 'utf-8'
page_text = response.text
#数据解析:简历名称+详情页的url
tree = etree.HTML(page_text)

# 新建一个文件夹
dirName = 'jianlis'
if not os.path.exists(dirName):  # 如果文件夹不存在，则新建，否则不新建
    os.mkdir(dirName)

### //*[@id="container"] div的上一级。
div_list = tree.xpath('//*[@id="container"]/div')
for div in div_list:
    title = div.xpath('./p/a/text()')[0]+'.rar'
    detail_url = div.xpath('./p/a/@href')[0]
    ### print(title,detail_url)
    ### 1年经验游戏运营个人简历模板.rar https:https://sc.chinaz.com/jianli/240112113120.htm
    #对详情页的url发起请求
    detail_page_text = requests.get(url=detail_url,headers=headers).text
    #数据解析：下载地址
    tree = etree.HTML(detail_page_text)
    ### //*[@id="down"]/div[2]/ul/li[1]/a
    download_url = tree.xpath('//*[@id="down"]/div[2]/ul/li[1]/a/@href')[0]
    #在下载请求建立模板
    data = requests.get(url=download_url,headers=headers).content
    download_path = dirName + '/' + title
    print(download_path)
    with open(download_path,'wb') as fp:
        fp.write(data)
    print(title,'保存下载成功！')