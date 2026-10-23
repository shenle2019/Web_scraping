# 得物 newSign 双层签名 + X-Auth-Token 游客 Token 复刻

> 仅限学习研究，禁止商用。本文所有请求只打本机 127.0.0.1:8000 的自建服务端；
> 真实得物 4.74.5 只做安装、断网启动观察和 Frida 只读 Hook，不做批量抓取、不做接口重放。

## 一、结论先说

| 项目 | 结果 |
| --- | --- |
| 本地服务端（版本检查 / newSign 校验 / 游客 Token / 推荐流） | 跑通 |
| 自建 App（模拟得物 4.74.5 的签名与 Token 链路） | 编译、装机、真机跑通 |
| Python 独立复刻 newSign | 与 App、服务端三方一致 |
| Frida Hook 自建 App（Java 签名 + native AES + 更新弹窗） | 跑通，密文 MD5 与 newSign 完全一致 |
| 代理对照（系统代理 vs Proxy.NO_PROXY） | 跑通，行为与课件一致 |
| SocksDroid 旁路 | 跑通，VPN 层能抓到绕过系统代理的请求 |
| 真实得物 4.74.5 安装 | 成功（versionName=4.74.5） |
| 真实得物 强制更新弹窗 / 断网启动绕过 | 均复现成功 |
| 真实得物 Frida Hook（RequestUtils.c + AESEncrypt + native + MD5） | 跑通，抓到明文、key、密文、newSign |

**没做的部分**：没有逆 `libJNIEncrypt.so` 的汇编实现（只确认了动态注册和导出函数的行为）、
没有对真实得物做接口重放或批量请求、没有脱壳。真实 App 上的 Hook 只用于观察它自己发出的请求参数。

## 二、newSign 到底是什么

课件结论，本次在自建 App 与真实得物上各验证了一遍：

```
参与字段：业务参数 + loginToken + platform + timestamp + uuid + v
排序：按 key 字典序（TreeMap / Collections.sort）
拼接：key + value 直接拼，没有任何分隔符
加密：AES-128-ECB / PKCS5Padding，key = d245a0ba8d678a61
编码：标准 Base64，不带换行
签名：MD5(Base64 字符串) -> newSign
```

真实得物 4.74.5 抓到的两条实例（Frida 只读输出）：

```
明文 = loginTokenpagetabplatformandroidtabId4timestamp1792745467858uuid6cfa0563bedd8748v4.74.5
key  = d245a0ba8d678a61
密文 = C+durZzmfI4wFUM+PtFLCcLeWeJ5HrPLlSt/xw/uN35TnIwgxfzH9EclkYR/TztMSD4fAHqbPlBnU0nwoTWHXEaNsBW7sRvv+3AXntq66ZyTAw55onwRa1Ma1U4AGlqt
MD5  = 778ccfa3d573a85e95b2dc7513602654   <- 就是这次请求的 newSign
```

`md5(密文)` 当场用 Python 复算，结果一致，说明链路判断没有偏差。

请求里还有 `abTest` 这种 JSON 值直接参与拼接的情况：

```
abTest{"name":"Commodity_subject","value":"2"},{"name":"Commodity_chuanda","value":"1"},{"name":"","value":""}lastIdlimit20...
```

所以拼接阶段不能对 value 做 URL 编码或二次转义，App 里是什么字符串就拼什么。

## 三、X-Auth-Token 是 JWT

```
header.payload.signature  三段 Base64Url
payload = {"iat":..., "exp":..., "iss":"<uuid>", "sub":"<uuid>",
           "uuid":"<uuid>", "userId":..., "isGuest":true}
```

游客 token 由 `POST /api/v1/app/user_core/users/getVisitorUserId` 的**响应头**返回，
这个请求自身也要带 newSign。拿到 token 后，feed 接口只校验 `X-Auth-Token`，
newSign 可带可不带（课件结论，本次服务端也按这个规则实现并验证）。

## 四、自建 App 做了什么

包名 `com.repl.dewu`，versionName 4.74.5，只跑 arm64-v8a。

| 文件 | 作用 |
| --- | --- |
| `MainActivity.java` | 启动查版本；三个按钮：取 Token / 拉 feed / 代理对照 ping |
| `update/UpdateChecker.java` | `GET /app/version`，`force=true` 就弹窗 |
| `update/UpdateDialog.java` | 不可取消的强制更新弹窗（对应课件的更新拦截点） |
| `security/AESEncrypt.java` | 复刻 `getByteValues()` 干扰串 + `encodeByte` native 调用 |
| `util/SignUtils.java` | 排序拼接 + `AESEncrypt.encode` + MD5 |
| `net/NetClient.java` | `API_CLIENT` 显式 `Proxy.NO_PROXY`，`PLAIN_CLIENT` 跟随系统代理 |
| `jni/aes_jni.c` | `JNI_OnLoad` 动态注册；固定 key；导出 `AES_128_ECB_PKCS5Padding_Encrypt` 方便 Hook |

