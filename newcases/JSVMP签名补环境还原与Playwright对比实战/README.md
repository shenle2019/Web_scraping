# JSVMP 签名补环境还原与 Playwright 对比实战

> 对应课件：《Day26：JS逆向爬虫基础案例07》（Proxy 代理 / 补环境 / JSVMP 小红书 X-s 签名还原 / execjs 联调）
>
> 交付形式：把课件案例**按自己的思路重写一遍**，组装成端到端可复现的实战项目，并对「补环境 JS 逆向」与「Playwright」两条技术路线做实测对比。

## 一、项目思路

课件案例是零散的补环境片段 + 一份 JSVMP 字节码资产（小红书 X-s 签名），缺少端到端闭环与量化对比。本项目自建「小红书签名 mock 站」（本地模拟站，数据全部自造），把课件技术点串成完整爬虫链路，并把两条路线的取舍做成数字。

| 站点机制 | 对应课件 | 本项目重写思路 |
|---|---|---|
| X-s 由 JSVMP（字节码 + 常量池）计算，算法不可读 | JSVMP 案例 | 不逆字节码：补环境让原字节码在 Node 里跑出签名 |
| 签名依赖浏览器环境（navigator / document / cookie） | 补环境 | 声明式 ENV_PLAN 注册表 + 访问监控器（闭包工厂版），替代课件 setProxy 字符串 eval 方案 |
| 服务端校验签名结构、时效 | 联调 | mock 站三层风控：结构 + X-t 时间窗 + 请求指纹白名单 |
| Python 侧驱动 JS 签名 | execjs 联调 | 不依赖 execjs（PyMiniRacer 兼容差），改用 Node CLI + base64 body 传参（规避 Windows 引号坑） |

最终链路：**补环境（Node 内跑 JSVMP）→ 签名 CLI → mock 站 200 → 反例全部 406**；另附 **Playwright 同款签名**与**双方案量化对比**。

## 二、目录结构

```
JSVMP签名补环境还原与Playwright对比实战/
├── js_asset/
│   └── source.js                 JSVMP 资产（课件复制，MD5 校验一致 D6585F43...）
├── 01_env_mini.js                补环境引擎（声明式 ENV_PLAN + 可选监控器 + cookie 注入）
├── 02_xhs_sign_cli.js            签名引擎（CLI + 库双形态：--path / --body-b64 / --count）
├── 03_sign_selftest.js           签名自检（结构 / 确定性 / 200 次压测）
├── 10_mock_server.py             本地 mock 站（端口 18999，三层签名校验，含 --selftest）
├── 20_spider_sign_pipeline.py    爬虫主流程（签名 -> 请求 -> 200 落盘 + 三组 406 反例）
├── 30_pw_sign_scheme.py          Playwright 方案（真实 Edge 内跑 JSVMP 签名）
├── 31_pw_vs_env_bench.py         双方案实测对比（冷启动 / 批量 / 结构 / 端到端）
├── pw_assets/
│   └── sign_page.html            Playwright 签名页（与补环境共用同一份 source.js）
├── pw_common.py                  公共辅助（本地站上下文 / Node 签名桥 / 发送工具）
├── run_log.py                    UTF-8 日志工具（生成 _run_*.txt）
└── _run_*.txt                    各脚本运行日志（作业验证结果，UTF-8）
```

## 三、验证结果汇总（全部通过）

