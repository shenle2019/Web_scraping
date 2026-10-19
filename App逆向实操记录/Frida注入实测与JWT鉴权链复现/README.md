# Frida 注入实测与金树林 JWT 鉴权链复现

复刻课件 `day04-hook和逆向案例` 的实操记录。目标有三块：电脑端 frida 安装、手机端 frida-server 部署、车智赢 hook 与金树林抓包逆向案例。所有结论均来自本机实测，失败项如实记录。

## 环境

| 项 | 实际情况 |
| --- | --- |
| 电脑 | Windows 10，Python 3.8.8 |
| frida（电脑） | frida 16.3.3 + frida-tools 13.7.1（pip 安装） |
| 手机 | Pixel 2 XL，Android 11，arm64-v8a，Magisk root |
| frida-server（手机） | 16.3.3，部署路径 /data/local/tmp/fs1663 |
| 目标 app | 车智赢 5.6.1；金树林 1.0.27（仅用于核对接口域名） |

## 目录内容

| 文件 | 作用 |
| --- | --- |
| `00_环境探测.py` | 检查 frida 版本、adb 连接、frida-server 进程、端口转发、远程设备进程数与前台应用 |
| `01_金树林接口探测.py` | DNS / TCP 443 / TCP 80 / HTTPS 接口 / robots.txt 可达性探测 |
| `02_本地Mock服务.py` | 按课件请求契约复刻 phoneCode、memberRegister、login、searchByPage 四个接口（JWT 自签） |
| `03_金树林登录链复现.py` | 取码 → 注册 → 登录拿 JWT → 带 Mobile-Token 搜索商品，可用 `--base-url` 切换真实站点或 Mock |
| `04_车智赢Hook验证_attach.py` | attach 方案：主动调用 encodeMD5 验证 + 挂 implementation 等真实登录 |
| `05_车智赢Hook实测_spawn.py` | spawn 方案：spawn → attach → load → resume，观察 15 秒存活状态 |
| `logs/` | 本次全部运行日志与崩溃栈 |

## 实测结果（2026-10-19）

| # | 环节 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 电脑端安装 frida | 成功 | pip 安装 frida 16.3.3 / frida-tools 13.7.1 |
| 2 | 手机端部署 frida-server | 成功 | xz 解压出 56,466,624 字节 → push 到 /data/local/tmp/fs1663 → chmod 755 → root 启动；`adb forward` 27042/27043 |
| 3 | frida 远程连接 | 成功 | 枚举到 143 个进程；`get_frontmost_application()` 在桌面时返回 None，app 在前台时正常返回车智赢 |
| 4 | attach hook 主动调用 | 成功 | `encodeMD5('1111111') = 7fa8282ad93047a4d6fe6111c93b308a`，与 day03 抓包密文一致 |
| 5 | attach hook 真实登录 | 失败（预期外） | 点击登录后 hook 无输出，app 主进程崩溃；crash buffer 回溯落在 `/memfd:frida-agent-64.so`，判定应用带 Frida 检测，见 `04_czy_login_crash_logcat.txt` |
| 6 | spawn hook | 失败（同上） | spawn 到 pid 29489，resume 后 15 秒内进程退出（ALIVE False），未收到 Java 层 hook 消息 |
| 7 | DES 加解密演示 | 成功 | 课件 5-des加密.py 原样运行：密文 `b'\x1c\xd5\xae\x17...'`，解密回 `b'hello world'` |
| 8 | 金树林真实接口 | 失败（站点下线） | DNS 解析到 112.124.33.43，443/80 全部 WinError 10061 积极拒绝；robots.txt 同样不可达；1.0.27 apk 内域名仍为 miappshop.jshulin.com，排除域名迁移 |
| 9 | 金树林链路（本地 Mock） | 成功 | 4 个接口全 200；登录返回 JWT，payload 解出 aud/exp/iat/userId/username；searchByPage 带 Mobile-Token 返回 total=4 |

关于第 5、6 项：hook 方法本身没有写错。主动调用能算出与抓包一致的 MD5，说明类名、方法名、注入链路都正确；崩溃发生在应用侧检测逻辑，属于目标 app 的防护行为，不是脚本 bug。结论：该版本车智赢在注入状态下无法走完真实登录，hook 实测停在主动调用验证层。

