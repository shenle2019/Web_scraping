# BiliReplica：自建 App 复刻 B站播放量/完播率签名链路

参考 day17~day19 课件，在本地从零写一个 Android App（不是改 B站 APK），把三天涉及的
签名与加密算法原样实现一遍，装到真机跑通，再用 jadx / Frida 反向验证这些算法能被正常
还原出来。

> 仅限学习研究，禁止商用。
> 全部请求只发往本机 mock server（`127.0.0.1:8899`，通过 `adb reverse` 映射），
> 不连接 B站任何线上接口，不做刷量。

## 一、复刻映射

| 课件知识点 | 本工程落点 | 文件 |
| --- | --- | --- |
| `H7` 拼 TreeMap + sha256 加盐 + 整体 AES | `ClickReport` + `BiliCrypto` | `app/src/com/example/bililike/ClickReport.java` |
| AES key/iv/盐常量 | `BiliCrypto` 常量 | 同上 |
| did 异或链 + Base64 | `DeviceProfile.buildDeviceId` | `app/src/com/example/bililike/DeviceProfile.java` |
| buvid XW/XY/XX/XZ | `DeviceProfile.buildBuvid` | 同上 |
| session_id 4 字节 hex | `DeviceProfile` 构造 | 同上 |
| fp_local = md5 + 时间 + 随机 + 校验码 | `DeviceProfile.buildFingerprint` + `BiliCrypto.fpChecksum` | 同上 |
| 拦截器写 4 个指纹头 | `ReportInterceptor.headers` | `app/src/com/example/bililike/ReportInterceptor.java` |
| heartbeat session=SHA1 | `HeartbeatReport.newSession` | `app/src/com/example/bililike/HeartbeatReport.java` |
| so 层 md5(明文+四段盐) | JNI 动态注册 + MD5 | `app/jni/bili_sign.c` |
| RegisterNatives 取偏移 | Frida 脚本 03 | `tools/frida/03_hook_register_natives.js` |
| hook update 取四段盐 | Frida 脚本 04 | `tools/frida/04_hook_native_md5_update.js` |
| NewStringUTF 兜底 | Frida 脚本 05 | `tools/frida/05_hook_newstringutf.js` |

## 二、目录结构

```
app/                 Android 源码（Java）+ jni/bili_sign.c
build.ps1            不依赖 Gradle 的构建脚本（aapt2 -> javac -> d8 -> clang -> 打包 -> 签名）
pack_apk.py          把 classes.dex 与 lib/ 塞进 aapt2 产出的壳 APK
server/              mock 服务端 + 验签日志 + 真机自检日志 + 断网冷启动截图
results/             summary.json 汇总 + build_summary.py/capture_selftest.py + frida_logs/ 实测日志
client_replica.py    Python 侧第二实现（交叉验证）
tools/frida/         5 个 hook 脚本 + run_hook.py 运行器
scan_bili_apk.py     对课件原 APK 做只读常量核对（dex）
scan_bili_so.py      对课件 libbili.so 做只读字符串核对
```

> 日志文件以 `.txt` 名义保存在 `results/frida_logs/` 与 `server/` 下：仓库 `.gitignore`
> 排除了 `*.log`，这些是实测证据而不是运行时垃圾，所以改扩展名入库。
> `summary.json` 里的数字全部由 `build_summary.py` 从上述日志解析生成，不手写。

## 三、环境与工具（本机实测）

- PC：Windows 10 22H2、JDK 1.8.0_371、Python 3.8.8（pycryptodome 3.24.0 / frida 16.3.3）
- Android SDK：`build-tools 30.0.3`、`platforms/android-30`，NDK **r25c**（本次新装，`D:\soft\android-ndk-r25c`）
- 反编译：jadx CLI（`D:\soft\jadx-cli`）
- 真机：Pixel 2 / Android 11（SDK 30）/ arm64-v8a / Magisk root，`frida-server 16.3.3` 常驻
- 本次新装到真机：`BiliReplica.apk`（自建）、`B站-v6240.apk`（仅静态核对 + 断网冷启动验证）

## 四、构建与运行

```powershell
# 1. 构建（NDK 路径按实际改）
powershell -ExecutionPolicy Bypass -File .\build.ps1

# 2. 起 mock 服务端
python .\server\mock_server.py

# 3. 端口反向映射 + 装机
adb reverse tcp:8899 tcp:8899
adb install -r .\build\BiliReplica.apk

# 4. 跑自检（App 启动即自动跑一遍）
adb shell am start -n com.example.bililike/.MainActivity
adb logcat -s BiliReplica:I
```

## 五、实测结果

| 验证项 | 方式 | 结果 |
| --- | --- | --- |
| native 与 Java 签名一致性 | App 自检 `native_parity` | PASS（三值相同） |
| click 请求体（AES + SHA256 盐） | mock server 解密后重算签名 | PASS |
| heartbeat 开始/结束（MD5 四盐 + session 形态） | mock server 重算 | PASS |
| 真机整链路 | `SELFTEST|99|done` | **3/3 PASS** |
| 服务端累计校验 | `verification_log.jsonl` 重算 | click 32、heartbeat 64、failed 0 |
| Python 第二实现 | `client_replica.py` | PASS（3 个请求全部 verified） |
| so 层偏移 | hook RegisterNatives | `nativeSign` offset **0x23cc** |
| so 层四段盐 | hook `bili_md5_update`（导出符号偏移 0x17dc） | `560c52cc` / `d288fed0` / `45859ed1` / `8bffd973`，两组心跳各 4 段 |
| so 返回值锚点 | hook NewStringUTF（长度 32） | 命中 md5，栈顶 `libbili.so!native_sign+0x19c` |
| 课件原 APK 常量核对 | dex 只读搜索 | 地址/盐/key/iv 全部命中（classes5/9/10.dex） |
| 旧版强制更新绕过 | 断网冷启动 B站 v6.24.0 | 直接进隐私协议页，未弹强制更新 |

## 六、与课件的差异（有意为之）

1. **不改线上 APK**：所有动态调试都打在自建 `com.example.bililike` 上，算法一致、数据不出本机。
2. **so 函数导出**：真实 `libbili.so` 里 update 是静态函数，要靠 IDA 找偏移；本工程把
   `bili_md5_update` 导出（并加 `noinline`），Frida 直接按符号挂，偏移仍由脚本现场算，
   保留「模块基址 + 偏移」这一课的核心结论。
3. **heartbeat 的 aid/cid 用固定值**：本地 mock 不校验业务字段，只校验签名与结构。
