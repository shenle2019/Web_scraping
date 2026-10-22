# 车智赢 3.56.0 登录三参数逆向复刻（真机验证）

> 仅限学习研究，禁止商用。本目录所有登录请求只发往本机自建的 Flask 服务端，没有向车智赢官方接口提交过任何账号。

## 一、这个案例要做什么

课件 day14 拆的是车智赢 Android 客户端的登录请求。一条 `POST /tradercloud/sealed/login/login.ashx` 的表单里，有三个不能直接看懂的字段：

| 字段 | 含义 |
| --- | --- |
| `pwd` | 密码的密文，不是明文 |
| `udid` | 设备指纹，不是明文设备号 |
| `_sign` | 全参数签名，改任何一个参数都会变 |

目标是：搞清楚这三个值各自怎么算，然后不依赖原 App、只用 Python 就能构造出一条能通过服务端校验的登录请求。

## 二、结论：三个参数怎么算

```
pwd   = md5(密码明文).toLowerCase()

udid  = Base64( 3DES-CBC/PKCS5Padding( 段1|段2|段3 ) )
        key = "appapiche168comappapiche168comap" 的前 24 字节
        iv  = "appapich"
        段1 = 设备唯一号（真实包里是 AHDeviceUtil.getDeviceId）
        段2 = System.nanoTime()，每次请求都不同
        段3 = 用户设备 ID（未登录时为空串，末尾也保留一个 |）

_sign = md5( 盐 + 按 key 升序拼的 k+v + 盐 ).toUpperCase()
        盐由 signByType(type) 选：0→KEY_V1  1→KEY_V2  2→KEY_SHARE  3→KEY_AUTOHOME
        登录接口走 type=1，即 KEY_V2
```

三个容易踩的点：

1. **盐不止一套**。`signByType` 按 `signType` 切四套盐，登录用 1 号。只抄到 0 号盐会一直对不上。
2. **拼接没有分隔符**。`TreeMap` 只负责给出稳定的 key 顺序，Python 侧等价于 `sorted()`；`k` 和 `v` 直接相连，`=`、`&` 都不能有。
3. **`nanoTime` 每次都不一样**。它进了 `udid`，而 `udid` 又进了签名原文，所以整条请求不能缓存复用，必须现场生成。

## 三、复刻链路：四层证据互相咬合

| 层 | 做法 | 落盘证据 |
| --- | --- | --- |
| 1. 静态 | 抽真实 apk 的 `libnative-lib.so` 与 `classes2.dex`，按字节找常量、符号、算法 | `evidence/real_apk_static_verify.txt` |
| 2. 抓包 | Charles 挂 8888，看真机请求里的三个字段长什么样 | `evidence/charles_capture.png` |
| 3. 动态 | 自建同构 App 装真机，Frida 挂链路每个方法，打印入参出参 | `evidence/frida_hook.txt`、`shot_frida_login_ok.png` |
| 4. 复算 | 纯 Python 重算三参数，直接打本地服务端 | `evidence/replay_result.json`、`server_request_log.txt` |

服务端不信任 App 传来的 `_sign`，而是自己按同样的规则重算一遍再比对；`udid` 也是自己 3DES 解出三段明文来验。这样"跑通"才有意义——是服务端认了这套算法，不是客户端自说自话。

### 为什么还要自己写一个 App

真实包只能证明"它这么发"，不能证明"这么算是充分的"。自己写一个同构 App 有两个好处：

- 可以把 key 换成自己的，验证"算法结构与 key 解耦"；
- 可以在里面保留课件的"错误候选"分支（`AHAPIHelper.toSign` 这个死代码），Hook 时一次都不触发，实证"搜到的第一个方法不一定是真正跑的那条路"。

## 四、目录结构

