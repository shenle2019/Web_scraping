#多线程数据爬取操作
#思路：
    #1.对不同的页码进行请求发送
    #2.批量将图片的链接和图片的名字进行数据解析
    #3.基于多线程的方式对所有图片进行网络请求，获取图片二进制的数据，持久化存储

import requests
from lxml import etree
from threading import Thread
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

#通过程序创建一个文件夹，用来存储图片
dirName = 'imgs_picdownload' #文件夹的名字
if not os.path.exists(dirName):
    #如果文件夹不存在则创建文件夹，如果存在则不创建
    os.mkdir(dirName)

#对不同页码进行网络请求,解析出所有图片的名字和下载链接
def get_img_msg():
    img_msg = [] #存储所有图片的信息
    for page in range(2,3):
        url = 'https://www.pkdoutu.com/zz/list?page=%d'%page
        page_text = requests.get(url=url,headers=headers).text
        tree = etree.HTML(page_text)
        a_list = tree.xpath('//*[@id="making-list"]/div[2]/a')
        for a in a_list:
            title = a.xpath('./p/text()')[0]+'.jpg'
            #此时应用了图片懒加载的技术，因此图片真正的链接存放在data-backup属性中
            src = a.xpath('./img/@data-backup')[0]
            dic = {
                'title':title,
                'src':src
            }
            img_msg.append(dic)
    return img_msg
#该函数是用于绑定给线程对象
def get_reqeust(dic):
    title = dic['title']
    src = dic['src']
    img_data = requests.get(url=src,headers=headers).content
    img_path = dirName + '/' + title
    with open(img_path,'wb') as fp:
        fp.write(img_data)
    print(title,':爬取保存成功！')

img_msg_list = get_img_msg()
#异步对所有的图片进行网络请求和持久化存储
for dic in img_msg_list:
    #给每一张图片创建一个线程
    t = Thread(target=get_reqeust,args=(dic,))
    t.start()
