# Day21 练习案例：四站 JS 逆向（请求签名 + 响应加密）

> 课件来源：`E:\路飞学城\课件\JS逆向\Day21：JS逆向爬虫基础案例02` 目录下的「练习案例」文件
> （4 个 base64 目标站点，本目录为完整练习交付：爬虫脚本 + 运行日志 + 验证结果）

## 0. 练习完成情况

课件「练习案例」给出 4 个 base64 目标。此前 Day21 只整理了学习笔记，**练习题本身未做过**；
本次全部完成并逐一验证通过，四个站点的逆向机制与验证结论如下。

## 1. 四站总览

| # | 站点 | 目标 base64 解码 | 逆向机制 | 验证结果 |
|---|------|------------------|----------|----------|
| 1 | 新东方搜课 | `https://souke.xdf.cn/search?cityCode=110100&kw=英语` | 请求头 `sign` = MD5 签名 | 错误 sign→400；正确→200，classList 12 条 |
| 2 | 精灵数据 | `https://www.jinglingshuju.com/articles` | 响应 `data` 字段 AES-ECB 加密 | 密文 6336 字符→解出 10 篇文章，total=1000 |
| 3 | 扇贝单词 | `https://web.shanbay.com/wordsweb/#/words-table` | 响应自定义字符集编码（PRNG + Trie） | 课件真实样本（43708 字符）解码成功 |
| 4 | 贝壳找房 | `https://bj.ke.com/?utm_source=baidu&...` | SSR 内嵌参数 + JSONP 异步接口 | sidebar errno=0；搜索建议 15 条 |

## 2. 分站说明

### 2.1 新东方搜课 souke.xdf.cn —— 请求头 sign 签名（MD5）

- **脚本**：`souke_sign_search.py`
- **接口**：`GET https://dsapi.xdf.cn/product/v2/class/search?{params}`
- **签名算法**（源码 `ot()` / `DTmv()` / `aCH8()`，crypto-js md5）：
  ```
  sign = MD5( params + "750F82C2-D8F6-49F6-878C-1E7EBEBC8DA2" )   # 小写 hex
  params = "appId=5053&t=<毫秒时间戳>" + 逐个追加 "&k=v"（跳过假值）
  请求头: {"Content-Type": "application/json", "sign": sign}
  ```
- **验证**（`_run_souke.txt`）：
  - 对照组（错误 sign）→ HTTP 400 `{"status":0,"message":"sign验证失败","code":"-1"}`
  - 正确 sign → HTTP 200，`totalRecords=1117`，`classList=12` 条
- **运行**：`python souke_sign_search.py`

### 2.2 精灵数据 jinglingshuju.com —— 响应体 AES 解密

- **脚本**：`jlsj_news_decrypt.py`
- **接口**：`POST https://vapi.jinglingshuju.com/Data/getNewsList`（form: `page=1&num=10`）
- **加密细节**（源码 `j="DXZWdxUZ5jgsUFPF"`，WordArray→ASCII，ECB 模式下 iv 为障眼法）：
  ```
  AES-ECB / PKCS7, key = "DXZWdxUZ5jgsUFPF"（16 字节）
  响应 data 为 base64 密文，解密后为 JSON
  ```
- **验证**（`_run_jlsj.txt`）：
  - HTTP 200，密文长度 6336
  - 对照组（错误 key）→ 乱码/异常，证明必须正确密钥
  - 正确 key → 文章 10 篇，total=1000，首篇《汉朔科技完成对哈步数据全资收购…》
- **运行**：`python jlsj_news_decrypt.py`

### 2.3 扇贝单词 web.shanbay.com —— 响应自定义编码（PRNG + Trie）

- **脚本**：`shanbay_wordsweb_decode.py`（双模式）
- **编码链路**（axios 响应拦截器 + 编码类 `k` / PRNG 类 / Trie 类，源码级复刻）：
  1. 版本头校验：`((32*S(c0)+S(c1))*S(c2)+S(c3)) % 32 <= 1`，`S(ch)= charCode>=65 ? ch-65 : ch-24`
  2. 密文前 4 字符 charCode 作 seed 初始化 MT19937 变种 PRNG（init 7 轮 + 预热 8 次）
  3. PRNG 为标准 base64 全部 64 字符生成"别名"填 Trie（A~J 每字符 1 符号，K 起 2 符号；
     符号集 `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567`，冲突避让）
  4. 密文自 index=4 起沿 Trie 贪心最长匹配还原标准 base64（`=` 透传）→ b64decode → JSON
- **重要发现**：真实加密接口为
  `apiv3.shanbay.com/wordsapp/user_material_books/{book}/learning/words/today_learning_items`（**需登录**）；
  匿名接口 `material_books` / `tags` 当前线上已返回**明文 JSON**（服务端策略变更，
  编译产物中 `custom:i` 的 `i` 为 undefined 变量，decode 分支不触发）。
  因此按合规要求不登录，改用**课件真实密文样本**做算法级强验证。