```
车智赢登录签名与3DES真机复刻验证/
├── README.md                     本文件
├── 验证记录.md                   按时间顺序的实测命令与输出
├── android/                      复刻 App 源码（AGP 8.0.2，无第三方依赖）
│   ├── settings.gradle / build.gradle / gradle.properties
│   └── app/
│       ├── build.gradle
│       └── src/main/
│           ├── AndroidManifest.xml
│           └── java/com/autohome/
│               ├── ahkit/AHAPIHelper.java           key 与死代码 toSign
│               ├── ahkit/jni/CheckSignUtil.java     key 常量 + checkState 缓存
│               ├── ahkit/utils/SecurityUtil.java    MD5 / 3DES
│               └── chezhiying/
│                   ├── AppUtils.java                getUDID 三段 + getIMEI 降级
│                   ├── LaunchModel.java             公共参数补齐 + 签名
│                   ├── SignManager.java             四套盐 + signByType
│                   ├── SPUtils.java
│                   └── LoginActivity.java           纯代码 UI + HttpURLConnection
├── server/chezhiying_server.py    Flask 校验服务（独立重算三参数）
├── scripts/
│   ├── 00_apk_static.py           真实 apk 只读静态核验
│   ├── 02_frida_hook.py           Hook 驱动（spawn + 点击登录）
│   ├── hook_sign.js               Hook 脚本
│   └── 10_replay_login.py         纯 Python 复算并请求本地服务端
└── evidence/
    ├── real_apk_static_verify.txt 静态核验报告
    ├── jadx_key_classes/         4 个关键类的 jadx 反编译归档（SignManager / SecurityUtil /
    │                             AHAPIHelper / LaunchModel），让 00_apk_static.py 离开本机也能跑
    ├── charles_capture.png        Charles 抓到本地请求
    ├── frida_hook.txt             Hook 全链路输出（7 行，toSign 一次没出现）
    ├── shot_frida_login_ok.png    复刻 App 登录成功截图（含请求参数与服务端返回）
    ├── shot_login_ok.png          早前一次登录成功截图
    ├── logcat_login_ok.txt        客户端侧完整日志
    ├── real_login_offline.png     真实 3.56.0 断网启动后的登录页
    ├── replay_result.json         Python 复算的请求/响应
    └── server_request_log.txt     服务端逐条校验记录
```

## 五、环境

- Windows 10/11 + PowerShell
- 真机 Pixel 2（Android 11，arm64-v8a，已 root）
- JDK：AGP 8.0.2 需要 JDK 17（本机用 `D:\Android\jbr`），`gradle 8.0` wrapper 发行包
- Android SDK：platform 33 + build-tools 30.0.3
- Python 3.8：Flask 2.0.3、pycryptodome、frida 16.3.3、frida-tools
- 设备端：`frida-server 16.3.3`（arm64）放在 `/data/local/tmp/frida-server`，root 启动
- PC 端：Charles 4.5.6、jadx 1.4.7
- 注意：本机 SDK 的 `ndk` 目录为空，所以复刻 App 没有编 `.so`，native 层用 Java 常量 + 同名方法模拟，真实 so 改用静态核验覆盖

## 六、怎么跑

```powershell
# 0. 起校验服务（必须监听 0.0.0.0，手机才连得上）
python server\chezhiying_server.py            # http://0.0.0.0:8000

# 1. 静态核验真实 apk（只读，不改包；关键类优先读 evidence\jadx_key_classes 的归档）
python scripts\00_apk_static.py "E:\路飞学城\课件\APP逆向(12期)\day14-车智赢app\软件\车智赢-v3.56.0.apk"

# 2. 编译并安装复刻 App
cd android
java -version                                 # 需要 17
gradle assembleDebug                          # 或 .\gradlew assembleDebug
adb install -r app\build\outputs\apk\debug\app-debug.apk

# 3. 确认 frida-server 在跑
adb shell "ps -A | grep frida"
python scripts\02_frida_hook.py               # 自动拉起 App、点登录、落 frida_hook.log

# 4. 纯 Python 复算
python scripts\10_replay_login.py             # 落 replay_result.json
```

App 里的服务端地址在登录页可直接改，默认填 PC 的局域网地址（`http://192.168.31.220:8000`）。

## 七、实测结果

| 检查项 | 结果 |
| --- | --- |
| 真实 apk | v3.56.0，178,992,876 字节，md5 `26964888fde2ccee78245a75b7cc8d22` |
| so 里的 3DES 全量 key | `libnative-lib.so` 偏移 `0x0a3a0d`（670221）命中 1 次，前后是 `\0yes\0…\0` |
| JNI 符号 | `Java_com_autohome_ahkit_jni_CheckSignUtil_get3desKey` 在偏移 81888 |
| 盐值归属 | 四套盐全在 `classes2.dex`，`SignManager` 就在这个 dex |
| 复刻 App 编译 | `BUILD SUCCESSFUL`，装真机启动正常 |
| 复刻 App 登录 | 服务端返回 `code:0 登录成功`，截图与 logcat 均在 `evidence/` |
| Frida Hook | 7 行输出，覆盖 `encodeMD5`×2、`getDesKey`、`encode3Des`、`getUDID`、`signByType`；`toSign` 一次未命中 |
| 纯 Python 复算 | `udid_plain=f58f2d53-…|6783696218932|`，`_sign=063B389C48E73AF1534A5699FA87EBD3`，服务端 `code:0` |
| 服务端校验记录 | 8 条，全部 `ok: true`，`errors: []` |
| 真实包离线启动 | 断网后直接进 `com.che168.autotradercloud.user.LoginActivity`，没有被强制更新拦住 |

