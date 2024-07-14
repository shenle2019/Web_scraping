from bs4 import BeautifulSoup

fp = open('test.html', 'r',encoding='utf-8')
# 1.创建一个BeautifulSoup的工具对象，然后把即将被解析的页面源码数据加载到该对象中
# 参数1：被解析的页面源码数据
# 参数2：固定形式的lxml(一种解析器)
soup = BeautifulSoup(fp, 'lxml')

# 2.可以调用BeautifulSoup对象的相关函数和属性进行标签定位和数据提取

# 标签定位-方式1:soup.tagName(只可以定位到第一次出现的该标签)
title_tag = soup.title
p_tag = soup.p

# 标签定位-方式2（属性定位）:soup.find(tagName,attrName='value')
# 注意：find只可以定位满足要求的第一个标签，如果使用class属性值的话，find参数class_
# 定位到了class属性值为song的div标签
div_tag = soup.find('div', class_='song')
# 定位到class属性值为du的a标签
a_tag = soup.find('a', class_='du')
# 定位到了id的属性值为feng的a标签
a_tag = soup.find('a', id='feng')

# 标签定位-方式3（属性定位）:soup.find_all(tagName,attrName='value')
# 注意：find_all可以定位到满足要求的所有标签
tags = soup.find_all('a', class_='du')
# 标签定位-方式4(选择器定位):
# 常用的选择器：class选择器(.class属性值)  id选择器(#id的属性值)
tags = soup.select('#feng')  # 定位到id的属性值为feng对应的所有标签
tags = soup.select('.du')  # 定位到class属性值为du对应的所有标签
# 层级选择器：>表示一个层级  一个空格可以表示多个层
tags = soup.select('.tang > ul > li > a')
tags = soup.select('.tang a')
# print(tags)

# 定位到标签内部数据的提取
# 方式1：提取标签内的文本数据
# tag.string:只可以将标签直系的文本内容取出
# tag.text:可以将标签内部所有的文本内容取出
tag = soup.find('a', id='feng')
content = tag.string

div_tag = soup.find('div', class_='tang')
content = div_tag.text

# 方式2：提取标签的属性值 tag['attrName']
img_tag = soup.find('img')
img_src = img_tag['src']
print(img_src)