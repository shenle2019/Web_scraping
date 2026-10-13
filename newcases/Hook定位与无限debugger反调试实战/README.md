# Hook 定位与无限 debugger 反调试实战

> 对应课件：《Day25：JS逆向爬虫基础案例06》（eval 函数 / hook 函数 / Object.defineProperty / hook cookie / hook header / 无限 debugger）
>
> 交付形式：把课件 7 个案例**按自己的思路重写一遍**，并组装成一个端到端可复现的实战项目。

## 一、项目思路

课件里的案例是零散 JS 片段，缺少可端到端验证的场景。本项目自建了一个「迷你风控站」（本地模拟站，数据全部自造），把课件全部技术点串成一条真实爬虫工作流：

| 站点机制 | 对应课件 | 逆向手段 |
|---|---|---|
| 核心算法与密钥被 `eval(atob(base64))` 混淆 | 01/02 eval 函数 | hook_eval.js 打印 eval/atob 入参，运行时还原明文 |
| 访问令牌写入 cookie（`access_token`） | 05 hook cookie | hook_cookie.js 拦截写入 + 调用栈定位生成位置 |
| 数据接口要求 `X-Sign` 签名头 | 06 hook header | hook_header.js 拦截 XHR `setRequestHeader` / fetch 双通路 |
| 页面挂双链「无限 debugger」拖住分析者 | 07 无限debugger | anti_debugger.js 源头切断；23 用 CDP 做真断点对照 |
| Hook 底座：属性读写拦截 + 原生透传 | 03/04 hook函数 | `Object.defineProperty` + 从原型取原生描述符 |

最终链路：**对抗反调试 → Hook 定位风控参数 → 采集数据 → 离线纯算复刻 → 脱离浏览器直连**。

## 二、目录结构

```
Hook定位与无限debugger反调试实战/
├── 10_local_server.py            本地模拟站服务（端口 18888，cookie 令牌 + X-Sign 双重校验）
├── server_assets/
│   ├── index.html                商品列表页
│   └── main.js                   站点核心脚本（eval 混淆 / 令牌 / 签名 / 双链无限 debugger）
├── hook_scripts/
│   ├── hook_cookie.js            Hook document.cookie（原生描述符 + 原生 setter 透传）
│   ├── hook_header.js            Hook XHR setRequestHeader / fetch 双通路
│   ├── hook_eval.js              Hook eval / Function 构造器 / atob 三入口
│   └── anti_debugger.js          无限 debugger 源头切断（setInterval/setTimeout/Function/eval）
├── pw_common.py                 公共辅助（本地站上下文、Edge 启动、脚本注入、断言）
├── 01_eval_verify.py            eval/exec 分工与作用域（Python 侧）
├── 02_keypoints_verify.js       课件四大知识点 JS 侧重写验证（Node 运行）
├── 20_hook_cookie_capture.py    Playwright：拦截 cookie 写入 + 调用栈定位
├── 21_hook_header_capture.py    Playwright：捕获 X-Sign 签名头 + 调用栈定位
├── 22_hook_eval_capture.py      Playwright：混淆代码运行时还原 + 密钥提取
├── 23_anti_debugger_cdp.py      Playwright + CDP：无限 debugger 真断点对照实验
├── 30_crawler_full.py           完整爬虫：对抗反调试 + Hook 定位 + 采集（输出 output/*.json）
├── 31_offline_replica_verify.py Hook 取证 → Python 纯算复刻 → requests 直连验证
└── _run_*.txt                   各脚本运行日志（作业验证结果，UTF-8）
```

## 三、验证结果汇总（全部通过）

