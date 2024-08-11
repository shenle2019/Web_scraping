from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    bro = p.chromium.launch(headless=False,slow_mo=2000)
    page = bro.new_page()
    page.goto('https://www.bilibili.com/')

    #xpath定位
    page.locator('//*[@id="nav-searchform"]/div[1]/input').fill('Python教程')
    page.locator('//*[@id="nav-searchform"]/div[2]').click()

    page.close()
    bro.close()