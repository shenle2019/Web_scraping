# APP 登录加密与签名还原（爱安丘 / 尿大夫 / 合伙人）

复刻课件 `day05-反编译案例` 的实操记录。三个案例都在本机 + 真机上完整走了一遍：安装课件原版 APK → jadx 反编译定位算法 → Frida 实时 hook 取运行时值 → Python 本地复算 → 向真实接口重放请求。所有数值、响应、失败项均来自本次实测，没有伪造“登录成功”。

## 环境

| 项 | 实际情况 |
| --- | --- |
| 电脑 | Windows 11 22H2，Python 3.8.8 |
| 依赖 | frida 16.3.3、requests 2.32.4、pycryptodome 3.24.0 |
| 手机 | Pixel 2，Android 11，arm64-v8a，Magisk root |
| frida-server（手机） | 16.3.3，`/data/local/tmp/frida-server`，端口 27042/27043 已转发 |
| jadx | 1.4.7，GUI `D:\soft\jadx\jadx-gui-1.4.7.exe`，CLI `D:\soft\jadx-cli\bin\jadx.bat` |
| 爱安丘 | 1.0.5，包名 `com.iqilu.app137`，进程名 `爱安丘` |
| 尿大夫 | 4.1.11.230417，包名 `com.uulife.medical.activity`，进程名 `尿大夫` |
| 合伙人 | 1.4，包名 `com.yltx.oil.partner`，进程名 `油联合伙人` |

三款 APK 均来自课件 `软件/apps/`，安装后未升级。jadx 的 GUI 与 CLI 都装到了本机 `D:\soft`，`00_环境自检.py` 会检查两个路径和版本。

## 目录内容

| 文件 | 作用 |
| --- | --- |
| `00_环境自检.py` | 检查 adb 设备、机型/Android、frida-server 可用性、端口转发、frida 版本、jadx 路径、三款 APP 的 versionName |
| `01_爱安丘AES登录.py` | 复算 AES key 与密码密文，按 APP 的请求头和 JSON 体 POST 登录接口 |
| `02_尿大夫sign登录.py` | 复算 MD5 截取拼接 sign，表单 POST 登录接口 |
| `03_合伙人XSign登录.py` | 复算密码 MD5 与 X-Sign，带自定义头表单 POST 登录接口 |
| `04_算法自检.py` | 7 组样本离线复算，与 Frida hook 输出逐字节比对，不联网 |
| `common.py` | MD5、Luhn IMEI、AES/CBC/PKCS7+Base64、毫秒时间戳、低频重试 POST |
| `frida_hook/day05_hooks.py` | 三款 APP 的 Frida hook 脚本，attach 中文进程名，同时打印 OkHttp 请求与响应 |
| `capture/` | 三个 APP 的实时 hook 输出（爱安丘为首次登录的控制台转录，见文件头说明） |
| `results/` | 本次环境自检、算法自检、三个接口的真实响应记录（UTF-8 无 BOM） |

## 三个案例的还原过程

### 1. 爱安丘 1.0.5：AES/CBC/PKCS7 + Base64

jadx 打开 `爱安丘-1.0.5.apk`，从登录 URL `https://app-auth.iqilu.com/member/login?e=1` 和请求字段 `password` 回溯到 `com.iqilu.core.util.EncryptUtil`：

```text
EncryptUtil.aesPassword(明文)
  = Base64(AES/CBC/PKCS7Padding)
key = EncryptUtil.getMD5(PRIVATE_KEY + getSecret() + orgid)
    的 32 位 hex 字符串按 UTF-8 字节使用（即 AES-256）
IV  = "0000000000000000"（16 个字符 '0'）
PRIVATE_KEY = "c058579161250b37"
getSecret() = R.string.secret_key + "APP" = "48dce77cf43eb6c3APP"
orgid = "137"
```

Frida hook `EncryptUtil.getMD5` 与 `EncryptUtil.aesPassword`，拿到运行时真值：

```text
getMD5("c058579161250b3748dce77cf43eb6c3APP137")
  = 6d6656a37cdb7977c10f6d83cab168e9
aesPassword("lqz123456") = 0FwYho4FQoTYvYu2eioWDw==
```

请求头关键项：`encrypt: 1`、`version: 1.0.5`、`orgid: 137`、`platform: android`、随机 15 位 `imei`、`CQ-AGENT` JSON；请求体：

```json
{"codeKey":"","password":"0FwYho4FQoTYvYu2eioWDw==","code":"","phone":"18953675222","key":""}
```

服务端返回 HTTP 200：

```json
{"code":0,"errmsg":"用户或者密码错误  登录失败 账号或密码错误","errorCode":50009}
```

返回 50009 而不是解密/签名错误，说明 key、IV、PKCS7 填充、Base64 全部正确，请求已经进入账号校验阶段。课件里的测试账号在此版本已不可用，所以没有拿到 token。

注意两个细节：

