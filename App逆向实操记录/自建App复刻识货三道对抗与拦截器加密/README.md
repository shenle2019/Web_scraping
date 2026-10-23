# 自建 App 复刻识货：强制更新 / Frida 反调试 / 拦截器加密 / 代理旁路

课件目录：`E:\路飞学城\课件\APP逆向(12期)\day15-识货app`

这篇记录做的是"把课件里的对抗点，自己写一个 App 复现一遍，再用 Frida 逐个打掉"，不是对真实识货做接口逆向。所有请求都发往本机 `192.168.31.220:8000` 的自建 Flask 服务。

仅限学习研究，禁止商用。

---

## 一、结论先说清楚

### 跑通的部分（自建 App，真机 Pixel 2 / Android 11 / arm64）

| 对抗点 | 实现 | 绕过方式 | 结果 |
| --- | --- | --- | --- |
| 强制更新弹窗 | `UpdateDialog.show()` 不可取消 | Hook 掉 `show()`，不弹窗 | 通过，截图 01 / 05 |
| Frida 反调试 | `libfridadetector.so` 扫 `/proc/self/maps` 和线程名 | spawn 被秒杀 → 删 so → 存活 | 通过，截图 06 |
| 拦截器加密 | `EncryptInterceptor` 把 `goods_id` 换成 `data=AES/ECB/Base64` | Hook `intercept()` 直接 `proceed()` | 通过，服务端收到明文，第 4 次触发 428 |
| 代理检测 | `Proxy.NO_PROXY` 直连 + 系统代理对照 | SocksDroid 在 VPN 层旁路 | 通过，`socks5.log` 有 CONNECT，服务端看到的来源 IP 变成 PC |
| 接口混用 | 老搜索免头拿 `goods_id`，新详情免头拿明文 | Python 复刻 | 通过，`goods_id=379112` |

### 真实识货 7.20.1（只做观察，未做接口逆向）

- 安装的是课件里的 7.20.1（versionCode 15670），没有升级。
- `libmsaoaidsec.so` 在，Frida spawn 即闪退；删掉后 App 能起，进入首页。
- 真实更新弹窗类不是课件的 `com.azhon.appupdate.dialog.UpdateDialog`，而是
  `com.shizhi.shihuoapp.component.dialogqueue.dialog.UpdateDialog`。
- 拦 `show()` 或 `show()` 后 800ms `dismiss()`，约 14 秒后进程都被结束；空脚本能活 40 秒。判断是版本校验/看门狗，不是反调试。
- 这一层没有继续深挖（用户确认不深挖），如实记录在案。

### 没做的部分（避免误解）

- 没有逆真实识货的 `sh-sign` / `sh-token` 算法。课件里也是固定值演示，本项目的 `sh-sign` 是自己服务端的等价校验。
- 没有脱真实 App 的壳，也没有对识货生产接口发过请求。
- AES key `shihuo-repl-key!`、接口路径、字段结构都是按课件思路在本地复刻的，不是从 APK 里抠出来的。

---

## 二、链路

```
┌─────────────────────────────┐        ┌──────────────────────────┐
│ com.repl.shihuo (自建 App)   │        │ Flask 192.168.31.220:8000 │
│  GuardApp → FridaGuard      │        │  /app/version             │
│  MainActivity → UpdateDialog│───────▶│  /daga/search/goods/v1    │
│  OkHttp + EncryptInterceptor│        │  /v3/sh-api/...（457）     │
└──────────┬──────────────────┘        │  /v4/.../public/detail    │
           │ Proxy.NO_PROXY             │  /v4/.../preload/single   │
           ▼                            │  /app/ping  /app/reset    │
   系统代理 8899（对照）                 └──────────────────────────┘
   SocksDroid VPN → SOCKS5 1080 ───────────────┘
```

- 系统代理：`proxy_logger.py`（8899，HTTP 正向代理，带日志）
- VPN 旁路：`socks5_logger.py`（1080，无认证 SOCKS5，带日志）

---

## 三、目录