关键点：Java 层故意保留课件的“障眼法”——`getByteValues()` 返回 0101 串并逐位取反传给
`encodeByte`，但 so 里根本不用第二个参数，真正的 key 是 `d245a0ba8d678a61`。
这样 Frida 在 Java 层看到的参数和 native 层真正用的 key 会对不上，正好复刻课件的坑。

编译：

```bat
build_so.bat     :: aarch64-linux-android24-clang -shared -fPIC -O2
build_apk.bat    :: gradle --offline assembleDebug
adb install -r android\app\build\outputs\apk\debug\app-debug.apk
```

## 五、真机 12 项验证

| # | 验证项 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 联网启动弹强制更新 | 通过 | 01_update_dialog.png |
| 2 | 断网启动不弹更新 | 通过 | 02_offline_start.png |
| 3 | 真机取游客 Token（newSign 校验通过） | 通过 | 03_token_ok.png + server.log |
| 4 | JWT payload 含 isGuest=true | 通过 | 03_token_ok.png |
| 5 | 带 token 拉 feed 200 / 20 条 | 通过 | 04_feed_ok.png |
| 6 | 错误 newSign 返回 456 | 通过 | repl_case.py 输出 |
| 7 | 无 token 拉 feed 返回 401 | 通过 | repl_case.py 输出 |
| 8 | Frida 跳过更新弹窗 | 通过 | 05_frida_bypass.png + frida_hook.log |
| 9 | Frida Hook Java 签名 + native AES | 通过 | frida_hook.log |
| 10 | 系统代理只抓到 PLAIN_CLIENT | 通过 | 06_proxy_compare.png + proxy.log |
| 11 | SocksDroid 抓到 NO_PROXY 请求 | 通过 | 07_socksdroid.png + socks5.log |
| 12 | 真实得物断网启动 + Hook 全链路 | 通过 | 09 / 10 / 12 + dewu_aes2.log |

## 六、代理对照怎么做的

1. PC 起一个极简 HTTP 代理 `scripts/proxy_logger.py`（8899），只打印目标地址；
2. 手机设置系统代理 `192.168.31.220:8899`；
3. App 点“代理对照 ping”（`PLAIN_CLIENT`）：代理日志出现
   `GET http://192.168.31.220:8000/app/ping <- 192.168.31.44`，服务端看到的来源是
   `192.168.31.220`（PC 的 IP）；
4. App 点“获取 Token”（`API_CLIENT` + `Proxy.NO_PROXY`）：代理日志里没有这条请求，
   服务端看到的是 `192.168.31.44`（手机真实 IP）。

结论：App 一旦写了 `Proxy.NO_PROXY`，系统代理就抓不到它，必须换 VPN 层。

## 七、SocksDroid 旁路

- PC 起 `scripts/socks5_logger.py`（1080）；
- 手机 SocksDroid 填 `192.168.31.220:1080`，开 VPN（`tun0 26.26.26.1/24`）；
- 用同样的按钮再走一遍，`socks5.log` 出现
  `CONNECT 192.168.31.220:8000 <- 192.168.31.44`，服务端来源变成 `192.168.31.220`。

这就是课件里“App 禁代理 → 用 SocksDroid 旁路”的完整复现。
注意课件强调的顺序：**先删系统代理，再开 SocksDroid**，两个一起开容易互相打架。

## 八、真实得物 4.74.5 这一段

安装课件自带的老版本（不升级）：

```
adb install -r "软件\得物-4.74.5.apk"
adb shell dumpsys package com.shizhuang.duapp | grep versionName   # 4.74.5
```

启动 Activity 不是 `.MainActivity`，而是 `com.shizhuang.duapp/.modules.home.ui.SplashActivity`，
用 `monkey -p com.shizhuang.duapp -c android.intent.category.LAUNCHER 1` 最省事。

1. **联网启动**：先弹隐私声明，同意后进首页，同时弹出“强制更新”弹窗（截图 09），
   背景里的首页照常渲染，但弹窗挡住操作；