- `secret_key` 是 16 位 `48dce77cf43eb6c3`，拼接后原文是 `c058579161250b37` + `48dce77cf43eb6c3` + `APP` + `137`。第一次漏了开头的 `48`，复算出的 key 对不上，靠 hook 输入串才定位到。
- Java 端是 `md5(...).getBytes()`，把 32 位 hex 字符串本身当密钥，属于 AES-256；不是把 hex 解码成 16 字节。

APP 一次点击会内置重试 8 次相同请求。连续测试后触发滑块验证码 `https://app-captcha.litenews.cn/server/slide?e=1`，继续请求返回：

```json
{"code":5,"errmsg":"  验证码获取次数过多，请稍后重试","errorCode":50000}
```

因此停止重复请求，以 18:52 首次 hook 的完整请求和 19:07 脚本重放的 50009 作为验证依据。

### 2. 尿大夫 4.1.11：MD5 截取拼接 sign

jadx 从登录 URL `https://api.niaodaifu.cn/v4/site/loginnew` 和字段 `sign` 回溯到 `com.uulife.medical.utils.SafeUtils.getSign(long)`：

```text
sign = md5("niaodaifu" + 秒时间戳)[12:30]
     + md5("android"   + 秒时间戳)[12:26]
```

请求是表单，密码明文，真正的门槛是 sign；`devisetoken` 只是设备标识，可以随机生成。hook `SafeUtils.getSign` 得到两组样本：

```text
getSign(1792405472) = acf37901198f906cefab3e4001d0b92a
getSign(1792408334) = 2d61ee52da5d9bf900df35c761994f73
```

重放响应 HTTP 200：

```json
{"status":1,"data":[],"message":"用户名或者密码错误"}
```

服务端没有返回“签名错误”，说明 sign 算法与时间戳单位（秒）正确。

### 3. 合伙人 1.4：密码 MD5 + X-Sign

jadx 定位到两处：

```text
LoginPresenter.submitLogin -> setPwd(Md5.md5(明文密码))
RequestParamsWrapper.sign(body)
  = md5(token + X-Req-Time + X-Noncestr[2:] + body).toLowerCase()
```

其中 `X-Noncestr` 固定 `123456`，签名只取后四位 `3456`；登录接口的 `X-Token` 为空串；`body` 必须与 FormBody 的字段顺序一致，即 `phone=...&password=...`。hook `Md5.md5` 和 `RequestParamsWrapper.sign` 得到：

```text
md5("123456") = e10adc3949ba59abbe56e057f20f883e
X-Req-Time = 1792408299226
X-Sign     = e06815789f099bcfefbe2a68b942555b
```

重放响应 HTTP 200：

```json
{"msg":"用户没有注册"}
```

同样不是签名错误，说明密码 MD5、签名原文拼接顺序、请求头都正确。

## 实测结果（2026-10-19）

| # | 环节 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 三款课件 APK 安装 | 成功 | 版本分别为 1.0.5 / 4.1.11.230417 / 1.4，未升级 |
| 2 | 断网绕过强制更新 | 成功 | 关 wifi + 数据 → force-stop → 启动 → 进登录页 → 恢复网络 |
| 3 | jadx 反编译 | 成功 | 三个 APK 均能检索到登录 URL、字段与算法类 |
| 4 | Frida hook | 成功 | 爱安丘 getMD5/aesPassword、尿大夫 getSign、合伙人 Md5/sign 均取到运行时值 |
| 5 | 算法本地复算 | 7/7 PASS | `results/算法自检结果.txt` |
| 6 | 爱安丘真实接口 | HTTP 200，50009 | `results/接口响应_爱安丘.txt` |
| 7 | 尿大夫真实接口 | HTTP 200，用户名或密码错误 | `results/接口响应_尿大夫.txt` |
| 8 | 合伙人真实接口 | HTTP 200，用户没有注册 | `results/接口响应_合伙人.txt` |
| 9 | 登录成功拿 token | 未完成 | 课件测试账号失效或未注册，属账号问题，不是算法问题 |
| 10 | 风控观察 | 已触发 | 爱安丘重复登录后出现滑块验证码与 50000 次数限制 |

第 9 项如实说明：本次验证的目标是“加密/签名是否被服务端接受”，三个接口都返回了业务层的账号错误，而不是解密失败、签名错误、参数错误，算法还原已经得到服务端验证。课件中的手机号在当前版本已不可用，没有为了凑“登录成功”去注册新账号或使用他人账号。

## 实操代码具体做了什么

**1. 公共层（`common.py`）**

- `md5()`：统一 32 位小写，等价 Java 的 `Md5.md5()`。
- `generate_imei()`：按 Luhn 规则生成 15 位 IMEI，服务端只当设备标识。
- `aes_cbc_pkcs7_base64()`：AES/CBC/PKCS7，key 用 hex 字符串字节，IV 为 16 个 `'0'`，输出 Base64。
- `post()`：单线程、失败间隔 3 秒、最多 3 次，避免高频请求。

**2. 环境层（`00_环境自检.py`）**

