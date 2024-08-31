from playwright.sync_api import sync_playwright
import requests
import json
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    #规避检测，伪造真实浏览器环境
    context.add_init_script(path='stealth.min.js')
    page = context.new_page()
    page.goto("https://www.xiaohongshu.com")
    #设置playwright的cookie环境：经过postman测试cookie只需要保留web_session和a1两个值即可
    #cookies必须是一个数组对象，必须包含最主要的四个值：domain ，name，path，value
    context.add_cookies(
        [
            {
                "name": "web_session",
                "value": "030037a1e1f8bb14695683eaaa214a73f906ce",
                "domain": ".xiaohongshu.com",
                "path": "/"
            },
            {
                "name": "a1",
                "value": '191a6f301c7k41ghhhh43gawc17bkvr0xrwsxp8j450000138529',
                "domain": ".xiaohongshu.com",
                "path": "/"
            }
        ]
    )
    page.reload() #添加cookie后，务必要重载page页面

    #json_data就是参数i

    json_data = {"cursor_score": "1.7036686839800014E9", "num": 27, "refresh_type": 1, "note_index": 35, "unread_begin_note_id": "",
     "unread_end_note_id": "", "unread_note_count": 0, "category": "homefeed_recommend", "search_key": "",
     "need_num": 12, "image_formats": ["jpg", "webp", "avif"], "need_filter_image": "false"}

#     json_data = {
#         "cursor_score": "1.7036686839800014E9",
#         "num": 20,
#         "refresh_type": 3,
#         "note_index": 55,
#         "unread_begin_note_id": "",
#         "unread_end_note_id": "",
#         "unread_note_count": 0,
#         "category": "homefeed_recommend",
#         "search_key": "",
#         "need_num": 10,
#         "image_formats": [
#             "jpg",
#             "webp",
#             "avif"
#         ]
# }
    #进行js注入，执行window._webmsxyw函数获取x-s的值
    encrypt_params = page.evaluate("([s,i]) => window._webmsxyw(s,i)",
                                   ["/api/sns/web/v1/homefeed",json_data])
    #将返回值转换成python字典
    x_s = dict(encrypt_params)['X-s']

    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'X-S':x_s,
        'Content-Type':'application/json;charset=UTF-8'
    }
    ### 注意使用实时的cookie信息。
    cookies = {
        'a1':'191a6f301c7k41ghhhh43gawc17bkvr0xrwsxp8j450000138529',
        'web_session':'030037a1e1f8bb14695683eaaa214a73f906ce'
    }
    url = 'https://edith.xiaohongshu.com/api/sns/web/v1/homefeed'

    #处理json串的请求参数
    #separators将逗号（,）作为键值对之间的分隔符，将冒号（:）作为键和值之间的分隔符。
    json_str = json.dumps(json_data,separators=(",",":"),ensure_ascii=False)
    ret = requests.post(url=url,headers=headers,data=json_str,cookies=cookies).json()
    print(ret)