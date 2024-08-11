import asyncio
from playwright.async_api import async_playwright
#封装一个特殊的函数
async def main():
    async with async_playwright() as p:  # p = sync_playwright()
        # 基于p创建一个浏览器对象（谷歌浏览器对象）
        bro = await p.chromium.launch(headless=False)
        # 创建一个浏览器页面
        page = await bro.new_page()
        # 在指定的页面中进行请求发送
        await page.goto('https://www.baidu.com')
        # 暂定2s中
        await page.wait_for_timeout(2000)
        # 获取访问页面的标题
        title = await page.title()
        # 获取页面的页面源码数据（重要=》可见即可得）
        page_text = await page.content()
        print(page_text, title)

        await page.close()
        await bro.close()

asyncio.run(main())