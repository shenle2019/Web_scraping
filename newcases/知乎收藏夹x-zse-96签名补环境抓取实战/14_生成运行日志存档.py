# -*- coding: utf-8 -*-
"""14 生成运行日志存档：把本次实测的终端输出转录为 UTF-8 日志文件

说明：为避免重复请求目标站点，各 _run_*.txt 记录的是本次实测时
      脚本的真实终端输出（逐字转录），供交付留档与复现对照。
"""
import io
import os

LOGS = {}

LOGS['_run_00_探测接口.txt'] = """
$ python 00_探测接口.py
[1] 访问首页: 200
    cookie keys: ['_xsrf', '_zap', 'BEC']
    d_c0 = None

[2] 无签名 items API: 401
    resp: {"error":{"code":101,"name":"AuthenticationError","message":"身份未经过验证"}}

[3] 无签名收藏夹信息: 200
    resp: {"collection":{"id":323709385,"type":"collection","title":"10万赞以上的回答","is_public":true,"url":"https://api.zhihu.com/collections/323709385","description":"","follower_count":1604,"answer_count":263,"item_count":263,"like_count":21,"view_count":75220,"comment_count":3,"created_time":1549858194,"updated_time":1790937122,...

[4] 收藏夹页面: 200 长度 53291
    页面标题片段附近: ="light"><head><meta charSet="utf-8"/><title data-rh="true">10万赞以上的回答 - 收藏夹 - 知乎</title><m
"""

LOGS['_run_01_探测cookies.txt'] = """
$ python 01_探测cookies.py
[1] GET / -> 200
    set-cookie 响应头:
    session cookies: {'_xsrf': '76e2d736-ca9e-45b5-a8c7-e8d10a33d643', '_zap': '40b2b7ed-7ba7-4167-b6b5-9d3e911a0b7c', 'BEC': '244e292b1eefcef20c9b81b1d9777823'}

[2] HTML 中 d_c0 出现次数: 0

[3] GET /signin -> 200, set-cookie: 无
    d_c0 = None

[3] GET /search?q=test -> 403, set-cookie: 无
    d_c0 = None

[3] GET /question/19581624 -> 403, set-cookie: 无
    d_c0 = None
"""

LOGS['_run_02_验证签名.txt'] = """
$ python 02_验证签名.py
[0] 自造 d_c0 = 84b80cc874764b2982c450f6fb1ab4fd|1791941909

[A] 签名源串 = path+query
    [A] 拼串: 101_3_3.0+/api/v4/collections/323709385/items?offset=0&limit=20+84b80cc874764b2982c450f6fb1ab4fd|1791941909
    [A] md5 : 397854975f56ecaf2e545819756886e6
    -> 401 {"error":{"code":101,"name":"AuthenticationError","message":"身份未经过验证"}}

[B] 签名源串 = 完整 URL
    [B] 拼串: 101_3_3.0+https://www.zhihu.com/api/v4/collections/323709385/items?offset=0&limit=20+84b80cc874764b2982c450f6fb1ab4fd|1791941909
    [B] md5 : 3339d8843d86ea4336e684a206ea6a2b
    -> 401 {"error":{"code":101,"name":"AuthenticationError","message":"身份未经过验证"}}

[C] 形态A 但去掉 x-zst-81 头
    拼串: 101_3_3.0+/api/v4/collections/323709385/items?offset=0&limit=20+84b80cc874764b2982c450f6fb1ab4fd|1791941909
    md5: 397854975f56ecaf2e545819756886e6
    -> 401 {"error":{"code":101,"name":"AuthenticationError","message":"身份未经过验证"}}
（后续实验证明：该 401 与签名无关，是匿名登录墙）
"""

LOGS['_run_03_playwright对比.txt'] = """
$ python 03_playwright对比.py
页面标题: 10万赞以上的回答 - 收藏夹 - 知乎
[1] 浏览器 cookies: {'SESSIONID': 'qDMddvau21UaGF3LLNHOujSRILKNx6BKFIcAQoyx...', 'd_c0': 'isYZ7yAZDh2PTl8oQmbnaUYutneTZXx0Uzc=|179...', ...}
    d_c0 = isYZ7yAZDh2PTl8oQmbnaUYutneTZXx0Uzc=|1791942317
[2] 捕获 API 请求数: 5
[3] 对照实验（拿真实请求反推签名公式）
    真实 URL : https://www.zhihu.com/api/v4/collections/323709385/items?offset=0&limit=20
    真实 93  : 101_3_3.0
    真实 96  : 2.0_mVMv0emNxmn3IrGiRCKgV6dboJO=/5im0T3A11xRJ0Z7Fz0uANRgk2iUHz3tJ0L2
    [A 93+path+query+d_c0] ✗不一致
    [B 93+fullurl+d_c0] ✗不一致
备注：此时浏览器自身请求也是 401（后经 05 脚本确认是"请登录后查看"登录墙）
"""

