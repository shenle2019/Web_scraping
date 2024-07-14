from lxml import etree

# 1.创建一个etree的工具对象，然后把即将被解析的页面源码数据加载到该对象中
tree = etree.parse('test.html')
# 2.调用etree对象的xpath函数然后结合着不用形式的xpath表达式进行标签定位和数据提取
# xpath函数返回的是列表，列表中存储的是满足定位要求的所有标签
# /html/head/title定位到html下面的head下面的title标签
title_tag = tree.xpath('/html/head/title')
# //title在页面源码中定位到所有的title标签
title_tag = tree.xpath('//title')
# 属性定位
# 定位到所有的div标签
div_tags = tree.xpath('//div')
# 定位到class属性值为song的div标签 //tagName[@attrName='value']
div_tag = tree.xpath('//div[@class="song"]')
# 索引定位://tag[index]
# 注意：索引是从1开始的
div_tag = tree.xpath('//div[1]')
# 层级定位
# /表示一个层级  //表示多个层级
a_list = tree.xpath('//div[@class="tang"]/ul/li/a')
a_list = tree.xpath('//div[@class="tang"]//a')

# 数据提取
# 1.提取标签中的文本内容:/text()取直系文本  //text()取所有文本
a_content = tree.xpath('//a[@id="feng"]/text()')[0]
div_content = tree.xpath('//div[@class="song"]//text()')
# 2.提取标签的属性值：//tag/@attrName
img_src = tree.xpath('//img/@src')[0]
print(img_src)