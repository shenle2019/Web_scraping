from playwright.sync_api import sync_playwright
import tujian
from urllib import request

with sync_playwright() as p:
    bro = p.chromium.launch(headless=False)
    page = bro.new_page()
    page.goto('https://passport.bilibili.com/login?from_spm_id=333.851.top_bar.login_window')

    page.locator('//*[@id="app"]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/input').fill('15027900535')
    page.wait_for_timeout(1)
    page.locator('//*[@id="app"]/div[2]/div[2]/div[3]/div[2]/div[1]/div[3]/input').fill('bobo@123.com')
    page.wait_for_timeout(1)
    page.locator('//*[@id="app"]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]').click()
    page.wait_for_timeout(3)

    # 此处找到验证码图片将其截图保存
    ele = page.locator('//div[@class="geetest_widget"]')
    ele.screenshot(path='./code.png')
    # 找到ele在当前页面的坐标{'x': 858, 'y': 335, 'width': 55, 'height': 55}
    box = ele.bounding_box()

    # 提交给打码平台
    result = tujian.getImgCodeText('code.png', 27)
    # result = '154,251|145,167'
    result_list = result.split('|')
    # result_list ==> ['154,251','145,167']
    # 6.根据识别出验证码的结果进行处理
    for pos in result_list:
        x = int(pos.split(',')[0])
        y = int(pos.split(',')[1])
        # page.mouse.move(box['x']+x,box['y']+y)
        # page.mouse.down()
        # page.mouse.up()  #或者直接使用click方式
        page.mouse.click(box['x'] + x, box['y'] + y)
        page.wait_for_timeout(500)

    # 找到确认按钮
    submit = page.locator('//div[@class="geetest_commit_tip"]')
    submit.click()

    page.wait_for_timeout(5000)
    page.close()
    bro.close()