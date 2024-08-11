from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    bro = p.chromium.launch(headless=False)
    page = bro.new_page()
    page.goto('https://www.baidu.com')

    # 方式1：
    # input_tag = page.locator('#kw').press_sequentially('hello world',delay=500)

    # 方式2：设置内容的输入的时间间隔
    tag = page.locator('#kw')  # id定位
    tag.focus()  # 聚焦于当前标签
    input_text = 'Hello, World!'
    for char in input_text:
        page.keyboard.type(char, delay=500)

    # 定位搜索按钮，进行点击操作
    page.locator('#su').click()

    page.close()
    bro.close()