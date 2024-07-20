import requests
from lxml import etree
import os

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
url = 'https://www.51miz.com/shipin/'
response = requests.get(url=url, headers=headers)
page_text = response.text

# 数据解析
tree = etree.HTML(page_text)
### /html/body/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]
### alist /html/body/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/a[1]

### div_list = tree.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/div')

# 新建一个文件夹
dirName = 'videos'
if not os.path.exists(dirName):  # 如果文件夹不存在，则新建，否则不新建
    os.mkdir(dirName)

a_list = tree.xpath(' /html/body/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/a')
for a in a_list:
    ### /html/body/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/a[1]
    ### /html/body/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/a[1]/div/div/div/video/source
    src_list = a.xpath('./div/div/div/video/source/@src')
    # 要给视频地址进行补全
    for src in src_list:
        # src就是一个完整的视频地址
        src = 'https:' + src
        print(src)
        video_data = requests.get(url=src, headers=headers).content
        video_title = dirName + '/' + src.split('/')[-1]
        print(video_title)

        ### video 文件写失败，但是迅雷可以下载成功。
        with open(video_title, 'wb') as fp:
            fp.write(video_data)
        print(video_title, '爬取保存成功！')
        break