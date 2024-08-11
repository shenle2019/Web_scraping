from playwright.sync_api import sync_playwright  #导入同步模块

#创建一个Playwright的管理器对象
with sync_playwright() as p: # p = sync_playwright()
    #基于p创建一个浏览器对象（谷歌浏览器对象）
    bro = p.chromium.launch(headless=False)
    #创建一个浏览器页面
    page = bro.new_page()
    #在指定的页面中进行请求发送
    page.goto('https://www.baidu.com')
    #暂定2s中
    page.wait_for_timeout(2000)
    #获取访问页面的标题
    title = page.title()
    #获取页面的页面源码数据（重要=》可见即可得）
    page_text = page.content()
    print(page_text,title)

    page.close()
    bro.close()