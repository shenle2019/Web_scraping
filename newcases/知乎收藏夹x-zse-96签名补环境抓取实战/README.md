# 知乎收藏夹 x-zse-96 签名补环境抓取实战

> 对应课件：《Day28：JS逆向爬虫基础案例09》（知乎 x-zse-96 签名 / JSVMP 字节码 VM / webpack 模块调用 / 补环境）
>
> 任务：纯 JS 逆向思路复刻课件案例，抓取收藏夹
> [https://www.zhihu.com/collection/323709385](https://www.zhihu.com/collection/323709385)「10万赞以上的回答」
> 的全部内容，逐条存档为 md 文件写入本地 Obsidian 库。
>
> 原则：**不做纯算**，用补环境黑箱调用原版 JS 生成签名（最省力路线）；链路不通处用 Playwright 对照定界。

## 一、成果

| 项 | 数值 |
|---|---|
| 收藏夹 | 「10万赞以上的回答」（创建于 2019-02-11，1604 人关注，服务端计数 263） |
| 实际抓取 | **252 条**（answer 249 + article 3），全部含全文（差额 11 条为已失效/删除条目，两次独立抓取稳定一致） |
| 输出目录 | `E:\一人公司\公众号写作\Obsidian\testobsidian\知乎高赞\10万赞以上的回答\` |
| 输出内容 | 252 个回答 md（`序号_标题_作者.md`）+ `_目录.md` 全量索引（共 253 个文件，3.2 MB） |
| 图片 | 111 个文件含图，共 2882 张图片链接（Obsidian 直接渲染网络图片） |
| 本目录日志 | `_run_*.txt` 14 份，为各脚本实测终端输出逐字转录 |

## 二、技术路线（JS 逆向为主线）

```
┌─ 一次性：Playwright 有头浏览器扫码登录 → output/zhihu_state.json（凭证，不入库）
│
┌─ 每次请求：本地补环境黑箱签名（不做纯算）
│    env.js   补环境（window=global / __ZH__.zse 三表 / DOM 桩 / Math.random 固定）
│    mod.js   知乎 chunk 4091（模块 1514：zse 签名模块，内含字节码 VM）
│    loader.js 改造版 webpack runtime（yuan.loader = __webpack_require__）
│    zhihu_sign.js  →  yuan.loader(1514)["ZP"](md5hex)   【黑箱调用】
│
│    x-zse-96 = "2.0_" + ZP( md5( x-zse-93 + "+" + 路径?查询 + "+" + d_c0 ) )
│
└─ requests + 登录态 cookies + 签名头 → 逐页抓取 items API（14 页，低频 1.2s 间隔）
     → HTML 正文（content.content）→ bs4 预处理 + markdownify → md 文件
```

- `items` 接口响应**直接携带回答全文**（`content.content` 为 HTML 字符串），无需逐条再请求详情接口。
- Node 侧签名脚本支持批量模式（JSON 数组进 / JSON 数组出），Python 侧 subprocess 一次调用批量出签。

## 三、关键发现（对照实验定界）

| # | 发现 | 实验依据 |
|---|---|---|
| 1 | 匿名访问收藏夹被**登录墙**拦截：items API 401「身份未经过验证」，页面显示「请登录后查看」；匿名浏览器自身请求同样 401 | 00 / 05 / 03 号脚本 |
| 2 | **登录态下服务端不校验 x-zse-96**：无签名、`2.0_AAAA…` 错误签名、本地补环境签名，三种请求全部 200 | 11 号脚本（三组对照） |
| 3 | `d_c0` 现由前端 JS 生成（服务端不再下发）；Chrome 155 运行时 Cookies 文件被**独占锁**（ERROR_SHARING_VIOLATION=32），常规读取方案不可行 | 01 / 06 / 07 号脚本 |
| 4 | 无头浏览器滚轮无法触发收藏夹翻页 → 直接走 API 分页更稳 | 09 号脚本 |
| 5 | 浏览器真实签名与本地穷举变体不一致，但登录态下不影响放行（签名公式校验仅在匿名场景可能生效，而匿名已被登录墙拦截） | 04 / 10 号脚本 |

> 体会：本案例的核心门槛已从「签名算法」转移到「登录态」；x-zse-96 在接口层面属于纵深防御，登录用户不强制校验。补环境链路完整保留（每次请求都实际生成签名），作为理解课件与后续匿名场景的通用能力。

## 四、目录结构

```
知乎收藏夹x-zse-96签名补环境抓取实战/
├── js/                              【JS 逆向签名工程】
│   ├── env.js                       补环境（已关闭调试日志的正式版）
│   ├── mod.js                       知乎业务 chunk（模块 1514 签名模块，原版）
│   ├── loader.js                    改造版 webpack runtime（已关闭模块加载打印）
│   └── zhihu_sign.js                签名入口（批量/stdin 两种模式）
├── 00_探测接口.py                    收藏夹元信息 / 401 登录墙 / 页面可达性
├── 01_探测cookies.py                 d_c0 下发情况探测
├── 02_验证签名.py                    自造 d_c0 + 本地签名实测（发现 401 为登录墙）
├── 03_playwright对比.py              浏览器真实签名材料采集 + 本地对照
├── 04_签名公式穷举.py                11 个拼串变体批量对照（登录墙下定界）
├── 05_匿名可见性检查.py              匿名页面截图 + 「请登录后查看」确认
├── 06_检查Chrome登录态.py            Chrome profile / 加密方案探测
├── 07_读ChromeCookie.py             ctypes 共享读 + DPAPI 探测（遇 Chrome 独占锁失败，留档）
├── 08_登录保存状态.py                一次性扫码登录 → storage_state
├── 09_playwright采集.py             登录态页面拦截 items 响应（发现响应含全文）
├── 10_登录态签名实测.py              登录态三组请求 + 真实签名穷举对照
├── 11_签名有效性对照.py              无签名/错误签名/本地签名 服务端反应对照
├── 12_抓取收藏夹.py                  【正式爬虫】14 页全量抓取（详情见第二节）
├── 13_生成Markdown.py                【成果生成】HTML→Markdown → Obsidian 目录
├── 14_生成运行日志存档.py            把实测终端输出转录为 _run_*.txt
├── _run_*.txt                       14 份运行日志（UTF-8）
└── output/                          运行产物（结果数据，.gitignore 不入库）
    ├── collection_raw_pages.json    逐页原始响应
    ├── collection_all_items.json    合并去重后 252 条
    ├── zhihu_state.json             登录凭证（严禁入库）
    └── *.png                        过程截图（登录态/匿名页/加载页）
```

## 五、验证结果汇总

| 脚本 | 验证内容（关键数据） | 结果 | 日志 |
|---|---|---|---|
| 00_探测接口.py | 收藏夹「10万赞以上的回答」263 计数；items 无签名 401；页面 200 | PASS | _run_00_探测接口.txt |
| 01_探测cookies.py | 首页不下发 d_c0（已改为前端生成）；/search 直接 403 | PASS | _run_01_探测cookies.txt |
| 02_验证签名.py | 补环境签名 64 字符与课件样例同型；三种拼串均 401（登录墙） | PASS | _run_02_验证签名.txt |
| 03_playwright对比.py | 浏览器匿名会话捕获 5 个 API 请求；签名材料对照不一致（因 401） | PASS | _run_03_playwright对比.txt |
| 04_签名公式穷举.py | 11 变体 x 真实样本 全部不一致（决定转登录路线） | PASS | _run_04_签名公式穷举.txt |
| 05_匿名可见性检查.py | 匿名页面正文 327 字，命中「请登录后查看」= 登录墙实锤 | PASS | _run_05_匿名可见性.txt |
| 06_检查Chrome登录态.py | Chrome 155；Cookies 常规复制 Permission denied | PASS | _run_06_检查Chrome登录态.txt |
| 07_读ChromeCookie.py | ctypes 共享读仍 ERROR_SHARING_VIOLATION=32（留档技术结论） | 失败留档 | _run_07_读ChromeCookie.txt |
| 08_登录保存状态.py | 扫码登录成功，z_c0 出现，storage_state 落盘 | LOGIN_OK | _run_08_登录保存状态.txt |
| 09_playwright采集.py | 第一页 19 条；**响应含全文**；无头滚动不翻页 | PASS | _run_09_playwright采集.txt |
| 10_登录态签名实测.py | 登录态无签名 200 / 本地签名 200；真实签名 7 变体对照 | PASS | _run_10_登录态签名实测.txt |
| 11_签名有效性对照.py | 无签名/全 A 错误签名/本地签名 **全部 200** → 登录态不校验 | PASS | _run_11_签名有效性对照.txt |
| 12_抓取收藏夹.py | 14 页全量：263 计数 → 去重 **252 条**（249 answer + 3 article），全部含全文，is_end 正常 | ALL PASS | _run_12_抓取收藏夹.txt |
| 13_生成Markdown.py | **252 个 md + 1 个索引**写入 Obsidian 目录；抽查元信息/图片/格式正常 | ALL PASS | _run_13_生成Markdown.txt |

## 六、复现方式

```powershell
cd newcases\知乎收藏夹x-zse-96签名补环境抓取实战
pip install requests playwright markdownify beautifulsoup4   # 依赖
python 08_登录保存状态.py     # 一次性：弹出浏览器扫码登录（凭证存 output/）
python 12_抓取收藏夹.py       # 抓取全部条目 → output/collection_all_items.json
python 13_生成Markdown.py     # 生成 md 到 Obsidian 目录
```

## 七、合规声明

- 仅限学习研究，**禁止商用**；抓取频率低（共 14 页、间隔 1.2s、单线程）。
- 收藏夹内容为公开分享数据，抓取结果仅本地存档，不公开传播。
- 登录凭证（`output/zhihu_state.json`）与全部结果数据已通过 `.gitignore` 排除，不入公开仓库。
- 未突破任何付费/私密内容边界；遇登录墙采用用户本人账号正常登录状态访问。
