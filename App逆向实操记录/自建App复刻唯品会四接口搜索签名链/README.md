# 自建App复刻唯品会四接口搜索签名链

> 仅限学习研究，禁止商用。
> 复刻课件：day20-唯品会01、day21-唯品会02（APP逆向 12 期）
> 测试对象：唯品会 v7.83.3（老版本，未更新，按教程方式绕过反调试）

## 案例目标

打通唯品会 App 搜索功能的四接口签名链，用纯算方式在本地复刻出服务端可识别的签名：

| # | 接口 | 方法 | 地址 | 作用 |
|---|------|------|------|------|
| 1 | device_reg | GET | https://mp.appvipshop.com/apns/device_reg | 注册设备，拿 device_token |
| 2 | getTokenByFP | GET | https://vcsp-api.vip.com/token/getTokenByFP | 拿 vcspToken |
| 3 | generate_token | POST | https://mapi.appvipshop.com/vips-mobile/rest/device/generate_token | 拿 did |
| 4 | 搜索 | POST | https://mapi.appvipshop.com/vips-mobile/rest/shopping/search/product/list/v1 | 商品搜索（最终目标） |

## 破解结论（算法还原）

- **api_sign**：`sha1(SALT + sha1(SALT + 按 key 排序后的参数字符串))`，双层 sha1
  - SALT = `aee4c425dbb2288b80c71347cc37d04b`
- **vcspSign**：同双层 sha1，盐 = `da19a1b93059ff3609fc1ed2e04b0141`；明文固定 → 结果为固定值
  - `05a68135d2bfd322e3a22f95bbc25a24c777f387`
- **edata**（第 3 接口请求体加密）：`base64(iv字节 + AES_CBC_PKCS5Padding(明文))`
  - key = `md5(b"aee4c425dbb2288b80c71347cc37d04b").digest()` = `cdd17ab29b84b32552ddcfbb4abf0225`
  - iv = 16 位随机 hex 字符
- 固定值：
  - api_key = `23e7f28019e8407b98b84cd05b5aef2c`
  - skey = `6692c461c3810ab150c9a980d0c275ec`
  - vcspKey = `4d9e524ad536c03ff203787cf0dfcd29`
  - channel = `oziq7dxw:::`
- 随机值：device_token / mars_cid = uuid4；did 取第 3 接口返回

## 反调试绕过（按教程方式）

App 内有 libmsaoaidsec.so 反调试检测，root 手机直接删除即可（课件 day20 绕过方式，不更新 APK）：

```
/data/app/.../com.achievo.vipshop-.../lib/arm/libmsaoaidsec.so   ← root 删除
```

删除后 frida attach + hook 正常输出（见 evidence/hook_final.log）。

## 目录结构

```
├── README.md                  # 本说明
├── 验证记录.md                 # 环境清单 + 真实评测结果
├── scripts/
│   ├── 00_verify_sign.py      # 算法对照验证（与课件 hook 输出比对，4/4 通过）
│   └── 01_repl_search.py      # Python 四接口签名链复刻脚本
├── android/                   # 自建 Android App（Java 实现同一签名链）
│   └── app/src/main/java/com/achievo/vipshop/repl/MainActivity.java
├── frida/                     # 真机 hook 取证脚本（01~08，08 为最终一体化脚本）
└── evidence/                  # 验证证据
    ├── hook_final.log         # gsNav 真实签名 hook 输出 + 进程存活结论
    ├── hook_search_api.log    # 搜索触发后进程存活结论
    └── 自建app四接口执行结果.png  # 真机自建 App 四接口执行截图
```

## 运行方式

### 1. Python 复刻（PC 端）

```bash
python scripts/00_verify_sign.py   # 先跑算法对照
python scripts/01_repl_search.py   # 再跑四接口签名链
```

### 2. 自建 App（安卓真机）

- 工程：`android/`（gradle 8.0 + AGP 8.0.2 + compileSdk 33，零依赖纯 Java）
- 构建：`gradlew assembleDebug`（JAVA_HOME=D:\Android\jbr，sdk.dir 指向本机 AndroidSdk）
- 安装：`adb install app/build/outputs/apk/debug/app-debug.apk`
- 验证：点按钮执行四接口，`adb logcat -s VipRepl` 看完整请求与响应

### 3. 真机 hook 取证（frida）

```bash
# 手机先启动 frida-server，root 删除 libmsaoaidsec.so 后：
python frida/08_auto_hook_search.py
```

## 真实评测结果摘要

- 算法对照：4/4 与课件 hook 输出一致
- 四接口：前 3 个接口真实返回 200（注册成功 / vcspToken / did），参数与签名全部被服务端接受
- 搜索接口：返回 `{"msg":"Forbidden by TFS","code":11000}` —— 与课件原版代码、Python 复刻、自建 App 三方结果一致，判定为服务端 TFS 风控升级（对无 App 环境的请求拦截），非复刻错误
- 反调试绕过：删 so 后 frida hook 正常、进程 120 秒存活，绕过有效
