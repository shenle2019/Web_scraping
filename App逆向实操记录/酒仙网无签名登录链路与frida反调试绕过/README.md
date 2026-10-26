# 酒仙网无签名登录链路与 frida 反调试绕过

> 本目录所有代码仅限学习研究，禁止商用。全程未使用真实账号登录线上站点，验证链路走本地 mock 服务端。

## 一、案例目标

复刻 day23 酒仙网 v9.1.13 的注册登录 + 预约链路，并验证课件里的两个对抗点：

1. 接口本身**没有签名**，`appKey` / `deviceIdentify` / `pushToken` 这些参数删掉也能通；
2. App 有 frida 反调试，普通 `frida-server` 一挂上就被杀，换 **hluda（strongR-frida 16.2.1）** 才能稳定 hook；
3. 附带用 `frida-dexdump` 脱壳，确认壳内 dex 可 dump。

## 二、课件结论（读课件后整理）

| 项目 | 结论 |
| --- | --- |
| 接口前缀 | `api.jiuxian.com`（抓包可见），走 `okhttp/3.14.9`，请求头只带 `secure: false` |
| 签名 | 无。四个接口全部明文表单/query，改参数不影响返回 |
| 可删参数 | `appKey`、`deviceIdentify`、`pushToken`、`channelCode` 等埋点字段 |
| 验证码 | `graphCode.htm` 出图 → `mobileCode.htm` 校验，4 位数字 + 干扰线，ddddocr 单次成功率约 80% |
| 登录 | `loginMobileFast.htm`（短信）/ `loginUserNamePassWd.htm`（账密），返回 `userInfo.token`（41 位） |
| 预约 | `preReservation.htm` 带 token，重复预约固定返回 `errCode=1200601` |
| 反调试 | 检测线程名 `gum-js-loop`、`pool-spawner`、`re.frida.server` 与 `frida-server` 进程名；检出即杀进程 |

## 三、实现思路

真实站点不适合反复登录试错（会触发风控），因此把链路拆成两半：

```
01_login_flow.py  ──HTTP──>  mock_server.py（本地 127.0.0.1:8008）
                                   │
                                   └─ 参数名/返回结构/错误码对齐课件抓包
02_anti_frida_check.py ──frida──> 真机上的酒仙 APK（只做 hook 取证，不登录）
```

- `mock_server.py`：`http.server.ThreadingHTTPServer` 手写四个接口，PIL 现场画 4 位验证码，token 用 `%032x%09d` 生成 41 位对齐真实长度；短信码固定 `1234`，通过 `/__mock/sms` 暴露给脚本（真实环境里这一步是看手机）。
- `01_login_flow.py`：ddddocr 识别 → 校验 → 短信登录 → 账密登录 → 预约两次（第二次必须 `1200601`）。
- `02_anti_frida_check.py`：`static` 模式扫二进制特征串；`device` 模式把 hluda 推到 `/data/local/tmp`，spawn 酒仙、注入脚本、6 秒后看进程是否还活着。

> 踩坑：Windows 中文主机名下 `HTTPServer.server_bind()` 会因 `socket.getfqdn()` 解码失败抛 `UnicodeDecodeError`，已用子类覆盖 `server_bind` 跳过反查。

## 四、运行方式

```powershell
# 1) 起 mock 服务端
python mock_server.py 8008

# 2) 跑登录 + 预约链路（结果写文件）
python 01_login_flow.py --out evidence_01_login_flow.log

# 3) 静态对比两个 frida-server 的特征串
python 02_anti_frida_check.py static

# 4) 设备侧：hluda 模式（frida 16.2.1 venv）/ 普通模式（系统 frida 16.3.3）
.\frida1621\Scripts\python.exe 02_anti_frida_check.py device --mode hluda
python 02_anti_frida_check.py device --mode frida

# 5) 脱壳
frida-dexdump -U -f com.jiuxianapk.ui -d
```

依赖：`requests`、`Pillow`、`ddddocr`、`frida==16.3.3`、`frida-dexdump`；hluda 用 `frida==16.2.1` 单独建 venv。

## 五、实测结果

### 1) 登录 + 预约链路（本地 mock）

```
[captcha] 第1次 OCR='8728' -> 通过
[sms-login] HTTP 200 ok            token=9c126d715bb20313825d96187d17b955879397091
[pwd-login] HTTP 200 ok            token2=3b19a02096a3bdb04d8458744bc4e1b1660897705
[reservation] success=1
[reservation] success=0 errMsg=您已预约成功，不需重复预约
结论：PASS 全部链路跑通
```

证据：[evidence/01_login_flow.txt](evidence/01_login_flow.txt)

### 2) frida 反调试对照（真机 Android 11 / Pixel 2 / magisk root）

静态特征串：

| 二进制 | gum-js-loop | re.frida.server | linjector | frida-server | pool-spawner |
| --- | --- | --- | --- | --- | --- |
| hluda-server-16.2.1 | **0** | **0** | 1 | 3 | 4 |
| frida-server-16.3.3 | 2 | 1 | 1 | 3 | 4 |

动态：

| 模式 | spawn | hook 消息 | 6 秒后进程 | 结论 |
| --- | --- | --- | --- | --- |
| hluda 16.2.1 | pid=27257 | `loaded classes = 16317` | 27257 存活 | **PASS** |
| frida-server 16.3.3 | pid=27451 | 无 | 27488（已重启） | **FAIL 被杀** |

证据：[evidence/02_hluda_device.txt](evidence/02_hluda_device.txt)、[evidence/02_frida_device.txt](evidence/02_frida_device.txt)

### 3) 脱壳

`frida-dexdump -U -f com.jiuxianapk.ui -d` → 45 个 dex，合计 98.5 MB，最大 `classes02.dex`，日志末行 `All done`。dex 文件属于第三方 App 代码，不入库，仅保留日志。

证据：[evidence/03_dexdump.txt](evidence/03_dexdump.txt)

## 六、文件说明

| 文件 | 作用 |
| --- | --- |
| `mock_server.py` | 本地 mock 服务端，复刻四个接口 + 图形/短信验证码 + 重复预约态 |
| `01_login_flow.py` | 客户端全链路脚本（OCR → 短信登录 → 账密登录 → 预约两次） |
| `02_anti_frida_check.py` | frida 特征串静态对比 + 真机 hluda/frida-server 动态对照 |
| `evidence/` | 运行日志（扩展名改为 .txt 以避开仓库 `*.log` 忽略规则） |

## 七、结论

- 酒仙网这套接口确实**零签名**，风控重心在验证码与登录态，OCR 用 ddddocr 足够。
- frida 反调试是**进程/线程名特征检测**，不是 ptrace 占坑，所以换 hluda 即可绕过；这也解释了为什么课件要求固定用 16.2.1 版本的 hluda。
- 复刻版走本地 mock，往返 8 次请求，未触碰线上登录接口，不存在封号风险。