| 脚本 | 验证内容（关键数据） | 结果 | 日志 |
|---|---|---|---|
| 03_sign_selftest.js | 签名 604 位 / 4 字段 / 384 hex payload；payload 头 32 稳定尾变化；200 次压测平均 24 ms | 11 PASS / 0 FAIL | _run_03_sign_selftest.txt |
| 10_mock_server.py `--selftest` | 三层风控五组合：无签名 406 / 伪造前缀 406 / 过期 406 / 伪造指纹 406 / 真实签名 200 | 5 PASS | _run_10_mock_selftest.txt |
| 20_spider_sign_pipeline.py | 正常流 200 + 12 条数据落盘；无签名 / 伪造指纹 / 签名过期三反例均 406 | 4 PASS / 0 FAIL | _run_20_spider_pipeline.txt |
| 30_pw_sign_scheme.py | 浏览器 cookie 修复 + webdriver 修正；签名 604 / 4 字段与补环境头 32 一致；端到端 200 | 6 PASS / 0 FAIL | _run_30_pw_sign.txt |
| 31_pw_vs_env_bench.py | 两方案结构完全同构（4 字段 / 384 / 同指纹头）；冷启动 118 ms vs 672 ms；纯执行 30.00 vs 24.56 ms/次 | 3 PASS / 0 FAIL | _run_31_pw_vs_env_bench.txt |

## 四、复现方式

```powershell
# 依赖：Python 3.8+、Node 18+、playwright（复用系统 Edge，无需 playwright install）、requests
pip install playwright requests

# 1) 签名引擎自检（Node：补环境 + JSVMP）
node 03_sign_selftest.js

# 2) mock 站三层风控自测
python 10_mock_server.py --selftest

# 3) 爬虫端到端（自动启停 mock 站）
python 20_spider_sign_pipeline.py

# 4) Playwright 方案 + 双方案对比实测
python 30_pw_sign_scheme.py
python 31_pw_vs_env_bench.py

# 人工浏览：python 10_mock_server.py  ->  http://127.0.0.1:18999/
```

## 五、关键技术说明

- **cookie 字段完整性驱动签名完整度（本项目矩阵实测发现）**：空 cookie → 简化签名（3 字段，payload 272 hex）；cookie 含 xsecappid 等 9 字段 → 完整签名（4 字段含 appId，payload 384 hex）。`xsecappid=xhs-pc-web` 是 appId 字段的来源；delete Buffer / Proxy 包装 / location 值均不影响签名结构。
- **payload 结构两段性**：同一输入多次调用，payload 头 32 位稳定（输入指纹段，只依赖 path + body），尾部变化（时间 / 熵成分）。补环境与真实浏览器两条链路产出的头 32 完全一致（4509d8ed...），用数字证明"补环境补对了"。
- **Node 21+ navigator 是只读 getter 全局**：直接赋值会被静默忽略，须 Object.defineProperty 覆盖；但实测 navigator（甚至 UA = "Node.js/24"）不影响签名结果——"能跑通 ≠ 补对了"的经典例证。
- **undici 惰性物化修复**：Node 20+ 删除 Buffer 后首次触发 undici 物化会整体崩溃；修复 = 补环境最先执行 `void globalThis.Headers` 先物化。
- **sloppy delete 的严格模式安全写法**：`globalThis.window = globalThis; delete globalThis.global;` 替代 `window = global; delete global`，语义等价且严格模式合法。
- **CLI 工程细节**：body 用 base64 传参（规避 Windows 命令行引号转义）；`process.exitCode` 替代 `process.exit()`（防 stdout 异步缓冲截断）。
- **mock 站校验的近似与局限**：服务端没有密钥、不能真算 JSVMP 签名，用「结构 + 时间窗 + 已知合法指纹白名单」做近似校验；黑盒签名无法防"body 替换 + 旧签名重放"，这正是真实站风控的密钥壁垒（详见对比文档）。
- **浏览器 document.cookie 批量写陷阱**：一次性写整串 "k1=v1; k2=v2..." 实测只落 1 条（Edge/Chrome），须逐条写入——这是 Playwright 方案实测踩到的第一道坑。

## 六、合规声明

本项目所有目标均为**本地模拟站**（`127.0.0.1:18999`），页面、接口、数据、密钥全部自造；签名资产仅用于本地离线计算；cookie 为值全占位的假数据（实盘场景用环境变量 `XHS_COOKIE` 注入真实凭证，凭证不入库），无任何真实站点请求，仅用于逆向技术学习与课件作业验证。