## 金树林案例实操代码做了什么

按层拆开看，课件 11 个脚本实际就做了四件事：

**1. 环境与注入（0/1/2/3/4）**
- 0-端口转发：`adb forward tcp:27042/27043`，把手机上的 frida-server 映射到本机。
- 1-打印进程：`frida.get_remote_device().enumerate_processes()` 找目标进程。
- 2/3-hook 车智赢：attach 与 spawn 两套固定骨架。区别只在开头：attach 直接 `rdev.attach("车智赢+")`，spawn 先 `pid = rdev.spawn(["包名"])`、`attach(pid)`，load 完必须 `resume(pid)`。
- 4-js 脚本：把同一段 hook JS 落成文件，用 frida CLI `-l` 加载，便于反复调试。

**2. 算法层（5/10）**
- 5-des加密：DES/ECB，key 固定 8 字节，手动补 `=` 到 8 的倍数，解密后按补位长度截断。演示了对称加密"同密钥可逆"的特征。
- 10-url 编码：`quote`/`unquote` 处理中文参数（上海 ↔ %E4%B8%8A%E6%B5%B7）。

**3. 业务链路（6/7/8/9）**
| 步骤 | 接口 | 关键点 |
| --- | --- | --- |
| 取码 | GET /memberLogin/phoneCode | `serviceType=6` 登录用码，`5` 注册用码 |
| 注册 | POST /memberLogin/memberRegister | JSON 体 phone/fid/password/phoneCode |
| 登录 | POST /memberLogin/login | 返回 `data.token`（JWT）与 tokenLong |
| 搜索 | POST /pro/searchByPage | 请求头 `Mobile-Token: <token>` 鉴权 |

**4. 工具函数（utils.py）**
- `header_str_to_dict`：把 Charles 复制的原始 header 文本按行、按 Tab 切成字典。
- `query_to_dict`：把 `a=1&b=2` 切参数字典。都是减少手工搬运的胶水代码。

本目录把上述 4 段脚本合并成 `03_金树林登录链复现.py` 一条可参数化链路，并额外做 JWT payload 解码；真实站点不可达时，用 `02_本地Mock服务.py` 验证同一套请求契约。

## 运行方式

```bash
# 1. 环境自检（手机需已连电脑并启动 frida-server）
python 00_环境探测.py

# 2. 目标站点可达性探测
python 01_金树林接口探测.py

# 3. 本地链路验证：终端 A 起 Mock
python 02_本地Mock服务.py
# 终端 B 跑链路
python 03_金树林登录链复现.py --base-url http://127.0.0.1:18080

# 4. 真实站点链路（当前预期失败，用于留证）
python 03_金树林登录链复现.py

# 5. 车智赢 hook（手机连电脑、app 在登录页）
python 04_车智赢Hook验证_attach.py
python 05_车智赢Hook实测_spawn.py
```

## 合规说明

- 全部脚本仅限学习研究，禁止商用；脚本头部均带声明。
- 仅使用占位手机号 13800000000 与虚构 Mock 数据，不包含任何真实账号、验证码、token。
- 请求低频：链路步骤间隔 ≥1 秒，单线程。
- 目标站已下线，未对真实业务发起注册/登录；robots.txt 因站点不可达无法获取，已如实记录。
- 结果日志不含凭证类敏感数据。

## 踩坑记录

1. **中文路径导致 `adb push` 异常**：先在纯 ASCII 临时路径中转再 push。
2. **frida-server 被强杀客户端后残留会话**：attach 会挂起无输出，重启 frida-server 即恢复。
3. **PowerShell 管道按 GBK 解码 Python 输出**：日志出现乱码。改为 Python 内部以 UTF-8 写日志文件（见 `logs/` 生成方式），不再依赖控制台编码。
4. **本机主机名含非 UTF-8 字节**：Python 3.8 `HTTPServer` 构造时 `getfqdn` 抛 `UnicodeDecodeError`，Mock 服务直接退出。已在 `02_本地Mock服务.py` 中重写 `server_bind` 跳过 `getfqdn` 修复。
