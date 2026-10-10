# 惠农网 H5 请求签名（x-client-sign）逆向实战

> 对应 Day22「今日练习」第 2 题：目标站点为 base64 编码串
> `aHR0cHM6Ly9tLmNuaG5iLmNvbS8=` 解码后的 **https://m.cnhnb.com/**（惠农网 H5 站）。
> 本题核心：逆向请求头中的 `x-client-sign` 签名算法，并用纯 Python 复刻后完成供应列表采集。

## 一、目标与反爬机制

**目标接口**：

```
POST https://appapi.cnhnb.com/recq/api/transform/supply/v501/index
请求体：{"pageNumber": N, "pageSize": 20, "ad_ch": 1}
响应：{"code":0,"msg":"success","data":{"datas":[...]}}
```

**反爬机制**：接口不校验 Cookie，但校验一组 `x-client-*` 请求头，
其中核心为 `x-client-sign` 签名（96 位 hex），由 `nonce / timestamp / deviceId` 与
内置密钥组合生成；另有 `x-b3-traceid`、`x-client-sid` 等辅助头。
缺少或伪造签名时接口返回 `code=500301`（"签名错误"）。

## 二、破解过程（分步探测式验证）

1. **定位签名函数**：抓包确认签名头后，下载 H5 站点加载的 `vendors.app.js`
   （webpack 模块 311），定位签名函数。
2. **提取算法与密钥**：签名函数按 `secretType` 分支，H5 场景取 `secretType=2`；
   生产环境密钥藏在经 RC4 混淆的字符串表中，解码后得到：
   `EOi^0N5sWWHhkrF2A0gekY9U20BgnAcr`。
3. **算法还原**（`secretType=2`，H5）：

   ```
   L = MD5(nonce)
   B = SHA1(timestamp)
   N = MD5(nonce + deviceId)
   C = SHA1(secret + timestamp)
   C = C[len-16 : len-1]              # 取中间 15 个 hex 字符
   D = 无符号十六进制转十进制(C)        # 复刻 Long.fromString(C, true, 16).toUnsigned().toString(10)
   sign = SHA384(L + "!" + B + "!" + N + "!" + D)
   ```

4. **双路验证**：
   - Node 调用打包 JS 模块 311 的签名函数，对 3 组真实抓包样本 3/3 匹配；
   - 纯 Python 复刻（`hashlib` + `int(C,16)`）对同样 3 组样本 3/3 匹配
     → 确认可脱离 Node 用纯 Python 实现。
5. **500301 攻坚（两大坑）**：Python 直连最初返回 500301，用对照组实验逐项排查：
   - **坑 1｜`x-hn-job` 头为必需**：该头内容为站方"招聘信"彩蛋
     （*If you see these message, I hope you dont hack us...*），服务端实际校验，
     缺省即 500301；
   - **坑 2｜deviceId 格式校验**：标准 uuid4（8-4-4-4-12）被拒，
     必须为 **7-4-4-4-9 位十六进制**（共 28 hex）格式。
6. **纯 Python 爬虫交付**：`cnhnb_supply_crawler.py`，内置签名器 + 翻页采集。

## 三、验证结果（2026-10-10 实测）

| 验证项 | 结果 |
| --- | --- |
| 纯 Python 签名器 vs 3 组抓包样本 | **3/3 全部匹配** |
| 实采（3 页 × 20 条） | **3 页 59 条真实供应数据，每页 code=0** |

采集输出（`output/`）：

- `cnhnb_supply_raw_<时间戳>.json`：3 页原始响应
- `cnhnb_supply_items_<时间戳>.json`：59 条精简字段（供应 ID/标题/价格/产地/店铺/发布时间等）

## 四、文件说明

- `cnhnb_supply_crawler.py`：**正式交付爬虫**（自包含签名算法，可直接运行）
- `output/`：采集结果（含第三方公开数据，**仅本地保留**，已加 `.gitignore`）

配套探测脚本位于上级 `探查脚本/` 目录（编号 p47~p53），关键验证记录：

| 脚本 | 作用 |
| --- | --- |
| `p46_call_sign311.js` | Node 直接调用打包 JS 模块 311 签名函数 |
| `p47_e2e_verify.js` | Node 端到端请求（模块 311 + fetch）跑通 |
| `p48_contrast.js` | 签名输入构造对照实验（排除"128 位"误判） |
| `p49_py_sign_verify.py` | 纯 Python 复刻签名 vs 3 组样本 → 3/3 PASS |
| `p50_device_test.py` | 定位 500301：固定样本 ID 也失败 → 是请求头差异 |
| `p51_header_test.py` / `p52_header_test2.py` | 对照组实验锁定 `x-hn-job` 为必需头 |
| `p53_device_test2.py` | 锁定 deviceId 需 7-4-4-4-9 十六进制格式 |

## 五、运行方式

```powershell
cd e:\webspider\Web_scraping\newcases\惠农网H5请求签名逆向
$env:PYTHONIOENCODING='utf-8'
python cnhnb_supply_crawler.py                 # 默认 3 页
python cnhnb_supply_crawler.py --pages 5       # 采集 5 页
```

依赖：`pip install requests`

## 六、合规声明（重要）

本目录脚本为**个人学习研究**用途的逆向技术练习，严格执行以下边界：

- **仅限学习**：不得用于商业用途、规模化抓取或数据转卖；不得注册账号以规避站方限制。
- **低频访问**：默认请求间隔 ≥ 1.5 秒、小批量采集（数页），不对目标站点造成负担。
- **数据与凭证不入库**：采集结果仅本地保留，已通过 `.gitignore` 排除。
- **签名头用途说明**：`x-hn-job` 为站方公开的"招聘信"内容，逆向研究仅用于通过服务端
  正常校验，不涉及任何越权数据访问。