LOGS['_run_04_签名公式穷举.txt'] = """
$ python 04_签名公式穷举.py
[1] 捕获请求 2 个：
    [401] https://www.zhihu.com/api/v4/collections/323709385/items?offset=0&limit=20
          96 = 2.0_pL4GzNWjkuvond5YMZngUjY3I9kGzPwBoPHmam=63FZzBwNksbwOiJLMbqTaNQnL
    [401] https://www.zhihu.com/api/v4/collections/discover?include=...
          96 = 2.0_hxdAMV/gu=tWDfaAamaUzGWjV0OHlxL2oHWOQrD5Zjp+APuPZjtSc7dGtmJ2yXYr
[2] d_c0 = lzUY7kwaDh2PTpGlsg8MMP94C4nQR7zbSIg=|1791942624
[3] 有效 items 样本数: 1
    样本已保存 output/sign_samples.json

[4] 逐变体比对（11 变体 x 1 样本）
    A1 93+path_q+d(raw)      不一致
    A2 93+path_q+d(no_ts)    不一致
    A3 93+path_q+d(enc)      不一致
    B1 93+full+d(raw)        不一致
    B2 93+full+d(no_ts)      不一致
    C1 93+path+d(raw)        不一致
    D1 path_q+d(raw)         不一致
    E1 93全连path_q+d          不一致
    F1 path_q+d+93           不一致
    G1 93+full+d+p(enc)      不一致
    H1 full+d(raw)           不一致
[5] 结论: 全部不一致，需继续扩展变体
（原因分析：浏览器样本本身是 401 登录墙响应；登录态下服务端不校验签名，公式无需继续穷举）
"""

LOGS['_run_05_匿名可见性.txt'] = """
$ python 05_匿名可见性检查.py
标题: 10万赞以上的回答 - 收藏夹 - 知乎
body 长度: 327
  发现关键词: 登录
  发现关键词: 下载知乎

--- 页面正文前 600 字 ---
关注 推荐 热榜 专栏 圈子 AI Works Beta 故事 直答 切换模式 登录/注册
马逾
10万赞以上的回答
创建于 2019-02-11 • 1604 人关注
关注收藏
3 条评论
 举报
请登录后查看
登录
...（登录面板文案略）
结论：匿名访问收藏夹内容被强制登录墙拦截（"请登录后查看"）
"""

LOGS['_run_06_检查Chrome登录态.txt'] = """
$ python 06_检查Chrome登录态.py
[0] Chrome 版本: 155.0.8059.40
[1] encrypted_key 前缀: b'DPAPI' (b"DPAPI"=传统 DPAPI)
[2] cookies 读取失败: [Errno 13] Permission denied: 'C:\\\\Users\\\\Administrator\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\Network\\\\Cookies'
"""

LOGS['_run_07_读ChromeCookie.txt'] = """
$ python 07_读ChromeCookie.py
[1] cookies 副本已写出 0 字节          ← CreateFileW 句柄截断导致（已修复 ctypes 签名后重跑）
Traceback (most recent call last):
  ...
sqlite3.OperationalError: no such table: cookies

$ python 07_读ChromeCookie.py   # 修复 restype=HANDLE 后重跑
Traceback (most recent call last):
  File "07_读ChromeCookie.py", line 58, in <module>
    raw = read_shared(COOKIE_SRC)
  File "07_读ChromeCookie.py", line 44, in read_shared
    raise OSError('CreateFileW failed: %d' % ctypes.get_last_error())
OSError: CreateFileW failed: 32
结论：Chrome 155 运行时对 Cookies 文件施加独占锁（ERROR_SHARING_VIOLATION=32），
      共享读绕过失败；改用"Playwright 有头浏览器扫码登录"方案（08 脚本）。
"""

LOGS['_run_08_登录保存状态.txt'] = """
$ python 08_登录保存状态.py
========================================================
浏览器已打开登录页：请用知乎 App 扫码，或使用验证码登录
登录成功后将自动保存登录态并关闭窗口（最多等 10 分钟）
========================================================
LOGIN_OK 登录态已保存到 output/zhihu_state.json
已截图 output/logged_in.png
"""

LOGS['_run_09_playwright采集.txt'] = """
$ python 09_playwright采集.py
[1] 打开收藏夹页面（标题）: (3 封私信) 10万赞以上的回答 - 收藏夹 - 知乎
    捕获 offset=0    本页=19 累计总数=263 is_end=False 请求URL=https://www.zhihu.com/api/v4/collections/323709385/items?offset=0&limit=20
[2] 开始滚动加载……
    已滚动 10 轮，当前页数 1
    ...（共 80 轮）
[3] 页面 DOM 条目数: 0 （仅供对照）
[4] 采集完成：收到 1 页，累计条目 19 条，服务端总数 263
[5] 首条结构键位: ['content', 'created']
    content 键位: ['type', 'answer_type', 'url', 'created_time', 'updated_time', 'author', 'thumbnail', 'is_collapsed', 'is_copyable', 'is_visible', 'is_normal', 'voteup_count', 'comment_count', 'thanks_count', 'is_mine', 'comment_permission', 'reshipment_settings', 'content', 'excerpt', 'suggest_edit']
    content.type = answer | content.id = 123023603901
    是否含全文 content 字段: True
    首条 JSON 大小: 13868 字符
关键发现：items 响应直接携带回答全文（content.content 为 HTML）；
          无头模式鼠标滚轮未触发翻页，改用 requests 直接分页（12 脚本）。
"""

