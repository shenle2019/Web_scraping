# 方式2
from urllib.request import urlretrieve

# 图片地址
img_url = 'https://preview.qiantucdn.com/58pic/37/Jp/9N/eC/yzkj10w3a4bf56ehvtudrxpic7s8oml9_PIC2018_png_aiys_PIC2018.jpg%21w1024_new_small_1'
# 参数1：图片地址
# 参数2：图片存储路径
# urlretrieve可以根据图片地址将图片数据请求到直接存储到参数2表示的图片存储路径中
urlretrieve(img_url, '2.jpg')