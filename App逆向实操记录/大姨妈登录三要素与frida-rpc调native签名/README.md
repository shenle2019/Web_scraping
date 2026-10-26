# 大姨妈 v8.6.0 登录三要素与 frida-rpc 调 native 签名

> 仅限学习研究，禁止商用。脚本单次请求、低频调用，只对课件自带测试账号做验证。

## 目标

把大姨妈 App（v8.6.0，课件自带测试包）登录接口
`POST https://uicapi.yoloho.com/user/login` 的三个要素还原并在 PC 端复刻：

| 要素 | 算法位置 | 还原方式 |
| --- | --- | --- |
| `device` | `PeriodAPIV2.setDeviceCode()` 内 `sha1(拼接明文)` | hook `MessageDigest.update` 抓明文，本地 sha1 复算 |
| `password` | `AESUtil.encrypt(密码, key, iv)` | hook 取 key/iv/密文；本地 AES-128-CBC 复算 |
| `sign` | `Crypt.encrypt_data(0, device+"user/login"+手机号+密文, 长度)`，native 实现在 `libCrypt.so` | 不硬跟 so，frida-rpc 把明文塞回 app 自己的方法执行 |

## 环境

- 手机：Pixel 2（`FA7B11A03073`），Android 11，Magisk root
- frida-server 16.3.3（arm64）运行在手机上，PC 侧 frida 16.3.3
- App：`day22-DYM-app\软件\大姨妈v8.6.0.apk`（不升级，保持 8.6.0）
- PC：Python 3.9 + requests + pycryptodome

## 两个必须先处理的拦路虎

1. **root 检测**：冷启动即弹「手机不安全」并退出。
   hook `com.yoloho.libcore.util.MiscUtil.isRooted/isSimulator` 返回 false，
   再 hook `com.mobile.auth.gatewayauth.manager.SystemManager.checkEnvSafe` 返回 null（去掉吐司）。
2. **更新弹窗**：会在登录页上层挡点击，返回键、点外部、`WindowManagerGlobal.removeView` 都无效。
   最终用**断网启动**解决：
   ```powershell
   adb shell svc wifi disable; adb shell svc data disable
   # 用 spawn 模式启动并 hook
   python scripts\01_hook_three_elements.py spawn 900
   adb shell svc wifi enable; adb shell svc data enable
   ```
   登录页干净出现后再恢复网络。

## 运行

```powershell
# 0. 手机端 frida-server（root）
adb shell su -c "nohup /data/local/tmp/frida-server-16.3.3-android-arm64 &"

# 1. 三要素 hook：attach 到已经停在登录页的 app
python scripts\01_hook_three_elements.py attach 600

# 2. 手机上点「我已阅读并同意」再点「确定」，控制台会打印 device/password/sign

# 3. PC 复刻：AES 本地算，sign 走 frida-rpc，发真实请求
python scripts\03_replay_login.py <手机号> <密码> --out evidence\03_replay_login_response.txt
```

`02_rpc_sign.py` 可单独调用，给任意拼接明文算 sign。

## 目录

```
scripts\01_hook_three_elements.py   root 绕过 + device/password/sign 全 hook（spawn/attach 两种模式）
scripts\02_rpc_sign.py              frida-rpc 单独算 sign
scripts\03_replay_login.py          device 复算 + AES 密码 + rpc 签名 + 真实登录请求
evidence\01_hook_three_elements.log 三要素 hook 原始输出
evidence\02_device_sha1_check.txt   device/password 本地复算核验
evidence\03_replay_login_response.txt 登录接口真实返回
evidence\04_login_page.xml          登录页 uiautomator dump（页面禁截屏，用 XML 留证）
evidence\05_device_env.txt          手机环境参数
```

## 结论

- `sha1(device 明文)` 本地复算 = app 的 `deviceCode`，完全一致。
- 本地 AES 算出的密码密文与 hook 抓到的一致（key = `md5(手机号)[:16]`，iv 固定）。
- `sign` 由 app 的 native 方法返回，PC 侧无需逆向 so 即可复用。
- 用这套三要素向服务端发真实请求，服务端能通过签名校验并进入业务判断，
  具体返回见 [验证记录.md](验证记录.md)。

## 踩坑

- 登录页 `FLAG_SECURE`，`screencap` 产出 0 字节，只能 `uiautomator dump` 留证。
- App 走的是 Android 平台内置 `HttpURLConnection`（`com.android.okhttp.*`），
  hook `okhttp3.*` 抓不到任何请求，得换 `java.net.URL` / `com.android.okhttp.internal.huc.HttpURLConnectionImpl`。
- 登录按钮受「我已阅读并同意」勾选控制，每次登录失败后勾选会复位，点「确定」前要先点 `ivCheck`。
- 账号密码连错会触发服务端限流（提示半小时后再试），调试时不要连续试错。