| 脚本 | 对应课件 | 验证内容（关键数据） | 结果 | 日志 |
|---|---|---|---|---|
| 01_eval_verify.py | 01 | Python 分工：eval=表达式 / exec=语句；混淆字符串静态隐身 | ALL PASS | _run_01_eval.txt |
| 02_keypoints_verify.js | 01/03/04/07 | 严格模式 eval 作用域、间接 eval 全局化、调用链、defineProperty 拦截/防拆除、六种无限 debugger 写法 | 13 PASS / 0 FAIL | _run_02_keypoints.txt |
| 10_local_server.py `--selftest` | — | 双重风控四种凭证组合：403/403/403/200 | PASS | _run_10_server_selftest.txt |
| 20_hook_cookie_capture.py | 05 | 拦截 `access_token=af55d6ca08bf31a8`，调用栈定位到 main.js:20；透传无损 | 4 PASS | _run_20_hook_cookie.txt |
| 21_hook_header_capture.py | 06 | 捕获 `X-Sign=545ff68598591473`，调用栈定位到 `fetchGoods (main.js:51)` | 4 PASS | _run_21_hook_header.txt |
| 22_hook_eval_capture.py | 02/07 | eval=3/atob=1/Function=1；全 base64 混淆段还原出 `secHash` 明文与两个密钥 | 4 PASS | _run_22_hook_eval.txt |
| 23_anti_debugger_cdp.py | 07 | CDP 对照：未对抗 3 秒内 8 次真实断点暂停；注入对抗后 0 次，且链1/链2 留痕、页面功能无损 | 6 PASS | _run_23_anti_debugger.txt |
| 30_crawler_full.py | 综合 | 接口响应路线 12 条 + DOM 对照 12 条；令牌/签名/密钥全部被 hook 捕获；数据落盘 | 6 PASS | _run_30_crawler_full.txt |
| 31_offline_replica_verify.py | 综合 | 复刻 token/X-Sign == 页面真实值；requests 直连自造新签名 200、错误签名 403 | 4 PASS | _run_31_offline_replica.txt |

> 说明：日志中展示的 `X-Sign` 每次运行不同（`ts` 为毫秒时间戳参与签名），`access_token` 当天固定（按 UTC 日期生成）。

## 四、复现方式

```powershell
# 依赖：Python 3.8+、playwright（复用系统 Edge，无需 playwright install）、requests
pip install playwright requests

# 1) 服务端双重风控自测
python 10_local_server.py --selftest

# 2) 课件知识点重写验证
python 01_eval_verify.py
node 02_keypoints_verify.js

# 3) Playwright Hook 实战（自动启停本地站）
python 20_hook_cookie_capture.py
python 21_hook_header_capture.py
python 22_hook_eval_capture.py
python 23_anti_debugger_cdp.py

# 4) 完整爬虫 + 离线复刻闭环
python 30_crawler_full.py
python 31_offline_replica_verify.py

# 人工浏览调试（Chrome DevTools 手动下断点观察 Hook 效果）
python 10_local_server.py    # 打开 http://127.0.0.1:18888/
```

## 五、关键技术说明

- **Hook 底座**：从 `Document.prototype` / `XMLHttpRequest.prototype` 取原生属性描述符，用 `Object.defineProperty` 覆盖，拦截后通过原生 setter/method 透传——不破坏页面功能，页面自身零感知。
- **调用栈定位**：Hook 回调里打 `new Error().stack`，直接看到「谁在什么时候写入了 cookie / 设置了签名头」，一步定位到 `main.js` 具体行号。
- **无限 debugger 对抗**：不是「跳过断点」，而是**源头切断**——回调 `toString()` 含 `debugger` 的定时器替换为空回调、`Function` 构造器去势、eval 剥离关键字；本项目的设计细节是链2 日志不含 "debugger" 字样，实现「掐断构造器但链本身存活」，验证对抗不影响页面既有逻辑。
- **CDP 对照实验**：headless 下无调试器挂载时 `debugger` 是空操作，所以用 CDP `Debugger.enable` 挂载真实调试器 → 统计 `Debugger.paused` 次数，把「拖住分析者」这个主观现象变成可量化的数字（8 次 vs 0 次）。
- **纯算复刻闭环**：hook_eval 还原的明文即算法的第一手资料；用 Python 重写 `secHash`（`h1=((h1<<5)+h1+c)>>>0`，`>>>0` 等价 `& 0xFFFFFFFF`），比对页面真实值一致后走 `requests` 直连——证明已完全脱离浏览器与反调试体系。

## 六、合规声明

本项目所有目标均为**本地模拟站**（`127.0.0.1:18888`），页面、接口、数据、密钥全部自造，无任何真实站点请求，仅用于逆向技术学习与课件作业验证。
