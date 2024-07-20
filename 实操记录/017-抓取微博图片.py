import requests
from lxml import etree

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ### 这个case的Referer 没有找到？
    ### https://blog.sina.com.cn/s/blog_01ebcb8a0102zi2o.html?tj=1  通过network-img中找到图片的缩略图，然后再找 Referer
    "Referer": "http://blog.sina.com.cn/",
}
url = 'http://blog.sina.com.cn/s/blog_01ebcb8a0102zi2o.html?tj=1'
page_text = requests.get(url, headers=headers).text
tree = etree.HTML(page_text)

###//*[@id="sina_keyword_ad_area2"]/div/a[1]/img
img_src = tree.xpath('//*[@id="sina_keyword_ad_area2"]/div/a/img/@real_src')
for src in img_src:
    data = requests.get(src, headers=headers).content
    with open('./123.jpg', 'wb') as fp:
        fp.write(data)
    break