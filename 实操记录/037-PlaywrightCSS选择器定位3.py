from playwright.sync_api import Playwright, sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,slow_mo=2000)
    context = browser.new_context(storage_state="taobao.json")
    page = context.new_page()
    page.goto("https://www.taobao.com/")

    page.locator('#q').fill('mac pro')
    # class属性值为btn-search tb-bg，在定位的时候选择空格左右两侧任意一个属性值即可
    page.locator('.btn-search').click()
    page.wait_for_timeout(1000)

    # 根据文本定位
    page.get_by_text('发货地').click()
    page.wait_for_timeout(1000)

    # 定位到满足要求所有的标签(商品列表最外层的a标签)
    locator = page.locator('.Content--contentInner--QVTcU0M > div > a')
    all_eles = locator.all()

    # 查看定位到满足要求标签的数量
    count = locator.count()
    print(count)
    # 定位到第10个a标签,nth下标从0开始
    a_10 = locator.nth(9)
    print(a_10.get_attribute('href'), a_10.inner_text())
    print('---------------------------------------------------------------------------')
    # 获得每一个a标签中的文本内容和href属性值
    for index in range(count):
        ele = locator.nth(index)
        text = ele.inner_text()
        href = ele.get_attribute('href')
        print(text, href)

    page.close()
    context.close()
    browser.close()