from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    ### 先把浏览器在chrome.exe目录打开，然后把百度网页打开，后面的操作才会有返回结果。
    browser = p.chromium.connect_over_cdp('http://localhost:8899/')
    # 获取page对象
    page = browser.contexts[0].pages[0]
    #该操作会直接作用在接管的浏览器中
    page.locator('//*[@id="kw"]').fill('haha')
    print(page.url)
    print(page.title())