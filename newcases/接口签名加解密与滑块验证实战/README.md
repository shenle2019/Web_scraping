# 接口签名加解密与滑块验证实战：三案例爬虫破解说明

> 围绕三个目标站点的请求签名、接口加解密与滑块验证进行的完整逆向实践。
> 三个案例全部攻克，正式脚本位于本目录 `20/21/22` 开头，结果输出到 `作业结果/`。

## 案例目标（原始要求 base64 解码后）

| 案例 | 目标网站 | 目标接口要求 |
| --- | --- | --- |
| 案例1 | `https://www.jiansheku.com/search/enterprise/p3/`（建设库） | 页码对应的页面数据（page） |
| 案例2 | `https://search.bidcenter.com.cn/search?keywords=服务`（采招网） | **数据加密的接口，进行解密** |
| 案例3 | `https://www.qimingpian.com/`（企名片） | `https://vipapi.qimingpian.cn/HomePage/recommendInfo` |

## 环境

- Python 3 + `requests` / `pycryptodome` / `playwright`（channel="chrome" 使用本机 Chrome）
- Windows PowerShell 运行需先设置 UTF-8：`$env:PYTHONIOENCODING='utf-8'`

---

## 案例1：建设库（sign 签名逆向 → API 直连）

**反爬机制**：搜索接口 `POST https://capi.jiansheku.com/nationzj/enterprice/page`
请求头带 `sign`、`timestamp` 双签名参数，直接请求返回 403/失败。

**破解过程**：
1. 从页面加载的打包 JS 里定位到 sign 生成函数（三层 MD5 套娃）：
   - `sign = Su(K3, Su(K2, Su(K1, Cu(param), ts), ts), ts)`，即三次 `MD5(data + key + ts)` 嵌套
   - `Cu(param)`：body 参数按 key 排序后拼接 `key=value&`（空值跳过）
   - K1/K2/K3 三个密钥硬编码在 JS 中（详见 `20_案例1_建设库爬虫.py`）
2. 用 Python `hashlib` 完整复刻该算法，实测接口返回 `code:200`（全站约 1.5 亿条企业数据）
3. 探测返回字段结构（`19_建设库字段探测.py`），确定交付字段

**结果**：`20_案例1_建设库爬虫.py` 抓取 3 页 × 20 条 = **60 条企业数据**
（中国电信、中移建设、中国联通等，含法人/注册资本/信用代码/资质数/中标业绩等 18 个字段）
→ `作业结果/案例1_建设库_企业数据.json / .csv`

## 案例2：招标网（采招网，三层反爬 → 全链路复刻）

**反爬机制（三层）**：

1. **阿里云滑块人机验证**：首次访问被重定向到 `HumanMachineVerificationTest4.shtml`
2. **JS 异步渲染**：过验证后 requests 拿到的仍只是壳页面，结果由 JS 动态加载
3. **接口响应加密**：数据接口返回加密 base64 密文

**破解过程**：

1. **滑块**：Playwright 真实浏览器（headed 模式，headless 会被识别）+ 定位滑块
   （`#aliyunCaptcha-sliding-slider`，Playwright 选择器可穿透 shadow DOM），
   用 easeOutCubic 缓动 + 微抖动模拟人类轨迹拖动，验证通过后导出 cookies
   （`21b_招标网滑块攻坚.py`，cookies 缓存在 `分析素材/bidcenter_cookies.json`，requests 可复用）
2. **定位接口**：抓 XHR 得到 `POST https://interface.bidcenter.com.cn/search/GetSearchProHandler.ashx`
   （`21f_抓招标XHR接口.py`），穷举下载页面 26 个 JS 后锁定加密逻辑在 `searchv17.js`
3. **解密**：`searchv17.js` 中 `AESDecrypt` 使用 `AES-CBC + ZeroPadding`，
   KEY/IV 藏在页面变量 `variate.key / variate.aceIV` 的 `words` 数组里
   （CryptoJS 的 WordArray，4 个 32bit 整数，按大端序拼 16 字节）
   → Python `pycryptodome` 复刻，解密成功（`21h/21i` 验证）
4. **请求复刻**：form 参数 `from/guid(uuid4)/location/token/deftag/keywords(双重编码)/mod/vtime(毫秒时间戳)`，
   翻页加 `page=N`；解密后数据在 `other2.listData`（每页 40 条）

**结果**：`21_案例2_招标网爬虫.py` 抓取 3 页 × 40 条 = **120 条招标数据**
（站方声称共 2.2 亿条；含标题/类型/地区/采购方式/中标金额/链接等字段，翻页已实测有效）
→ `作业结果/案例2_招标网_服务搜索结果.json / .csv`

## 案例3：企名片（3DES 解密）

**反爬机制**：`GET https://vipapi.qimingpian.cn/HomePage/recommendInfo` 返回
`{"status":0,"encrypt_data":"<base64密文>"}`，真实数据 DES3 加密。

**破解过程**：
1. 下载站点 JS 收集可疑加密函数（`04/08_企名片JS收集.py`），定位到 `kt` 解密函数
2. 从 JS 中提取密钥 `5e5062e82f15fe4ca9d24bc5`（24 字节 = 3DES 密钥）
3. Python 复刻：`DES3.new(key, MODE_ECB)` 解密 + 去除 PKCS7 填充（末尾字节 ≤ 8 截掉）

**结果**：`22_案例3_企名片爬虫.py` 抓取 **10 条**推荐资讯
（id/标题/链接/发布时间/配图）→ `作业结果/案例3_企名片_推荐资讯.json / .csv`

---

## 文件说明

- **正式交付脚本**：`20_案例1_建设库爬虫.py`、`21_案例2_招标网爬虫.py`、`22_案例3_企名片爬虫.py`
  （均自包含加密算法，可直接运行）
- **分析过程脚本**：`00~19` 探测/验证系列，`21a~21i` 招标网攻坚系列（滑块、抓包、JS 定位、解密验证）
- **结果输出**：`作业结果/`（三案例 JSON + CSV；含第三方数据与已公开个人信息，**仅本地保留**，已加入 `.gitignore`，不入公开仓库）
- **分析素材**：`分析素材/`（抓包 HTML、XHR JSON、下载的 JS、cookies、解密样本）

## 运行方式

```powershell
cd e:\webspider\Web_scraping\newcases\接口签名加解密与滑块验证实战
$env:PYTHONIOENCODING='utf-8'
python 20_案例1_建设库爬虫.py   # 案例1
python 21_案例2_招标网爬虫.py   # 案例2（cookies 失效时会自动弹浏览器过滑块）
python 22_案例3_企名片爬虫.py   # 案例3
```

## 合规声明（重要）

本目录脚本均为**个人学习研究**用途的逆向技术练习，严格执行以下边界：

- **仅限学习**：不得用于商业用途、规模化抓取或数据转卖；不得注册账号以规避站方限制。
- **低频访问**：保持小批量（数页）与请求间隔（≥1 秒），不对目标站点造成负担。
- **数据与凭证不入库**：抓取结果（`作业结果/`，含第三方数据及已公开个人信息）与会话凭证
  （cookies）仅本地保留，已通过 `.gitignore` 排除，严禁提交公开仓库。
- **边界变更先评估**：扩大抓取规模、更换用途或目标站前，先核对目标站 robots.txt 与用户协议。

## 备注

- 案例2 的 cookies 有效期有限，失效后运行 `21b_招标网滑块攻坚.py` 或直接跑 `21_案例2_招标网爬虫.py`（内置自动刷新）即可。
- 滑块验证需真实浏览器窗口（headed），headless 会被阿里云风控识别，这是本案例的关键点。