一次 Hook 的完整落盘（`evidence/frida_hook.txt`）：

```
ready | hooks installed
encodeMD5 | in=123456 out=e10adc3949ba59abbe56e057f20f883e
getDesKey | key=appapiche168comappapiche168comap
encode3Des | plain=f58f2d53-1309-36e1-a690-a34c8f49691c|70379918572707| cipher=mxd5AgE5TjiAm6fL0By539zDo0KLfelEUv5UE/eLUuZWiq3aKsuT5YMSI90qmyliwlUBzAnisdc=
getUDID | udid=mxd5AgE5TjiAm6fL0By539zDo0KLfelEUv5UE/eLUuZWiq3aKsuT5YMSI90qmyliwlUBzAnisdc=
encodeMD5 | in=W@oC!AH_6Ew1f6%8_appidatc.android…username13800138000W@oC!AH_6Ew1f6%8 out=5901f37086c86d2fb10ddf6b5702e699
signByType | type=1 sign=5901F37086C86D2FB10DDF6B5702E699 map={…}
```

第 6 行那个超长 `in=` 就是签名原文：盐 + 排序后的键值对 + 盐。把它和 Python 侧 `SALT_V2 + "".join(k + v for k in sorted(params)) + SALT_V2` 对照，能逐字符对上。

## 八、和课件口径的差异（实测发现，不是抄错）

1. **复刻 App 只沿用了 KEY_V2**。真实包的 `KEY_V1="com.che168.www"`、`KEY_SHARE="moc.861ehc.relaed.bup.wyfv"`、`KEY_AUTOHOME="@7U$aPOE@$"` 都已在静态核验里确认，但复刻工程里另外三套盐换成了自造值（`a1b2c3d4e5f6g7h8` / `share#2024$chezhiying` / `autohome@api#2024`），因为登录只走 type=1，换掉不影响链路，还能顺带验证"盐和算法是解耦的"。要对真实包做 type=0/2/3，必须换回真值。
2. **`getUDID` 第一段的来源不同**。真实 3.56.0 是 `AHDeviceUtil.getDeviceId(context)`；复刻 App 用的是 `AppUtils.getIMEI` 四级降级（SP → `TelephonyManager.getDeviceId` → wlan0 MAC 的 UUID → AndroidID 的 UUID → `"sssss"`）。两者在明文里占的是同一个位置，服务端只校验"能解出三段"，因此都通得过。
3. **`nanoTime` 的量级**。课件里给的随机区间是 `5.1e12 ~ 7.1e12`，但真机实测是 `6.78e13 ~ 7.04e13`，大了一个数量级。设备不同、开机时长不同都会变，别把它当固定位数。
4. **`udid` 第三段可以是空串**。未登录状态下 `UserInfoUtil.getUserDeviceId` 返回空，拼出来的明文是 `段1|段2|`，末尾那个 `|` 必须保留，否则解密出来只有两段，服务端会判不合格。
5. **`AHAPIHelper.toSign` 是死代码**。它能被搜到、能被 Hook 上，但登录链路根本不经过它；真正打签名的是 `LaunchModel.lambda$initRequestCommonParams$0`。

## 九、本次操作对环境做的改动（请知悉）

- 手机原本装的是车智赢 **5.6.1**，课件包是 **3.56.0**。`adb install -r` 报 `INSTALL_FAILED_VERSION_DOWNGRADE`，改用 `adb install -r -d` 允许降级，**原 5.6.1 已被替换**。要恢复需自行重装。
- 手机原有全局代理 `192.168.31.220:8888`（陈旧值，Charles 没开时会让手机断网）。抓包期间启动 Charles 复用这个端口，结束后已执行 `settings put global http_proxy :0` 清空。
- 验证真实包能否离线启动时开过飞行模式，已执行 `cmd connectivity airplane-mode disable` 恢复，Wi-Fi 也已重新打开。
- 没有修改、重打包、二次签名任何官方 apk；静态核验只读取 apk 内的 so 与 dex 字节。

## 十、合规说明

- 目标始终是本机 `127.0.0.1:8000` 的自建服务端，没有对车智赢线上接口发起登录请求。
- 官方 apk 只做本地静态读取与离线启动截图，未做重打包分发。
- 目录中不含任何真实账号、密码、Cookie 或 token；`server_request_log.txt` 里的 `13800138000/123456` 是本地自建服务端写死的测试账号。
