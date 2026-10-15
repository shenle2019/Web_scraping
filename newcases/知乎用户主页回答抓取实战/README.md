# 知乎用户主页回答抓取实战（丧心病狂刘老湿）

> 任务：抓取知乎用户「丧心病狂刘老湿」全部回答
> [https://www.zhihu.com/people/bingo-liu-66](https://www.zhihu.com/people/bingo-liu-66)
> 的全部回答内容，逐条存档为 md 文件，写入用户指定 Obsidian 目录。
>
> 路线：复用「知乎收藏夹x-zse-96签名补环境抓取实战」的登录态 + stealth 反检测 + 页面内 fetch 黑箱驱动（不做纯算）。

## 一、成果

| 项 | 数值 |
|---|---|
| 目标用户 | 丧心病狂刘老湿（IP 属地黑龙江，关注者 124.7 万，服务端回答计数 **1628**） |
| 实际抓取 | **1560 条**（含全文 1557 条；差额 68 条为服务端折叠/隐藏条目，分页返回不完整） |
| 输出目录 | `E:\一人公司\公众号写作\Obsidian\testobsidian\知乎高赞\丧心病狂刘老湿\` |
| 输出内容 | 1560 个回答 md（`序号_标题.md`）+ `_目录.md` 全量索引（共 1561 个文件，9.94 MB） |

## 二、技术路线

```
┌─ Playwright(系统Chrome) + stealth.min.js 消除 webdriver 指纹 + 登录态
│
├─ 页面 JS 上下文内 fetch members/answers 接口（同源自动携带 cookies，
│    指纹与真实浏览器一致，服务端风控放行，无需自行签名）
│
└─ Python 侧低频翻页（82 页，1.2s 间隔）→ HTML 正文 → bs4 + markdownify → md
```

## 三、关键发现（对照实验定界）

| # | 发现 | 实验依据 |
|---|---|---|
| 1 | members/answers 接口对 requests + 补环境签名（带完整 x-zse-96）返回 403(10003)「请求参数异常，请升级客户端后重试」；同链路收藏夹 items、relations/mutuals 均 200，签名与登录态本身有效 | 01 / 01b / 01c 脚本 |
| 2 | Playwright 自动化浏览器发起同一接口同样 403，且知乎 CEO（zhouyuan）页面同样显示「系统繁忙」→ 排除用户级限制 | 02 / 02c 脚本 |
| 3 | **注入 stealth.min.js 消除 navigator.webdriver 等指纹后，接口立即 200** → 403 根因是知乎对 members/answers 接口新增的自动化浏览器指纹风控（2026 新增，收藏夹 items 接口无此风控） | 02d 脚本 |
| 4 | 页面内 fetch（绕过前端签名拦截器、不带 x-zse-96）返回 200 → 登录态下该接口同样不校验签名；手动 fetch 即可，无需调用页面签名函数 | 03 脚本 |
| 5 | 分页条数不稳定（20~39/页），存在折叠条目导致服务端计数 1628 与去重后 1560 的差额 | 03 脚本运行日志 |

> 体会：知乎 web 端风控已从「签名校验」转向「浏览器指纹 + 接口分级」：收藏夹 items 无指纹风控，members/answers 有指纹风控。补环境签名链路保留（见 01_探测接口.py），但本任务实际未用签名——页面内 fetch 更省力。**简单优先：能页面内 fetch 就不自行签名。**

## 四、目录结构

```
知乎用户主页回答抓取实战/
├── 01_探测接口.py            requests+补环境签名 → 403(10003) 留档
├── 01b_对照实验.py           include/sort 参数对照（全 403）+ 收藏夹 items 对照（200）
├── 01c_对照实验2.py          用户级/接口级定界：zhouyuan 也 403，articles 也 403
├── 02_playwright拦截真实请求.py   浏览器真实 XHR 捕获（URL/头留档）
├── 02b_检查页面状态.py       页面文本 + SSR initialData 检查
├── 02c_验证页面与数据源.py    zhouyuan 页面同样「系统繁忙」→ 接口级限制实锤
├── 02d_stealth验证.py        stealth 注入 → 200，根因锁定【关键转折】
├── 03_抓取回答.py            【正式爬虫】页面内 fetch 82 页全量抓取
├── 04_生成Markdown.py        【成果生成】HTML→Markdown → Obsidian 目录
└── output/                   运行产物（结果数据，不入库）
    ├── answers_raw_pages.json    逐页原始响应
    ├── answers_all_items.json    合并去重后 1560 条
    ├── member_page.png           页面截图
    └── real_requests.json        浏览器真实请求留档
```

## 五、验证结果汇总

| 脚本 | 验证内容（关键数据） | 结果 | 日志 |
|---|---|---|---|
| 01_探测接口.py | 补环境签名 64 字符正常生成；answers 接口 403(10003) | 留档 | — |
| 01b_对照实验.py | 4 组参数全 403；收藏夹 items 200（totals=263） | PASS | — |
| 01c_对照实验2.py | zhouyuan answers 403；刘老湿 articles 403 → 接口级限制 | PASS | — |
| 02_playwright拦截真实请求.py | 浏览器 XHR：answers 403、mutuals 200；捕获新版 include 与 ws_qiangzhisafe 参数 | PASS | — |
| 02b_检查页面状态.py | 页面正常渲染但答案区「系统繁忙」；initialState 含空 answers 实体 | PASS | — |
| 02c_验证页面与数据源.py | zhouyuan 页面同样「系统繁忙」 | PASS | — |
| 02d_stealth验证.py | stealth 注入后 webdriver=None，answers 请求 200×2，页面正常显示回答 | **关键通过** | — |
| 03_抓取回答.py | 82 页全量：去重 1560 条（总数 1628），含全文 1557，is_end 正常 | ALL PASS | 终端输出 |
| 04_生成Markdown.py | **1560 个 md + 1 个索引**写入目标目录；3 条无正文（删除/折叠） | ALL PASS | 终端输出 |

## 六、复现方式

```powershell
cd newcases\知乎用户主页回答抓取实战
# 依赖：requests playwright markdownify beautifulsoup4
# 前置：../知乎收藏夹x-zse-96签名补环境抓取实战/output/zhihu_state.json 登录态
python 03_抓取回答.py       # 全量抓取 → output/answers_all_items.json
python 04_生成Markdown.py   # 生成 md 到 Obsidian 目录
```

## 七、合规声明

- 仅限学习研究，**禁止商用**；抓取频率低（82 页、间隔 1.2s、单线程）。
- 回答内容为公开分享数据，抓取结果仅本地存档，不公开传播。
- 登录凭证与全部结果数据通过 `.gitignore` 排除，不入公开仓库。
- 未突破任何付费/私密内容边界；登录态为账号本人正常状态。
