from lxml import etree
import requests
import os
import re

# 新建一个文件夹
dirName = 'girls'
if not os.path.exists(dirName):  # 如果文件夹不存在，则新建，否则不新建
    os.mkdir(dirName)

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
# 创建一个通用的url:除了第一页其他页码的通用url
url = 'https://pic.netbian.com/4kmeinv/index_%d.html'
for page in range(1, 6):
    if page == 1:
        new_url = 'https://pic.netbian.com/4kmeinv/index.html'
    else:
        new_url = format(url % page)
    print('----------正在请求下载第%d页的图片数据----------' % page)
    response = requests.get(url=new_url, headers=headers)
    response.encoding = 'gbk'
    page_text = response.text

    # 数据解析：图片地址+图片名称
    tree = etree.HTML(page_text)  # HTML()专门用来解析网络请求到的页面源码数据
    # 该列表中存储的是每一个li标签
    li_list = tree.xpath('//div[@class="slist"]/ul/li')
    for li in li_list:
        # 局部解析：将li标签中指定的内容解析出来
        img_title = li.xpath('./a/b/text()')[0] + '.jpg'  # 左侧./表示xpath的调用者对应的标签
        img_src = 'https://pic.netbian.com' + li.xpath('./a/img/@src')[0]

        # 对图片发起请求，存储图片数据
        img_data = requests.get(url=img_src, headers=headers).content
        # girls/123.jpg
        img_path = dirName + '/' + img_title

        # 定义一个函数来清理文件名
        def clean_filename(filename):
            # 替换文件名中的非法字符
            filename = re.sub(r'[\\/*?:"<>|]', "", filename)
            return filename


        # 清理文件路径
        cleaned_img_path = clean_filename(img_title)
        img_path = dirName + '/' + cleaned_img_path
        img_data = b''  # 示例图片数据

        print(img_path)

        # 尝试写入文件
        try:
            with open(img_path, 'wb') as fp:
                fp.write(img_data)
        except OSError as e:
            print(f"无法写入文件：{img_path}. 错误：{e}")

        # with open(img_path, 'wb') as fp:
        #     fp.write(img_data)
        print(img_title, '下载保存成功！')