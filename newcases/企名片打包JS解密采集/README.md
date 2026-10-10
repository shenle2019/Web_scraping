# 企名片打包 JS 解密采集实战（webpack / ESM 逆向）

> 对应 Day22「今日练习」第 1 题：**把企名片用 webpack 做一下**。
> 本题核心：在站点打包 JS 中定位接口加密函数，还原解密算法，
> 并完成频道资讯接口的数据采集。

## 一、目标与反爬机制

**目标站点**：https://www.qimingpian.com/（企名片）

**目标接口**：

```
POST https://vipapi.qimingpian.cn/Activity/channelInformationByChannelName
表单参数：channel_name / page / num / unionid
响应：{"status":0,"message":"success","encrypt_data":"<base64密文>"}
```

**反爬机制**：接口返回 `encrypt_data` 为 3DES 加密后的 base64 密文，
真实数据（`list` 资讯列表）需解密后才能读取。

**打包形态说明**：作业年代站点为 webpack 打包；当前线上站点已升级为
Nuxt3 / Vite 的 ESM 构建产物（chunk 内为 `import {...} from "./entry.xxx.js"` 形态）。
两者的逆向思路完全一致：**定位加密调用链 → 提取函数 → 复刻 or 直接执行**。
本目录同时交付两条路线（见下）。

## 二、破解过程（分步探测式验证）

1. **定位加密调用链**：在页面 chunk（`daily-activity.af082922.js`）中找到：

   ```js
   V0(_) = JSON.parse(N0("sjdqmp20161205#_316@gfmt", L0.decode(_), 0, 0, "012345677890123", 1))
   ```

   其中 `N0` 为打包产物中**自定义实现的 3DES**（`B0` 为其密钥预处理函数）：
   - `N0(key, data, u, C, h, f)`：`u=0` 解密、`C=0` 走 ECB、`f=1` 为 PKCS7 去尾填充；
   - 通过括号配对从压缩代码中**原样提取** `N0`（5726 字符）与 `B0`（2642 字符），
     存于 `qmp_js_funcs/`，未做任何修改。

2. **密钥甄别**：`V0` 中硬编码的字符串 `sjdqmp20161205#_316@gfmt` 对
   `vipapi` 接口不适用（实测解密失败）；经样本验证，本接口实际使用的
   3DES 密钥为 `5e5062e82f15fe4ca9d24bc5`。

3. **双路验证**：
   - **路线 A（原版函数直调）**：Node 中 `eval` 提取出的原版 `N0/B0`，
     实时抓取接口密文并调用 `N0(key, bin, 0, 0, iv, 1)` 解密 → **成功解出 20 条**；
   - **路线 B（纯 Python 复刻）**：`pycryptodome` 的 `DES3.MODE_ECB` + 去 PKCS7 填充，
     与路线 A 解密结果**逐字节一致**。
   - 另用本地自造样本（Python 3DES-ECB 加密的 JSON）交叉验证两路线一致性。

4. **登录墙合规处理**：实测第 2 页起服务端返回
   `{"status":60004,"message":"未登录用户只能看20条数据"}`。
   **学习研究场景不绕过登录限制**，爬虫对该状态做友好识别并停止翻页。

## 三、验证结果（2026-10-10 实测）

| 验证项 | 结果 |
| --- | --- |
| Node 原版 N0/B0 函数解密实时数据 | **成功，20 条资讯** |
| Python 复刻 vs Node 原版解密 | **逐字节一致** |
| 本地自造样本交叉验证 | 两路线均与预期一致 |
| 爬虫实采 | **1 页 20 条**（第 2 页起为 60004 登录限制，合规停止） |

采集输出（`output/`）：

- `qmp_channel_raw_<时间戳>.json`：原始响应（含密文）
- `qmp_channel_items_<时间戳>.json / .csv`：20 条精简资讯（ID/标题/摘要/时间/链接等）
- `qmp_n0_js_decrypted_sample.json`：Node 原版函数解密样本

## 四、文件说明

- `qmp_channel_crawler.py`：**正式交付爬虫**（纯 Python 3DES 复刻解密，可直接运行）
- `qmp_n0_verify.js`：**原版函数验证器**（Node，直接执行打包 JS 中提取的 N0/B0 解密实时数据）
- `qmp_js_funcs/`：从打包 JS 中按括号配对**原样提取**的函数源码
  - `N0_des3.js`：自定义 3DES 解密函数
  - `B0_key_schedule.js`：密钥预处理函数
- `output/`：采集结果（含第三方公开数据，**仅本地保留**，已加 `.gitignore`）

配套探测脚本位于上级 `探查脚本/` 目录（编号 p54~p59），关键验证记录：

| 脚本 | 作用 |
| --- | --- |
| `p54_qmp_chunk_analyze.py` | 分析 chunk 中的接口线索与 N0 模式选择逻辑 |
| `p55_qmp_key_verify.py` | 密钥甄别：新 key FAIL / 老 key 解出 20 条 |
| `p56_qmp_build_struct.py` | 判定构建形态（Nuxt3/Vite ESM） |
| `p57_qmp_n0_extract.py` | 括号配对提取 N0 完整源码（含 B0） |
| `p58a_qmp_n0_prepare.py` | 构造本地样本 + 实时密文，Python 解密基准 |
| `p58b_qmp_n0_verify.js` | Node eval 原版函数解密两样本 → 与 Python 逐字节一致 |
| `p59_deploy_js_funcs.py` | 部署 N0/B0 源码到本目录 `qmp_js_funcs/` |

## 五、运行方式

```powershell
cd e:\webspider\Web_scraping\newcases\企名片打包JS解密采集
$env:PYTHONIOENCODING='utf-8'

# 路线 B：纯 Python 爬虫（默认 3 页）
python qmp_channel_crawler.py
python qmp_channel_crawler.py --pages 5 --channel 24新声

# 路线 A：Node 原版函数验证器（需 Node 18+，内置 fetch）
node qmp_n0_verify.js
```

依赖：`pip install requests pycryptodome`

## 六、合规声明（重要）

本目录脚本为**个人学习研究**用途的逆向技术练习，严格执行以下边界：

- **仅限学习**：不得用于商业用途、规模化抓取或数据转卖。
- **低频访问**：默认请求间隔 ≥ 1.5 秒、小批量采集（数页），不对目标站点造成负担。
- **不绕过登录限制**：服务端从第 2 页起要求登录（60004），脚本识别后主动停止翻页，
  不注册账号、不伪造身份绕过。
- **数据与凭证不入库**：采集结果仅本地保留，已通过 `.gitignore` 排除。