```
自建App复刻识货三道对抗与拦截器加密/
├─ README.md                 本文
├─ 验证记录.md                逐项验证结果与日志摘录
├─ server/
│  ├─ app.py                 Flask 服务端（版本/搜索/详情/验证码/AES）
│  └─ run_server.bat         后台启动脚本
├─ android/
│  ├─ build.gradle / settings.gradle / gradle.properties
│  └─ app/
│     ├─ build.gradle
│     └─ src/main/
│        ├─ AndroidManifest.xml
│        ├─ java/com/repl/shihuo/
│        │  ├─ GuardApp.java             启动即做 Frida 检测
│        │  ├─ MainActivity.java         6 个按钮 + 日志区
│        │  ├─ net/Api.java              新老头、UA、接口
│        │  ├─ net/NetClient.java        NO_PROXY / 默认代理两套 client
│        │  ├─ net/EncryptInterceptor.java
│        │  ├─ security/FridaGuard.java  JNI 声明 + 结果日志
│        │  ├─ update/UpdateChecker.java
│        │  ├─ update/UpdateDialog.java  不可取消弹窗
│        │  └─ util/Crypto.java          AES/ECB/PKCS5 + Base64
│        ├─ jni/frida_guard.c            扫描 maps 与线程名
│        └─ res/layout/activity_main.xml
├─ frida/
│  ├─ driver.py              spawn/attach 驻留驱动（解决 CLI 退出问题）
│  ├─ 00_noop.js             空脚本，观察存活
│  ├─ 01_trace_dlopen.js     打印 so 加载顺序
│  ├─ 02_kill_update_dialog.js  拦自建 App 的更新弹窗
│  ├─ 03_list_interceptors.js   打印 OkHttp 拦截器类名
│  ├─ 04_skip_interceptor.js    跳过加密拦截器
│  ├─ 05_shihuo_update_dialog.js   真实识货：拦 show
│  ├─ 06_shihuo_dialog_show_then_dismiss.js  真实识货：先 show 再 dismiss
│  ├─ set_socks_ip.js        用 Frida 给 SocksDroid 填 IP
│  ├─ remove_guard_so.sh     删自建 App 的检测 so
│  └─ remove_shihuo_guard_so.sh  删识货的 libmsaoaidsec.so
├─ scripts/
│  ├─ repl_case.py           Python 端：老搜索 + 新详情 + 密文解密
│  ├─ proxy_logger.py        8899 HTTP 代理（带日志）
│  ├─ socks5_logger.py       1080 SOCKS5（带日志）
│  └─ socks5_debug.py        1080 调试版（逐步打印握手）
└─ evidence/                 截图与日志
```

构建产物（`build/`、`.gradle/`、`local.properties`、`*.apk`、`*.so`、OkHttp/Okio 的 jar）没有入库，按下面的步骤本地生成。

---

## 四、怎么跑

### 0. 依赖

- JDK 17（本机 `D:\Android\jbr`）、Gradle 8.0 + AGP 8.0.2
- SDK 33、build-tools 30.0.3、NDK r26d
- 手机：Pixel 2 / Android 11 / arm64-v8a，已 root，frida-server 16.3.3
- PC：Python 3 + `flask` `pycryptodome` `requests` `frida`

OkHttp / Okio 的 jar 需要自己放（项目里没提交二进制）：

```
curl -o android/app/libs/okhttp-3.14.9.jar https://repo1.maven.org/maven2/com/squareup/okhttp3/okhttp/3.14.9/okhttp-3.14.9.jar
curl -o android/app/libs/okio-1.17.2.jar  https://repo1.maven.org/maven2/com/squareup/okio/okio/1.17.2/okio-1.17.2.jar
```

再写 `android/local.properties`：`sdk.dir=C:/Users/<you>/AppData/Local/Android/Sdk`。

### 1. 服务端

```
python server/app.py
```

默认 `0.0.0.0:8000`。App 的 `BASE_URL` 在 `android/app/build.gradle` 里，改成本机局域网 IP。

### 2. 编译检测 so

```
build_so.bat
```

调用 NDK 的 `aarch64-linux-android24-clang.cmd` 编译 `jni/frida_guard.c`，输出到 `app/src/main/jniLibs/arm64-v8a/libfridadetector.so`。

### 3. 编译安装

