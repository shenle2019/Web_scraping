from playwright.sync_api import sync_playwright
from lxml import etree
#封装页面切换的函数
def switch_to_page(context,title):
    for page in context.pages:
        if title == page.title():
            #浏览器停留在此page页面
            page.bring_to_front()
            return page
with sync_playwright() as p:
    bro = p.chromium.launch(headless=False,slow_mo=1000)
    context = bro.new_context()
    page = context.new_page()
    page.goto('https://www.bilibili.com/')

    #xpath定位
    page.locator('//*[@id="nav-searchform"]/div[1]/input').fill('Python教程')
    page.locator('//*[@id="nav-searchform"]/div[2]').click()

    #切换到新打开的page中
    select_page = switch_to_page(context,'Python教程-哔哩哔哩_bilibili')
    page_text = select_page.content()
    tree = etree.HTML(page_text)
    div_list = tree.xpath('//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div/div[3]/div/div')
    for div in div_list:
        title = div.xpath('.//h3[@class="bili-video-card__info--tit"]/@title')[0]
        author = div.xpath('.//span[@class="bili-video-card__info--author"]/text()')[0]
        print(title,author)
    page.close()
    bro.close()