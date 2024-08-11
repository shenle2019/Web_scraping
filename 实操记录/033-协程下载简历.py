import asyncio
import requests
from lxml import etree
import os
import aiohttp

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

#通过程序创建一个文件夹，用来存储图片
dirName = 'jianli_download' #文件夹的名字
if not os.path.exists(dirName):
    #如果文件夹不存在则创建文件夹，如果存在则不创建
    os.mkdir(dirName)

#对不同页码进行网络请求,解析出所有图片的名字和下载链接
def get_jianli_msg():
    jianli_msg = [] #存储所有图片的信息
    for page in range(2,4):
        url = 'https://sc.chinaz.com/jianli/free_%d.html'%page
        response = requests.get(url=url,headers=headers)
        response.encoding = 'utf-8'
        page_text = response.text
        tree = etree.HTML(page_text)
        div_list = tree.xpath('//*[@id="container"]/div')
        for div in div_list:
            title = div.xpath('./p/a/text()')[0] + '.rar'
            detail_url = div.xpath('./p/a/@href')[0]
            detail_page_text = requests.get(url=detail_url,headers=headers).text
            tree = etree.HTML(detail_page_text)
            download_url = tree.xpath('//*[@id="down"]/div[2]/ul/li[1]/a/@href')[0]
            dic = {
                'title':title,
                'download_url':download_url
            }
            jianli_msg.append(dic)
        return jianli_msg

jianli_msg_list = get_jianli_msg()

#特殊函数：特殊函数需要对图片进行网络请求
async def get_request(dic):
    async with aiohttp.ClientSession() as sess:
        async with await sess.get(url=dic['download_url'],headers=headers) as response:
            jianli_data = await response.read() #获取二进制的图片数据
            dic['jianli_data'] = jianli_data
            return dic

def saveJianli(t):
    #是否可以获取图片二进制的数据呢？
    dic = t.result()
    jianli_data = dic['jianli_data']
    jianli_title = dic['title']

    jianli_path = dirName + '/' + jianli_title
    with open(jianli_path,'wb') as fp:
        fp.write(jianli_data)
    print(jianli_title,':爬取保存成功！')

tasks = []
for dic in jianli_msg_list:
    c = get_request(dic)
    task = asyncio.ensure_future(c)
    task.add_done_callback(saveJianli)
    tasks.append(task)
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))