```
gradle assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

项目没带 wrapper，用本机 Gradle 8.0；要 wrapper 就自己 `gradle wrapper` 生成。

注意：`AndroidManifest` 里必须 `android:extractNativeLibs="true"`，`build.gradle` 里必须
`packaging { jniLibs { useLegacyPackaging true } }`。否则 AGP 8 会把 so 留在 APK 里
（`base.apk!/lib/...`），后面"删 so"没法做。

### 4. Frida

手机端：

```
adb shell su -c "/data/local/tmp/frida-server &"
```

PC 端：

```
python frida/driver.py spawn frida/02_kill_update_dialog.js 30 com.repl.shihuo
python frida/driver.py spawn frida/01_trace_dlopen.js 15 com.repl.shihuo
python frida/driver.py attach frida/03_list_interceptors.js 15 识货复刻
```

`driver.py` 是为了解决 frida CLI 在非交互终端里 spawn 后立刻退出、脚本随之卸载的问题。

### 5. 删 so（绕过反调试）

```
adb push frida/remove_guard_so.sh /data/local/tmp/
adb shell su -c "sh /data/local/tmp/remove_guard_so.sh"
```

脚本会 `pm path` 找安装目录，删掉 `lib/arm64-v8a/libfridadetector.so`，再启动就是
`UnsatisfiedLinkError` → 被 `FridaGuard` catch → 打印"检测库不存在，反调试检测跳过"。

### 6. 代理与旁路

```
python scripts/proxy_logger.py     # 8899
python scripts/socks5_logger.py    # 1080
adb shell settings put global http_proxy 192.168.31.220:8899   # 对照请求用
```

SocksDroid 配 `192.168.31.220:1080`，开 VPN 后，App 即使写 `Proxy.NO_PROXY`，TCP 也会被
VPN 抓进 tun0，再由 SocksDroid 转给 PC 的 1080。

### 7. Python 端复刻

```
python scripts/repl_case.py 篮球
```

输出：老搜索的 `goods_id` → 新搜索无头 457 → 新详情明文 → 老详情密文进密出并解密。
结果写 `repl_result.json`（结果数据不入库）。

---

## 五、关键代码做了什么

### 1. 更新弹窗

`UpdateChecker` 请求 `/app/version`（`force=true, latest=7.73.0`），`MainActivity` 拿到
`latest` 后直接 `UpdateDialog.show(this, latest)`；`UpdateDialog` 里 `setCancelable(false)`，
唯一按钮是"立即更新"，点完就 `finish()`。所以正常用户只有"去更新"一条路。

绕过就是 Hook 唯一入口：

```js
var UpdateDialog = Java.use("com.repl.shihuo.update.UpdateDialog");
UpdateDialog.show.implementation = function (activity, latest) {
    console.log("[hook] UpdateDialog.show(" + latest + ") 被拦截，未弹窗");
};
```

### 2. 反调试 so

`GuardApp.onCreate` 先 `FridaGuard.check()`，再 `setContentView`。so 里两个扫描：

- `/proc/self/maps` 找 `frida`、`gum-js-loop`、`linjector`、`gadget`
- `/proc/self/task/*/comm` 找线程名

命中就 `exit(0)`。日志里能看到 `dlopen` 最后加载 `libfridadetector.so`，紧接着
`detached: process-terminated`。

绕过不是"改返回值"，而是把 so 从安装目录删掉：`System.loadLibrary` 抛
`UnsatisfiedLinkError`，Java 层 catch 住后继续走。这也解释了为什么必须
`extractNativeLibs=true`。

### 3. 拦截器加密

`EncryptInterceptor` 只处理 `/app_swoole_shoe/preload/single`：

- 请求里有 `goods_id` → 换成 `data=Base64(AES/ECB/PKCS5({"goods_id":"..."}))`
- 响应里 `data` 是字符串 → 解密后再交给业务

定位靠 Hook `okhttp3.OkHttpClient$Builder.addInterceptor`，打印
`interceptor.$className`（用 `getClass()` 会报 `not a function`）。跳过就是：

```js
Enc.intercept.implementation = function (chain) {
    return chain.proceed(chain.request());
};
```

跳过之后服务端收到的是明文 `goods_id`，第 4 次开始返回 428 图片验证码（本地固定 8888）。

### 4. 代理检测

`NetClient` 里两个 client：

- `API_CLIENT`：`.proxy(Proxy.NO_PROXY)`
- `PLAIN_CLIENT`：默认，走系统代理

"对照请求"按钮走 `PLAIN_CLIENT`，`proxy.log` 能看到
`[proxy] GET http://192.168.31.220:8000/app/ping <- 192.168.31.44`，
服务端日志 `ip=192.168.31.220`（代理的出口）。
"搜索(老接口)"走 `API_CLIENT`，系统代理看不到，服务端 `ip=192.168.31.44`，证明 NO_PROXY 生效。

SocksDroid 开起来之后，再点同一个按钮：

```
[socks] CONNECT 192.168.31.220:8000 <- 192.168.31.44
```

服务端记录 `ip=192.168.31.220`，说明请求是从 PC 的 SOCKS5 转发出去的，
NO_PROXY 在 socket 层被绕开。

### 5. 服务端

- `/app/version`：固定返回 `force=true, latest=7.73.0`
- `/daga/search/goods/v1`：老搜索，不看头，返回两条商品
- `/v3/sh-api/daga/search/goods/v1`：缺 `sh-sign`/`sh-token` 返回 457
- `/v4/services/sh-goodsapi/public/detail`：新详情，明文免头
- `/v4/services/sh-goodsapi/app_swoole_shoe/preload/single`：
  - `data` 分支：AES 解密 → 加密返回（密文进密文出）
  - `goods_id` 分支：明文，第 4 次起 428，`captcha=8888` 放行
- `/app/ping`：代理对照
- `/app/reset`：重置计数

AES 参数：`AES/ECB/PKCS5Padding`，key `shihuo-repl-key!`（16 字节），密文 Base64。

---

## 六、真实识货 7.20.1 实测

1. 装 `识货7.20.1.apk`（课件 `软件/` 目录），`versionCode=15670`，没有装 7.53.0/7.73.0。
2. 首次启动有隐私弹窗、性别选择，同意后进首页。
3. `lib/arm64-v8a/` 下有 `libmsaoaidsec.so`，另有 `libsg*`、`libsh_security`、
   `libKwAppGuardSDK`、`libEncryptorP.so` 等一堆安全库。
4. Frida spawn：加载 `libmsaoaidsec.so` 后进程结束（复现课件的闪退）。
5. `remove_shihuo_guard_so.sh` 删掉这个 so，再 spawn：进程存活，进入首页，出现真实更新弹窗
   "版本太旧了 / 你的版本需要升级啦 / 立即更新"。
6. Hook `android.app.Dialog.show` 打印类名，确认真实弹窗类：
   `com.shizhi.shihuoapp.component.dialogqueue.dialog.UpdateDialog`。
7. 直接不调用 `show()`，约 14 秒进程被结束；先 `show()` 再 800ms `dismiss()`，同样被杀；
   空脚本 `00_noop.js` 能活 40 秒。判断是版本校验/看门狗，不是 Frida 检测。
8. 到这一步停住，没有继续改版本校验。

---

## 七、踩坑清单（都真实踩过）

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 装完 APK，`lib/` 下没有 so | AGP 8 默认不提取 native lib | `extractNativeLibs=true` + `useLegacyPackaging true` |
| Gradle 报路径含非 ASCII | 项目在中文目录 | `android.overridePathCheck=true` |
| `frida -U -f ...` spawn 后脚本立刻卸载 | CLI 在非交互终端退出 | 用 `frida` Python API 自己管生命周期（`driver.py`） |
| `--no-pause` 不认 | frida 16.3.3 移除了该参数 | 去掉，改用 `device.resume(pid)` |
| attach 包名找不到进程 | 新版 frida 枚举的是 label | 依次试包名/label（`识货复刻`、`SocksDroid`） |
| `interceptor.getClass is not a function` | Frida 的 Java 包装 | 改用 `interceptor.$className` |
| SocksDroid 改了 prefs，启动又变回 127.0.0.1 | App 启动时重置默认值 | 只能走 UI；用 Frida 对弹窗 `EditText` 调 `setText` |
| `adb input text` 的 `.` 变成 `。` | 中文输入法（Gboard 拼音） | 换 IME 也无效；ADBKeyboard 的 `exported=false` 装不上；最后用 Frida setText |
| SOCKS5 握手卡死，App 全超时 | 解析请求漏读 RSV 字节 | 补 `read_exact(conn, 1)`，见 `socks5_logger.py` |
| `su -c` 卡住，后续 su 全阻塞 | adb 会话卡死 | `Stop-Process adb` + `adb start-server` |
| PowerShell 不认 `&&`、`cmd /c` 被工具拦 | 环境限制 | 全部改 `;`，编译写 `.bat` 再执行 |

---

## 八、合规

- 只访问本机 `192.168.31.220:8000` 的自建服务，低频调用。
- 真实识货只做了：安装课件提供的 7.20.1、启动、观察 so、删本地 so、观察弹窗；没有请求它的生产接口。
- 本目录不含 cookies、token、账号信息；`repl_result.json` 等结果数据没有入库。
- 仅限学习研究，禁止商用。
