from playwright.sync_api import sync_playwright
import tuypian
from urllib import request

#有的检测移动速度的 如果匀速移动会被识别出来，来个简单点的渐进
def get_track(distance):  # distance为传入的总距离
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.2
    # 初速度
    v = 1
    while current < distance:
        if current < mid:
            # 加速度为2
            a = 4
        else:
            # 加速度为-2
            a = -3
        v0 = v
        # 当前速度
        v = v0 + a * t
        # 移动距离
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
    return track

with sync_playwright() as p:
    bro = p.chromium.launch(headless=False)
    page = bro.new_page()
    page.goto('https://passport.jd.com/new/login.aspx?')

    page.locator('//*[@id="loginname"]').fill('123456@qq.com')
    page.wait_for_timeout(1000)
    page.locator('//*[@id="nloginpwd"]').fill('123456@qq.com')
    page.wait_for_timeout(1000)
    page.locator('//*[@id="loginsubmit"]').click()

    page.wait_for_timeout(2000)

    bg_img_src = page.locator('.JDJRV-bigimg > img').get_attribute('src')

    # 两张图片保存起来
    request.urlretrieve(bg_img_src, "background.png")

    #基于图鉴平台实现计算滑动距离
    distance = tuypian.getImgCodeText('background.png',33)
    distance = int(distance)

    #定位到滑块标签
    slide = page.locator('//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[2]/div[3]')
    # 找到滑块在当前页面的坐标（这个会返回一个字典里边四个数字）
    #{'x': 858, 'y': 339.9921875, 'width': 55, 'height': 55}
    box = slide.bounding_box()

    #让鼠标移动到滑块标签的中间上
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    # 按下鼠标
    page.mouse.down()
    # 这里获取到滑块x坐标中心点位置
    x = box["x"]
    # 滑动的长度放到轨迹加工一下得到一个轨迹
    tracks = get_track(distance)
    for track in tracks:
        # 循环鼠标按照轨迹移动
        page.mouse.move(x + track, 0)
        x += track
    # 移动结束鼠标释放
    page.mouse.up()

    page.wait_for_timeout(5000)
    page.close()
    bro.close()