不依赖 `ps | grep frida`（该进程在部分系统上不可见），直接用 `frida.get_remote_device().enumerate_processes()` 判断 frida-server 是否可用；同时校验 adb 设备、端口转发、jadx 路径与三款 APP 版本，防止误装成最新版。

**3. 注入层（`frida_hook/day05_hooks.py`）**

- `TARGETS` 用中文进程名而不是包名：`爱安丘`、`尿大夫`、`油联合伙人`。
- 按 jadx 结论挂点：`EncryptUtil.getMD5/aesPassword`、`SafeUtils.getSign(long)`、`Md5.md5`、`RequestParamsWrapper.sign`。
- 额外挂 `okhttp3.internal.http.RealInterceptorChain.proceed`，打印 URL、Headers、Body、Response；尿大夫不用 OkHttp，`ClassNotFound` 属正常。
- JS 侧统一用 `send()` 回传，Python 侧同时打印和写文件；`console.log` 不会进入 Python 回调。

**4. 复算层（`01/02/03`）**

三个脚本结构一致：本地算出关键值 → 打印中间量 → 组装与 APP 相同的请求头和请求体 → 低频 POST → 打印 HTTP 状态与响应。都支持 `--no-request`，只复算不联网。

**5. 自检层（`04_算法自检.py`）**

把 hook 到的输入输出固化成 7 条样本（爱安丘 2 条、尿大夫 2 条、合伙人 3 条），离线复算后逐条比对，任何一条不一致都会返回非 0。

## 运行方式

```bash
# 0. 手机连电脑，启动 frida-server，端口转发
adb forward tcp:27042 tcp:27042
adb forward tcp:27043 tcp:27043

# 1. 环境自检
python 00_环境自检.py

# 2. 离线算法自检（不联网）
python 04_算法自检.py

# 3. 只复算，不发请求
python 01_爱安丘AES登录.py --no-request
python 02_尿大夫sign登录.py --no-request
python 03_合伙人XSign登录.py --no-request

# 4. 真实接口（低频，单次）
python 01_爱安丘AES登录.py
python 02_尿大夫sign登录.py
python 03_合伙人XSign登录.py

# 5. Frida 实时 hook（APP 停在登录页后运行，点登录观察输出）
python frida_hook/day05_hooks.py --target aiqiu --out capture/爱安丘_hook输出.txt
python frida_hook/day05_hooks.py --target niaodaifu --out capture/尿大夫_hook输出.txt
python frida_hook/day05_hooks.py --target partner --out capture/合伙人_hook输出.txt
```

## 断网绕过强制更新

课件明确要求不要升级 APK。实际步骤：

```bash
adb shell svc wifi disable
adb shell svc data disable
adb shell am force-stop com.iqilu.app137
adb shell monkey -p com.iqilu.app137 1
# 等 APP 进入登录页
adb shell svc wifi enable
adb shell svc data enable
```

尿大夫、合伙人同理，只换包名。断网时 APP 的版本检查请求失败，会直接进入登录页；此时再恢复网络，后续登录请求正常发出。

## 踩坑记录

1. **`console.log` 不进 Python 回调**：Frida 的 `console.log` 由 frida-core 直接写到 stdout，`script.on("message")` 收不到，日志文件只有头部。改用 `send()` 后正常落盘。
2. **爱安丘 secret 漏了 `48`**：`getSecret()` 实际是 `48dce77cf43eb6c3APP`，第一次按 `dce77cf43eb6c3` 复算，key 从 `6d66...` 变成 `f77d...`。靠 hook 打印的 `getMD5` 输入串定位并修正。
3. **attach 要用中文进程名**：包名 `com.iqilu.app137` attach 会 `ProcessNotFoundError`，必须用 `爱安丘` / `尿大夫` / `油联合伙人`。
4. **尿大夫协议勾选框点不中**：`login_user_layout` 的实际 bounds 是 `[240,1661][313,1734]`，点 `(276,1697)` 才生效；点边缘 `(290,1660)` 无效。
5. **frida-server 用 `ps` 查不到**：`adb shell ps -A | grep frida` 为空，但 27042 在监听、`frida-ps -U` 正常。环境自检改为枚举进程判断。
6. **爱安丘风控**：一次点击重试 8 次，连续测试触发滑块验证码与“验证码获取次数过多”，后续只能用首次 hook 的 50009 作为依据，不能反复刷接口。
7. **PowerShell 重定向编码**：直接 `>` 会写成 UTF-16，`results/` 统一用 `UTF8Encoding($false)` 写无 BOM 文件；Python 侧设置 `PYTHONIOENCODING=utf-8`。
8. **`*.log` 被仓库忽略**：验证结果统一保存为 `.txt`，否则提交不进 Git。

## 合规说明

- 全部脚本仅限学习研究，禁止商用；脚本头部均带声明。
- 只使用课件里的占位手机号（18953675221 / 18953675222），未使用任何真实用户账号、验证码或 token。
- 请求低频、单线程、失败重试间隔 3 秒；爱安丘触发风控后立即停止重复请求。
- 三个接口返回的都是账号/注册类错误，未获取任何用户数据或登录凭证。
