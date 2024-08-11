# - 语法结构：page.locator()
#   - 参数：标签/id/层级/class 选择器
# - 交互操作：
#   - 点击元素， `click()` 方法
#   - 元素内输入文本， `fill()` 方法

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    bro = p.chromium.launch(headless=False,slow_mo=2000)
    page = bro.new_page()
    page.goto('https://www.baidu.com')

    #定位到输入框，进行文本录入
    page.locator('#kw').fill('Python教程') #id定位
    # 定位搜索按钮，进行点击操作
    page.locator('#su').click()
    #后退操作
    page.go_back()

    page.locator('.s_ipt').fill('爬虫')  # class定位
    page.locator('#su').click()
    page.go_back()

    page.locator('input#kw').fill('人工智能')  # 标签+属性定位
    page.locator('#su').click()
    page.go_back()

    page.locator('#form > span > input#kw').fill('数据分析') #层级定位
    page.locator('#su').click()

    page.close()
    bro.close()