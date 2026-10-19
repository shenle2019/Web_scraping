# charles抓包与jadx反编译定位登录MD5

## 案例目标
复刻 day03 课件案例：对「车智赢」App 的登录请求抓包，发现密码字段 `pwd` 是 32 位
十六进制密文；再用 jadx 反编译 apk 定位加密函数 `SecurityUtil.encodeMD5`，
确认其为标准 MD5（小写 hex），并用 Python 复算验证三方一致。

## 环境
- 手机：Pixel 2（Android 11，已 root，已装 Charles 根证书，192.168.31.44）
- 抓包：Charles 4.5.6（PC 192.168.31.220:8888 代理）
- 反编译：jadx 1.4.7（CLI），目标 apk 为 day03 资料包中的 车智赢3.42.0.apk
- 实际登录的 App 版本：5.6.1（appbuildcode=512，用户手动更新过）

## 步骤与思路
1. **抓包**：手机走 Charles 代理登录测试账号（18953675221 / 1111111），抓到
   `POST https://dealercloudapi.che168.com/tradercloud/sealed/login/login.ashx`
   请求体含 `pwd=7fa8282ad93047a4d6fe6111c93b308a`（32 位十六进制，疑似 MD5）。
2. **反编译**：jadx 反编译 apk 后按课件思路搜 `login.ashx`，定位调用链：
   - `com/che168/autotradercloud/user/model/UserModel.java:87`
     `public static final String LOGIN_URL = "/tradercloud/sealed/login/login.ashx";`
   - `UserModel.java:149` 的 `loginByPassword()`：
     `... .url(LOGIN_URL).param("username", str2).param("type", str4)`
     `.param("signkey", str5).param("pwd", SecurityUtil.encodeMD5(str3));`
   - `com/autohome/ahkit/utils/SecurityUtil.java:57` 的 `encodeMD5()`：
     `MessageDigest.getInstance("MD5")` → 逐字节转十六进制字符数组 → `toLowerCase()`，
     即标准 MD5 小写 hex。
3. **验证**：`hashlib.md5(b"1111111").hexdigest()` 与抓包密文、课件标准结果三方一致。

## 目录结构
- `capture/车智赢登录抓包会话.chls` —— Charles Auto Save 导出的完整会话（登录请求证据）
- `scripts/01_提取Charles抓包请求.py` —— 从 .chls 提取 login.ashx 请求与参数明细
- `scripts/02_验证MD5.py` —— hashlib 复算 MD5 并与抓包密文、课件结果比对
- `scripts/验证结果_01_抓包提取.txt`、`scripts/验证结果_02_MD5验证.txt` —— 运行输出存档
- `evidence/UserModel.java`、`evidence/SecurityUtil.java` —— jadx 反编译关键证据文件
- `decompiled/` —— jadx 对 3.42.0.apk 的完整反编译输出（体积大，已 gitignore，可再生）

## 运行方式
```
cd scripts
python 01_提取Charles抓包请求.py     # 缺省读取 ../capture/车智赢登录抓包会话.chls
python 02_验证MD5.py
```

## 验证结果
`01_提取Charles抓包请求.py` 输出（节选）：
```
[请求] POST https://dealercloudapi.che168.com/tradercloud/sealed/login/login.ashx
[请求体] appid=atc.android&_sign=44130B1ECCA8677A9E0EB8BDB2E8D8A1&appbuildcode=512&...&pwd=7fa8282ad93047a4d6fe6111c93b308a&...&username=18953675221
  pwd            = 7fa8282ad93047a4d6fe6111c93b308a
  username       = 18953675221
[响应体] {"returncode":2040007,"message":"账号或密码错误"}
```
注：课件测试账号已失效（响应"账号或密码错误"），不影响加密分析；密文与课件一致。

`02_验证MD5.py` 输出：
```
[明文] 1111111
[本地复算 MD5] 7fa8282ad93047a4d6fe6111c93b308a
[Charles 抓包 pwd] 7fa8282ad93047a4d6fe6111c93b308a
[课件标准结果]    7fa8282ad93047a4d6fe6111c93b308a
[结论] 三者一致 -> 登录密码加密 = 标准 MD5(32位小写hex)，验证通过
```

## 实操要点与踩坑记录
- 车智赢 3.42.0 首次启动出现强制升级弹窗且无法关闭：断网启动绕过
  （`svc wifi disable` → force-stop → 重新打开）；最终用户手动更新到 5.6.1。
- 软键盘弹出会压缩布局导致 UI 坐标漂移（登录按钮从 (540,1100) 移到 (540,581)）：
  tap 前需重新 dump 界面取坐标，或按键盘弹出状态使用对应坐标。
- Charles 手动导出会话不可靠（Swing 对话框 + SendKeys 路径注入失败），
  改用 Auto Save 工具：charles.config 的 `<autoSave>` 条目配置
  `toolEnabled=true / enableOnStartup=true / savePeriod=1 / savePath=...`，
  每 1 分钟自动落盘 .chls。
- `.chls` 是 xstream 二进制序列化，URL/请求体等字符串未压缩，可直接按 UTF-8 检索提取。
- 屏幕休眠时 `adb shell input tap` 无效：先 `keyevent 224` 唤醒再操作。
- 版本差异观察：5.6.1 的 `loginByPassword` 多了 `.signType(1)`，
  请求体因此额外出现 `_sign` 参数（由 `HttpUtil.checkParams` → `mParamsInterceptor.checkParams`
  注入，具体算法未在本案例展开），课件 3.42.0 无此参数。

## 声明
仅限学习研究，禁止商用。脚本只复算课件公开的测试数据，不做批量采集，结果数据不入库。