2. **断网启动**：`svc wifi disable` → force-stop → 启动 → 进首页（截图 10），
   不弹更新；再开网，页面正常刷新。这就是课件说的绕过方式，不需要改包；
3. **Frida**：进程名是 `得物(毒)`，不是包名；attach 后用
   `Java.enumerateLoadedClassesSync()` 能直接找到
   `com.shizhuang.duapp.common.utils.RequestUtils` 和
   `...net.interceptor.WebRequestInterceptor`，方法签名与课件一致：

```
public static synchronized java.lang.String RequestUtils.c(java.util.Map, long)
```

Hook `c(Map, long)` 能打印出业务参数（`productId`、`limit`、`showType`、`spuId`、`roomId` 等），
Hook `AESEncrypt.encode` / native 导出函数 / `RequestUtils.a(String)` 能拿到完整三段：

```
明文 -> AES-128-ECB(key=d245a0ba8d678a61) -> Base64 -> MD5 -> newSign
```

真实 App 里还观察到 `userId=2962793549` 参与消息通道的签名，说明登录态下参与字段会更多，
这一点课件没有展开，本次只记录现象，没有继续深挖。

## 九、踩坑表

| # | 坑 | 现象 | 处理 |
| --- | --- | --- | --- |
| 1 | PowerShell `$pid` 是只读内置变量 | 赋值失败，frida 附加到 PowerShell 自己 | 改用 `$appPid` |
| 2 | `libJNIEncrypt.so` 首次签名才 dlopen | 注入时 `findExportByName` 返回 null | 300ms 轮询等 so 加载 |
| 3 | 直接打印 Map | 只得到 `[object Object]` | `keySet().toArray()` 逐个 get |
| 4 | cast 成 HashMap 后 `entrySet().iterator()` | `TypeError: not a function` | 同上，改用 keySet |
| 5 | 先 attach 再浏览 | 页面有缓存，签名不触发 | `frida -f` spawn，让 Hook 先于请求 |
| 6 | 真实得物进程名 | `-n com.shizhuang.duapp` 找不到进程 | `frida-ps -U` 看到是 `得物(毒)`，用 PID attach |
| 7 | 启动 Activity | `.MainActivity` 不存在 | 用 monkey 走 LAUNCHER |
| 8 | 断网启动前没 force-stop | 旧进程还在，弹窗照旧 | 先 `am force-stop` 再启动 |
| 9 | 系统代理没清 | SocksDroid 与代理冲突 | `settings put global http_proxy :0` |
| 10 | 首次启动隐私弹窗 | 不点同意进不去 | 点 `agree_tv` |
| 11 | 得物强制更新弹窗是自定义 View | uiautomator dump 拿不到文字 | 以截图为准 |
| 12 | `adb exec-out screencap -p > x.png` | PowerShell 按文本重定向，PNG 损坏 | `adb shell screencap -p /sdcard/x.png` + `adb pull` |
| 13 | gradle 提示 `Unable to strip libJNIEncrypt.so` | 不是错误 | 打包未 strip 的 so，正常 |
| 14 | 服务端日志里的来源 IP | 分不清是谁 | `192.168.31.44`=手机直连，`192.168.31.220`=经过 PC 代理 |

## 十、目录说明

```
server/app.py                 本地仿真服务端（Flask）
run_server.bat                启动服务端
build_so.bat                  编译 libJNIEncrypt.so
build_apk.bat                 编译 APK
android/                      自建 App 源码（不含 so、不含 build 产物）
frida/hook_sign_all.js        自建 App：更新弹窗 + Java 签名 + native AES
frida/find_requestutils.js    真实得物：枚举类与方法
frida/hook_dewu_realsign.js   真实得物：RequestUtils.c 参数与 newSign
frida/hook_dewu_aes.js        真实得物：明文 / key / 密文 / MD5 全链路
scripts/repl_case.py          Python 独立复刻 newSign 并做四项接口验证
scripts/proxy_logger.py       带日志的 HTTP 代理（8899）
scripts/socks5_logger.py      带日志的 SOCKS5（1080）
evidence/                     截图、服务端日志、代理日志、Frida 输出
验证记录.md                   逐项验证与日志摘录
```

## 十一、合规声明

- 只采集匿名公开数据，不绕登录墙、不碰付费内容、不做规模抓取；
- 真实得物只装老版本做启动与 Hook 观察，单次运行、无批量请求、无接口重放；
- 所有自建服务端数据均为本地 mock，不含任何真实商品或用户数据；
- 结果文件与 token 不入库（`repl_result.json` 已排除），本文只保留机制说明与必要证据。
