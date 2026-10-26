# 动态调试：dex 断点命中与 smali 改包重签

> 本目录代码仅限学习研究，禁止商用。被测 App 是课件自带的 SoDebug 自建工程（包名 com.nb.sodebug），不涉及任何线上账号与真实业务。

## 一、案例目标

把 day30（smali 语法、调试权限、dex 调试）与 day31（so 调试、IDA、DDMS/jdb）合并成一条主线：

1. 用 `am start -D` + `adb forward jdwp` + `jdb` 打通 **dex 断点调试**，在 `onClick` 命中并读出 native 返回值
2. 用 baksmali/smali + zipalign + apksigner 复刻课件里 MT 管理器的 **改 smali + 重签名** 流程
3. 用 IDA 8.3 + `android_server64` 打通 **so 调试**（attach/spawn、下断点、看寄存器）

## 二、课件结论（读课件后整理）

| 项目 | 结论 |
| --- | --- |
| dex 调试 | 需要能读 smali；jadx/JEB 断点，底层就是 JDWP + jdb（DDMS 也是干这个） |
| 调试权限 | `ro.debuggable=1`（MagiskHidePropsConf 或 AOSP userdebug）**或** App 清单 `android:debuggable="true"` |
| so 调试 | 手机跑 `android_server(64)`，PC 端 `adb forward tcp:23946`，IDA attach/spawn，F2 断点、F8 单步 |
| spawn 模式 | 先 `adb shell am start -D -n 包/Activity`，IDA 附加后再用 `jdb -connect ... port=8700` 放行 |
| 常见坑 | IDA 7.5 启动调试会崩，课件要求换 IDA 8.3；IDA 绿色版路径不能含中文；ddms/jdb 需 JDK 1.8 |

## 三、本机实际走法

- 本机 `ro.debuggable=0`，但 SoDebug 是 debug 包（`run-as com.nb.sodebug id` 可验证），按课件“二者满足其一”走 **per-app debuggable**，没有刷 MagiskHidePropsConf（避免改全局属性 + 重启风险）
- jdb 用 `C:\Program Files\Java\jdk-1.8\bin\jdb.exe`
- smali/baksmali 用 jadx-1.4.1/lib 里的 `baksmali-2.5.2.jar` / `smali-2.5.2.jar`（瘦 jar，需要把 dexlib2/util/guava/antlr 一起放进 `-cp`，再指定 `org.jf.baksmali.Main`）
- 改包签名用 SDK build-tools 30.0.3 的 `zipalign.exe` + `apksigner.bat`，keytool 生成测试 keystore（keystore 只留在本机 `smali_work/`，未入库）

## 四、实测结果

### 1) dex 断点调试（PASS，7/7）

```text
[0] ro.debuggable = 0
[0] run-as 验证 debuggable = uid=10217(u0_a217) ... context=u:r:runas_app:s0
[1] am start -D -> pid 30768
[2] adb forward tcp:8700 jdwp:30768
[3] jdb -connect com.sun.jdi.SocketAttach:hostname=127.0.0.1,port=8700
[4] stop in com.nb.sodebug.MainActivity$1.onClick
[5] 点击"点我"(115,273) -> 断点命中: "线程=main", com.nb.sodebug.MainActivity$1.onClick(), 行=34
[6] next 单步越过 Utils.demo() -> 方法参数: result = 3
[7] E/测试  (30768): 3
总判定：PASS
```

关键点：断点下在 `MainActivity$1.onClick`，不能下在 `Utils.demo`（native 方法没有 Java 字节码）；`next` 越过 native 调用后 `result` 直接可见，等于在 Java 侧看到了 native 的返回值。

证据：`evidence/01_dex_debug.txt`

### 2) smali 修改 + 重打包 + 重签名（PASS，9/9）

```text
[1] apk 内 dex：classes3.dex, classes.dex, classes2.dex, classes4.dex
[1] 目标类 Lcom/nb/sodebug/MainActivity; 在 classes3.dex
[2] 命中的原指令：const-string v2, "\u6d4b\u8bd5"
  [smali] const-string v2, "PATCHED_BY_SMALI"
[3] smali 汇编回 dex：2592 字节
[4] zipalign -p 4 -> apksigner sign -> verify：CN=Demo ...
[5] 卸载原版 -> 安装改包 Success
[logcat] E/PATCHED_BY_SMALI(31771): 3
总判定：PASS
```

坑点记录：
- App 自身类不在 `classes.dex`，要按 `Lcom/nb/sodebug/MainActivity;` 在四个 dex 里找
- baksmali 会把中文常量转成 `\uXXXX`，正则要匹配转义形式，否则“找不到 const-string”
- `resources.arsc` 必须不压缩存放，否则 targetSdk 30+ 安装被拒
- 重签名后与原包签名不同，必须先 `adb uninstall` 再装

