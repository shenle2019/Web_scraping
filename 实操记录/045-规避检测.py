from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    bro = p.chromium.launch(headless=False)
    context = bro.new_context()
    context.add_init_script(path='./stealth.min.js')
    page = context.new_page()
    page.goto('https://www.taobao.com/')

    ret = page.evaluate('window.navigator.webdriver')
    print(ret)

    page.wait_for_timeout(3000)
    page.close()
    bro.close()