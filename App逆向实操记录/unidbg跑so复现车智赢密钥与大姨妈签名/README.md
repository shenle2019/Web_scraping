# unidbg 本地跑 so：车智赢密钥与大姨妈签名

> 本目录所有代码仅限学习研究，禁止商用。仅调用 App 的 so 计算密钥/签名，不登录、不下单、不碰线上业务接口。

## 一、案例目标

把 day25 / day26 / day27 三课合成一条主线——**在 PC 上用 unidbg 跑 Android so，拿到与真机一致的结果**：

1. day25：环境搭建 + 32 位静态注册 so（车智赢 `libnative-lib.so` → `get3desKey`）
2. day26：换一个 so、换位数、换返回类型（大姨妈 64 位 `libCrypt.so` → `encrypt_data`）
3. day27：把 Java 侧打包成 jar，用 Python 调用并校验

## 二、课件结论（读课件后整理）

| 项目 | 结论 |
| --- | --- |
| unidbg 定位 | 在 PC 上模拟 Android 运行环境，直接加载 so 并调用其中的 JNI 方法，不需要真机/不需要脱壳 |
| 关键对象 | `AndroidEmulator`（设备）→ `Memory`（内存 + `AndroidResolver(23)`）→ `VM`（Dalvik 虚拟机）→ `DalvikModule`（so）→ `Module`（基址） |
| 静态/动态注册 | 车智赢是静态注册，不用执行 `JNI_OnLoad`；动态注册必须 `dm.callJNI_OnLoad(emulator)` |
| 位数匹配 | so 在 `armeabi-v7a` 用 `for32Bit()`，在 `arm64-v8a` 用 `for64Bit()`，错了直接加载失败 |
| 方法签名 | `get3desKey(Landroid/content/Context;)Ljava/lang/String;`、`encrypt_data(JLjava/lang/String;J)Ljava/lang/String;` |
| 补环境 | 当 so 回调 Java（如 TreeMap/entrySet、Context.getPackageName）时需要继承 `AbstractJni` 重写对应方法；本次两个案例都是纯计算，未触发回调 |

## 三、实现思路

```
课件 rar（925MB）
   └─ 只抽 3 类文件：out/artifacts/unidbg_0_9_7_jar/（含 unidbg-0.9.7.jar）
                     apks/che/libnative-lib.so + che3.32.1.apk
                     apks/dym/libCrypt.so

CheSignDemo.java  ──for32Bit──> libnative-lib.so ──> get3desKey(Context) = 32 位密钥
DymSignDemo.java  ──for64Bit──> libCrypt.so       ──> encrypt_data(0, 85 字明文, 85) = 32 位 sign
        │
        ├─ 真机交叉验证：frida 直接调用 CheckSignUtil.get3desKey(null)
        └─ 打包 che-sign.jar（MANIFEST 里写 Class-Path）→ Python 调用 + 校验
```

两个校验锚点：

- 车智赢：unidbg 结果 vs 真机 frida 调用结果，必须一字不差；
- 大姨妈：unidbg 结果 vs day22 已经由 frida-rpc 验过的签名值 `5bcd65ecd0bc26785ccbbdac1d06051f`。

## 四、运行方式

```powershell
# 1) 从课件 rar 抽取运行所需文件（只抽 3 类，避免解压 1GB）
& "C:\Program Files\7-Zip\7z.exe" x unidbg-0.9.7.rar `
  "unidbg-0.9.7\out\artifacts\unidbg_0_9_7_jar\*" `
  "unidbg-0.9.7\apks\che\*" "unidbg-0.9.7\apks\dym\*" -o<目标目录> -y

# 2) 编译 + 打包 jar（在 unidbg-0.9.7 目录）
.\build_java.ps1

# 3) 直接跑 / Python 调用
& "C:\Program Files\Java\jdk-1.8\bin\java.exe" -jar che-sign.jar
python 01_call_unidbg.py --out evidence_03_python_call.log

# 4) 真机交叉验证（需车智赢 APK 已安装、hluda/frida-server 已启动）
python 02_hook_real_app.py --out evidence_02_real_app.log
```

依赖：JDK 1.8（`java`/`javac`/`jar`）、课件自带 `unidbg-0.9.7.jar`、`frida` 客户端。

## 五、实测结果

### 1) 车智赢 32 位静态注册（本地 unidbg）

```
[unidbg] so base = 0x40000000
[unidbg] get3desKey = appapiche168comappapiche168comap
[unidbg] key length = 32
```

证据：[evidence/01_unidbg.txt](evidence/01_unidbg.txt)

### 2) 真机交叉验证（frida 直接调同一个 JNI 方法）

```
spawn pid=29637
真机 get3desKey = 'appapiche168comappapiche168comap'
结论：PASS 真机调用成功
```

两者**完全一致**，说明 unidbg 跑出来的不是"能跑但算错"的假结果。
证据：[evidence/02_real_app.txt](evidence/02_real_app.txt)

### 3) Python 调用打包后的 jar

```
[unidbg] get3desKey = appapiche168comappapiche168comap
解析出的 key = 'appapiche168comappapiche168comap'
与期望值比对：一致
结论：PASS Python 调用 unidbg 成功且结果稳定
```

证据：[evidence/03_python_call.txt](evidence/03_python_call.txt)

### 4) 大姨妈 64 位 so（换位数 + 换返回类型）

```
[unidbg] so base = 0x40000000
[unidbg] plain length = 85
[unidbg] sign = 5bcd65ecd0bc26785ccbbdac1d06051f
```

与 day22 用 frida-rpc 在真机上算出的 `5bcd65ecd0bc26785ccbbdac1d06051f` 相同。
证据：[evidence/04_dym_unidbg.txt](evidence/04_dym_unidbg.txt)

## 六、文件说明

| 文件 | 作用 |
| --- | --- |
| `src/CheSignDemo.java` | 车智赢 32 位 so → `get3desKey` |
| `src/DymSignDemo.java` | 大姨妈 64 位 so → `encrypt_data` |
| `manifest.txt` | jar 的 `Main-Class` + `Class-Path` |
| `build_java.ps1` | javac 编译 + jar 打包 |
| `01_call_unidbg.py` | Python 调 jar、正则取 key、与期望值比对 |
| `02_hook_real_app.py` | 真机 frida 调用同一 JNI 方法做交叉验证 |
| `evidence/` | 运行日志（.txt 规避仓库 `*.log` 忽略规则） |

> `unidbg-0.9.7.jar`（146MB）、`che3.32.1.apk`（121MB）、`libnative-lib.so`、`libCrypt.so` 均来自课件，不入库；按上面第 1 步从 rar 里抽取即可复现。

## 七、结论

- unidbg 的核心不是"破解算法"，而是**把 so 当黑盒在 PC 上调用**：只要方法签名、位数、JNI 注册方式对，结果和真机一致。
- 本次两个 so 都是纯计算，没有触发 Java 回调，所以不需要补环境；真正需要补环境的是回调里用到 `TreeMap`、`Context`、`SharedPreferences` 的案例（day26 的唯品会/得物），本目录只记录结论，未复刻那两个。
- 打包成 jar 后 Python 直接 `subprocess` 调用即可，适合挂到爬虫脚本里；但要注意 jar 依赖的 `Class-Path` 必须写对，否则 `NoClassDefFoundError`。
