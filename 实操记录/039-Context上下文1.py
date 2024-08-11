from playwright.sync_api import sync_playwright

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
    # 使用上下文管理对象获取浏览器打开的所有page页面
    pages = context.pages
    for sub_page in pages:
        # 遍历每一个page，打印起page标题
        print(sub_page.title())

    page.close()
    bro.close()