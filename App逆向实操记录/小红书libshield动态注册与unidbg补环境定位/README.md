# 小红书 libshield 动态注册与 unidbg 补环境定位

> 本目录所有代码仅限学习研究，禁止商用。只做 so 静态分析 + PC 侧加载，不启动线上 App、不登录、不发业务请求。

## 一、案例目标

复刻 day28 + day29 小红书 shield 案例的关键结论，并如实给出可验证的边界：

1. 定位加密点：`libshield.so` + `com.xingin.shield.http.XhsHttpInterceptor`，native 方法 `intercept(Chain, long)` 往请求头写 `shield` / `xy-platform-info`
2. 确认 so 是**动态注册**（`JNI_OnLoad` + `RegisterNatives`），不是 `Java_*` 静态导出
3. 在 unidbg 里加载 so，按课件思路一层层补环境，记录**具体卡在哪一层**

## 二、课件结论（读课件后整理）

| 项目 | 结论 |
| --- | --- |
| so | `libshield.so`（armeabi-v7a，32 位） |
| Java 类 | `com.xingin.shield.http.XhsHttpInterceptor implements Interceptor` |
| native 方法 | `static native void initializeNative()`、`native long initialize(String)`、`native Response intercept(Interceptor.Chain, long)` |
| 初始化顺序 | 类静态块 `initializeNative()` → 构造器 `cPtr = initialize(str)` → 请求时 `intercept(chain, cPtr)` |
| 产出 | 请求头 `shield: <加密串>`、`xy-platform-info: <加密串>` |
| 难点 | day29 用 unidbg 跑 intercept 时需要补大量 okhttp3/okio/SharedPreferences 环境，属于"堆环境"型案例 |

## 三、实现思路

分两步，先静态、再动态：

```
01_inspect_so.py   ── 解析 ELF：架构 / .dynsym / 关键字符串（不执行、不联网）
XhsShieldDemo.java ── unidbg：for32Bit + AndroidResolver(23) + loadLibrary + JNI_OnLoad
                        └─ AbstractJni 里逐层补环境，日志打印"未处理的方法签名"
```

补环境方式：重写 `callObjectMethodV`，对已知签名返回假对象，其余打印出来再交给父类，这样每次运行都能看到 so 下一个要什么。

## 四、运行方式

```powershell
# 静态取证
python 01_inspect_so.py --out evidence_02_so_static.log

# unidbg 加载（需要 day25 抽出来的 unidbg-0.9.7.jar）
& "C:\Program Files\Java\jdk-1.8\bin\javac.exe" -encoding UTF-8 -cp <unidbg.jar> -d classes unidbg\unidbg-0.9.7\src\XhsShieldDemo.java
& "C:\Program Files\Java\jdk-1.8\bin\java.exe" -cp "classes;<unidbg.jar>" XhsShieldDemo
```

`apks/xhs/libshield.so` 从课件 `day28-小红书案例1\apk\libshield.so` 拷贝（738,920 字节）。

## 五、实测结果

### 1) ELF 静态取证（可复现）

```
架构 = ARM(32)，ELF32
导出函数总数 = 473，其中 Java_* 静态注册符号 = 0
  JNI_OnLoad：有
字符串 com/xingin/shield/http/XhsHttpInterceptor      出现 1 次
字符串 initializeNative                               出现 1 次
字符串 okhttp3/Interceptor                            出现 2 次
字符串 xy-platform-info                               出现 1 次
```

证据：[evidence/02_so_static.txt](evidence/02_so_static.txt)

结论：`Java_*` 导出为 0 + `JNI_OnLoad` 存在 ⇒ 动态注册；类名与 header 名都在 so 里，和课件 hook 结果互相印证。

### 2) unidbg 加载与补环境定位

第一轮：`JNI_OnLoad` 里 so 调 `android/app/Application->getPackageName()Ljava/lang/String;`，未补环境直接抛
`Illegal JNI version: 0xffffffff`。

补上返回 `com.xingin.xhs` 后，第二轮前进到：

```
emulate RX@0x400102ed[libshield.so]0x102ed exception
msg=android/content/pm/PackageInfo->signatures:[Landroid/content/pm/Signature;
```

证据：[evidence/01_xhs_init.txt](evidence/01_xhs_init.txt)

也就是说：**so 在 JNI_OnLoad 阶段就要校验宿主包名与签名**，之后才会注册 native 方法。要继续往下走，需要伪造 `PackageInfo`、`Signature[]` 乃至签名校验结果；再往后 `intercept` 还需要 okhttp3 的 `Request/Response/Headers/Chain` 全套对象，这正是 day29 里"补环境补到崩溃"的部分。

**本目录没有打通 intercept，也不伪造 shield 值**。这一节的价值是把"卡在哪一层、下一层要什么"变成可复现的日志，而不是一个假的成功截图。

## 六、文件说明

| 文件 | 作用 |
| --- | --- |
| `01_inspect_so.py` | ELF 解析：架构、导出函数、关键字符串（纯静态） |
| `unidbg/unidbg-0.9.7/src/XhsShieldDemo.java` | unidbg 加载 so + 第一层补环境 + 未处理签名打印 |
| `evidence/01_xhs_init.txt` | unidbg 两轮加载日志（含失败点） |
| `evidence/02_so_static.txt` | ELF 静态分析结果 |

> `libshield.so` 与 `unidbg-0.9.7.jar` 均来自课件，不入库。

## 七、结论与边界

- 已证实：so 走动态注册、初始化阶段做宿主校验、header 名写死在 so 里，与课件 hook 结论一致。
- 未完成：unidbg 跑通 `intercept` 生成 `shield`。原因是初始化链上的签名校验 + okhttp3 环境依赖，属于课件里最重的一类补环境工作。
- 替代路线（课件同样给出）：真机 frida hook `XhsHttpInterceptor.intercept` 直接读 header 值；但本次按"不碰真实 App 账号"的约束没有走这条，避免触发风控。
- 如果后续要继续，建议顺序：先伪造 `PackageInfo.signatures` 让 `JNI_OnLoad` 返回正常版本号 → 再补 `okhttp3.Request/Response` 的 `ProxyDvmObject` → 最后用 `intercept` 的 `Chain` 代理对象取 header。