证据：`evidence/02_smali_patch.txt`

### 3) so 调试（未打通，卡在 IDA 启动）

已完成、可复现的部分：

```text
adb push dbgsrv/android_server64 /data/local/tmp/android_server64 && chmod 755
su -c "nohup /data/local/tmp/android_server64 -p23946 >/data/local/tmp/as.log 2>&1 &"
ps: root 31878 ... android_server64
as.log: IDA Android 64-bit remote debug server(ST) v8.3.28
        Listening on 0.0.0.0:23946...
adb forward tcp:23946 tcp:23946  ->  TCP 23946 connect = OK
```

App 侧：点击一次按钮后 so 已加载，`/proc/31972/maps` 中
`758322a000-758322b000 r-xp 00000000 .../lib/arm64/libutils.so`，即模块基址 `0x758322a000`。

卡点：IDA 绿色版启动即退出（exit 1，未生成 .i64），日志只有
`The key file is not found. -> OK`。排查结论：

1. 首次失败是**中文路径**导致 88 个插件全部 `LoadLibrary ... can't load file`；建 `C:\ida83` 目录联接（junction）后插件正常加载（课件自带说明也写了“释放路径不要含中文”）
2. 用桌面代理跑完 `IDA_Pro_8.3_绿化工具.exe`：输出“设置.idb/.i64 文件关联成功 / 桌面快捷方式成功 / 绿化完成!”，生成 `C:\ida83\ida.key`，注册表写入 `License = P.Y.G Team, Personal license`、`Python3TargetDLL = C:\ida83\python311\python311.dll`
3. 绿化后再启动 IDA，被 **IDAPython 运行时**挡住：
   `Unexpected fatal error while initializing Python runtime. Please run idapyswitch...`
   原因是绿色版 `python311` 目录不完整：`python311._pth` 只写了 `python311.zip` 和 `.`，但 zip 不存在，标准库实际在 `python311\python311\` 下，连 `python.exe -c "print(1)"` 都报 `No module named 'encodings'`

因此 **IDA attach、断点、F8 单步这一段没有跑通，本目录不伪造 so 断点结果**。`ida_work/test_attach.idc` 是把 attach 流程脚本化的半成品，恢复环境后可直接复用。

## 五、恢复后的下一步（按成本排序）

1. 修 Python 运行时（最小改动）：在 `C:\ida83\python311\python311._pth` 末尾补一行 `python311`，再启动 `ida64.exe`
2. 或运行 `C:\ida83\idapyswitch.exe`，指定本机可用的 Python 3（如 `D:\Android\jbr` 之外的 CPython）
3. 或临时把 `C:\ida83\python311\python311.dll` 改名，让 IDA 不加载 IDAPython（能进主界面，但没有 Python 插件）
4. IDA 能进主界面后：`idat64.exe -A -S attach.idc libutils.so`，脚本里 `LoadDebugger("android")` → `SetRemoteDebugger("127.0.0.1","",23946)` → `AttachProcess(pid,-1)` → `RebaseProgram(0x758322a000, MSF_FIXONCE)` → 在 `Java_com_nb_sodebug_Utils_demo` 下断 → `ContinueProcess` → 点按钮 → `GetRegValue`/`StepInto` 读 age/size/result

## 六、文件说明

| 文件 | 作用 |
| --- | --- |
| `01_dex_debug.py` | am start -D + forward + jdb 断点 + next/locals + logcat 验收（7 项判定） |
| `02_smali_patch.py` | 定位目标 dex → baksmali → 改 TAG → smali → 重打包 → zipalign → 重签 → 装机验证（9 项判定） |
| `ida_work/test_attach.idc` | IDA attach 连通性脚本（LoadDebugger/SetRemoteDebugger/AttachProcess/GetRegValue），等 IDA 修好后继续 |
| `evidence/01_dex_debug.txt` | dex 调试全过程日志 |
| `evidence/02_smali_patch.txt` | 改包重签全过程日志 |
| `evidence/03_ida_attempt.txt` | IDA 批处理失败与 python311 目录缺陷的取证 |

不入库：`smali_work/`（中间 dex、改包、keystore）、`libutils.so`（课件资产）、IDA 本体与 android_server（工具）。

## 七、结论与边界

- dex 调试、smali 改包重签两条链路已在真机完整跑通并可重复执行
- so 调试只完成到“android_server 在手机上跑起来 + 端口转发 + 模块基址已定位”，IDA 侧被绿色版 Python 运行时卡住，未产生断点/寄存器证据
- 全程只用自建 SoDebug 测试包，没有碰线上 App 与真实账号；`ro.debuggable` 保持 0，走的是 per-app debuggable
