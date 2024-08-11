from playwright.sync_api import sync_playwright


# 封装页面切换的函数
def switch_to_page(context, title):
    for page in context.pages:
        if title == page.title():
            # 浏览器停留在此page页面
            page.bring_to_front()
            return page


# 点击百度首页中左上角的全部链接，以打开多个不同的page页面
with sync_playwright() as p:
    bro = p.chromium.launch(headless=False, slow_mo=1000)
    # 创建上下文管理对象
    context = bro.new_context()
    # 基于上下文管理对象打开一个page页面
    page = context.new_page()
    page.goto('https://www.baidu.com')
    # 点击百度首页中左上角的全部链接，以打开多个不同的page页面
    a_list = page.locator('//*[@id="s-top-left"]/a').all()
    for a in a_list:
        a.click()

    # page页面的切换
    select_page = switch_to_page(context, 'hao123_上网从这里开始')
    # 在指定的page中进行相关操作
    select_page.locator('//*[@id="search"]/form/div[2]/input').fill('测试测试')
    select_page.locator('//*[@id="search"]/form/div[3]/input').click()

    page.close()
    bro.close()