- **验证**（`_run_shanbay_sample.txt`）：
  - 样本 seed=5DEV，长度 43708，校验值 1（通过）
  - PRNG 前 10 值 `[26,18,8,19,6,10,1,21,28,6]`
  - 还原 base64 前缀 `eyJpcHAiOjEwLCJwYWdlIjo0LCJ0b3RhbCI6NTAsIm9iamVjdHMiOlt7InR5cGVf`
  - 解出 `ipp=10, page=4, total=50`，10 个单词：advanced / soar / evolve / associate /
    migrate / canal / slide / overnight / cite / decisive（与课件请求参数 page=4 完全吻合）
  - 在线模式：匿名请求 `material_books` 返回明文 JSON（日志 `_run_shanbay.txt`）
- **运行**：
  ```
  python shanbay_wordsweb_decode.py             # 在线请求匿名接口（当前为明文）
  python shanbay_wordsweb_decode.py --sample    # 离线解码 output/shanbay_cipher_sample.txt
  ```

### 2.4 贝壳找房 bj.ke.com —— SSR 内嵌参数 + JSONP 异步接口

- **脚本**：`ke_ershoufang_probe.py`
- **要点**（页面 SSR 结构 + `sellList/index.js` 异步调用定位）：
  1. 二手房列表页 `https://bj.ke.com/ershoufang/` 为 SSR 直出（首页 30 条，totalPage=100），
     页面内嵌 `window.GLOBAL_INFOS` 提供全部接口上下文：
     `url="/web/ershoufang/sidebar"`、`sidebar={type,cityId:110000,id:110000,uuid:<每页动态>,ucid}`、
     `count=<在售总数>`、`ids`（本页 30 套房源 id）
  2. 侧栏异步接口（`getAsyncData` 实现为 `$.ajax({url: API_URL+url, dataType:"jsonp"})`）：
     ```
     域名 = ljConf.domainConfig.ajaxapiroot = "https://ajax.api.ke.com/"（注意不是 bj.ke.com，直接请求 404）
     GET https://ajax.api.ke.com/web/ershoufang/sidebar
         ?cityId=110000&id=110000&uuid=<uuid>&ucid=&type=city&callback=jQuery...&_=<ts>
     应答为 JSONP 包装，解析后 errno=0
     ```
  3. 搜索建议：`GET https://bj.ke.com/api/headerSearchForPlatC?channel=ershoufang&cityId=110000&query=<kw>`
     （channel 映射 `{sell:"ershoufang",...}[type]`，cityId 原取自 cookie `select_city`）
- **验证**（`_run_ke.txt`）：
  - SSR：count=118448，本页 30 条 / ids 30 个，totalPage=100
  - sidebar：HTTP 200，JSONP 解析成功 **errno=0，request_id=10100719914375**，
    data 分区 `[price, agent, guide, resblock, redian, wenda, baike, vpoint, more_wenda_url, ditu]`
  - 搜索建议（query=望京）：code=0，**15 条**（望京 / 望京站 / 望京南站 / 望京西站 / 望京东站 …）
- **运行**：`python ke_ershoufang_probe.py`

## 3. 文件清单

```
多站请求签名与响应加密逆向/
├── souke_sign_search.py            # 站1 脚本（MD5 签名）
├── jlsj_news_decrypt.py            # 站2 脚本（AES-ECB 解密）
├── shanbay_wordsweb_decode.py      # 站3 脚本（自定义编码解码，--sample 双模式）
├── ke_ershoufang_probe.py          # 站4 脚本（SSR + JSONP 接口）
├── README.md                       # 本文件
├── _run_souke.txt                  # 站1 运行日志
├── _run_jlsj.txt                   # 站2 运行日志
├── _run_shanbay.txt                # 站3 在线模式日志
├── _run_shanbay_sample.txt         # 站3 离线样本模式日志
├── _run_ke.txt                     # 站4 运行日志
└── output/                         # 验证结果数据（已 gitignore，仅本地保留）
    ├── souke_sign_result.json
    ├── jlsj_news_result.json
    ├── shanbay_cipher_sample.txt   # 课件真实密文样本（43708 字符）
    ├── shanbay_sample_result.json  # 离线解码验证结果
    ├── shanbay_sample_decoded.json # 离线解码完整明文
    ├── shanbay_wordsweb_result.json
    └── ke_ershoufang_result.json
```

## 4. 合规声明

- 全部脚本**匿名**运行、**低频**（每个脚本每次运行 1~3 个请求），仅用于学习验证签名 /
  解密 / 接口参数逆向结论，**不批量翻页采集**、不绕过任何登录与风控。
- 扇贝站真实加密接口需登录，本次**未登录、未使用任何他人账号凭证**（老师课件中的登录
  凭证未复制进本目录），改用课件内公开的真实密文样本做离线算法验证。
- 输出数据含第三方内容（课程 / 文章 / 词表 / 房源），仅本地留存学习，
  `output/` 目录已在 `.gitignore` 中排除，不会提交到公开仓库。