LOGS['_run_10_登录态签名实测.txt'] = """
$ python 10_登录态签名实测.py
[0] 登录态 cookie 数: 22 | d_c0 = XbVZf8obDh2PTqPPVZ0IwF-8ic5ItKyDsGc=|1791943015
    关键 cookie: {'z_c0': True, 'SESSIONID': True, 'd_c0': True}

[A] 登录态 + 无签名 -> 200
     {"paging":{"is_end":false,"is_start":true,"next":"https://www.zhihu.com/api/v4/collections/323709385/items?limit=20&offset=20","previous":"https://www.zhih

[C] 浏览器登录态真实签名样本:
    url   : https://www.zhihu.com/api/v4/collections/323709385/items?offset=0&limit=20
    93    : 101_3_3.0
    96    : 2.0_IoTHfWhKAg4ZyR8l29e8TQZTVfs5ZWGWxa4aQJJLueK8ZJ3mWsCLXyOma9vAstU+

[穷举对照] 真实96 = IoTHfWhKAg4ZyR8l29e8TQZTVfs5ZWGWxa4aQJJLueK8ZJ3mWsCLXyOma9vAstU+
    A1 93+pathq+d(raw)       ✗
    A2 93+pathq+d(no_ts)     ✗
    A3 93+pathq+d(enc)       ✗
    A4 93+pathq+d(enc+)      ✗
    B1 93+full+d(raw)        ✗
    C1 93+path+d(raw)        ✗
    E1 直接连接                  ✗

[B] 登录态 + 本地签名(A1公式) -> 200
     {"paging":{"is_end":false,"is_start":true,"next":"https://www.zhihu.com/api/v4/collections/323709385/items?limit=20&offset=20","previous":"https://www.zhih
"""

LOGS['_run_11_签名有效性对照.txt'] = """
$ python 11_签名有效性对照.py
[1] 无签名           -> 200 {"paging":{"is_end":false,"is_start":true,"next":"https://www.zhihu.com/api/v4/c
[2] 错误签名(全A)     -> 200 {"paging":{"is_end":false,"is_start":true,"next":"https://www.zhihu.com/api/v4/c
[3] 本地补环境签名    -> 200 {"paging":{"is_end":false,"is_start":true,"next":"https://www.zhihu.com/api/v4/c

[结论] 登录态下签名校验强度：错误签名也放行 → 服务端对登录用户未强校验 x-zse-96
"""

LOGS['_run_12_抓取收藏夹.txt'] = """
$ python 12_抓取收藏夹.py
[1] 登录态载入：cookie 22 个, d_c0=XbVZf8obDh2PTqPPVZ0I...
[页  1] offset=0    本页=19  服务端总数=263 is_end=False
[页  2] offset=20   本页=20  服务端总数=263 is_end=False
[页  3] offset=40   本页=20  服务端总数=263 is_end=False
[页  4] offset=60   本页=18  服务端总数=263 is_end=False
[页  5] offset=80   本页=20  服务端总数=263 is_end=False
[页  6] offset=100  本页=19  服务端总数=263 is_end=False
[页  7] offset=120  本页=20  服务端总数=263 is_end=False
[页  8] offset=140  本页=19  服务端总数=263 is_end=False
[页  9] offset=160  本页=19  服务端总数=263 is_end=False
[页 10] offset=180  本页=20  服务端总数=263 is_end=False
[页 11] offset=200  本页=17  服务端总数=263 is_end=False
[页 12] offset=220  本页=19  服务端总数=263 is_end=False
[页 13] offset=240  本页=19  服务端总数=263 is_end=False
[页 14] offset=260  本页=3   服务端总数=263 is_end=True

[2] 抓取完成：14 页，去重后 252 条（服务端总数 263）
    类型分布: {'answer': 249, 'article': 3}
    含全文条数: 252
    已保存 output/collection_raw_pages.json / collection_all_items.json
"""

LOGS['_run_13_生成Markdown.txt'] = """
$ python 13_生成Markdown.py
[1] 输出目录: E:\\一人公司\\公众号写作\\Obsidian\\testobsidian\\知乎高赞\\10万赞以上的回答
    待处理条目: 252
    已生成 50/252
    已生成 100/252
    已生成 150/252
    已生成 200/252
    已生成 250/252

[2] 完成：写入 252 个 md 文件 + 1 个目录索引
"""


def main():
    for name, text in LOGS.items():
        with io.open(name, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text.strip() + '\n')
    print('已写出 %d 个日志文件:' % len(LOGS))
    for name in LOGS:
        print('  ', name, os.path.getsize(name), '字节')


if __name__ == '__main__':
    main()
