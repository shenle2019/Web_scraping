# 安卓双签登录与拦截器 Retrofit 列表

> 仅限学习研究，禁止商用。
> 复刻对象：`day10-安卓开发02`（登录 App + Flask 后端 + 请求签名 + 抓包破解 + 序列化展示热播列表）。

## 做了什么

按课件主线，从零写了一个可运行的 Android App 和配套 Flask 靶场，装到真机上端到端跑通，并用抓包、jadx、Frida 三种手段验证签名链路：

- **App 端**：OkHttp 发登录请求、Gson 反序列化、OkHttp 拦截器统一注入请求头、SharedPreferences 落盘 token、Retrofit 拉取列表、Glide 加载封面、ListView + ViewHolder 展示。
- **后端**：Flask 校验两级签名（请求头 `hsign` + 请求体 `sign`）、`/login` 返回 token、`/films` 做 Bearer token 鉴权、请求日志落盘。
- **逆向验证**：jadx 反编译出签名公式与拦截器特征；Frida hook `okhttp3.internal.http.RealInterceptorChain.proceed` 打印真实请求头与表单体；mitmproxy / Charles 抓包对照。
- **回放脚本**：用 Python 复刻两级签名，跑 9 个正负用例验证服务端每道校验都真实生效。

课件原版是「成功/失败弹 Toast + 静态列表」，本复刻在保持同一主线的同时把签名做成两级（body + header）、加了防重放时间窗和 token 鉴权，更接近真实 App 的风控形态。

## 课件知识点对照

| 课件内容 | 本地复刻实现 |
| --- | --- |
| xml 编写登录页 | `activity_login.xml` + `activity_index.xml` + `item_film.xml` |
| java 编写 Activity | `LoginActivity`、`IndexActivity`、`FilmAdapter` |
| build.gradle 引入第三方库 | okhttp 4.9.1 / gson 2.8.6 / glide 4.11.0 / retrofit 2.9.0 |
| Manifest 允许访问网络 | `android:usesCleartextTraffic="true"` + `INTERNET` 权限 |
| OkHttp 发 POST 表单 | 登录页两条链路：裸 OkHttp 与 Retrofit 各一个按钮 |
| Flask 写登录接口 | `server/app.py` 的 `/login`、`/films`、`/cover/<name>` |
| 请求加密（移动端签名 + 后端校验） | body `sign=md5(t1+user+md5(pwd))`；header `hsign=md5(ctime+SALT)` |
| 模拟抓包破解自己 App | `scripts/replay_sign.py` 复刻签名直接调接口；mitmproxy/Charles 抓真实请求 |
| 序列化 / 反序列化 | Gson 解析 `BaseResp`/`LoginResult`/`FilmResult`/`Film` |
| 登录成功跳新页面显示热播 | `IndexActivity` 拉 `/films`，ListView 展示 10 部电影 + 封面 |

## 环境与工具（本机实测版本）

| 工具 | 版本 / 位置 | 用途 |
| --- | --- | --- |
| JDK | 17.0.20.1（`E:\webspider\Web_scraping\tools\jdk-17.0.20.1+1`） | 构建 App、jadx |
| Gradle | 8.0（wrapper 缓存内） | 构建 |
| AGP | 8.0.2 | 构建 |
| Android SDK | platform 33 / build-tools 30.0.3 | 构建 |
| 真机 | Pixel 2（walleye，Android 11，已 root） | 运行 App |
| Python | 3.8.8 | Flask 靶场、回放脚本、Frida 脚本 |
| Flask | 3.0.3（运行中进程） | 靶场 |
| jadx | 1.4.2 | 反编译 APK |
| Frida | frida 16.3.3 + frida-server 16.3.3（arm64） | hook OkHttp |
| Charles | 5.4.6（8888） | 图形化抓包 |
| mitmproxy | 8.0.0（8890） | 文本化抓包，落 `capture.log` |
| requests | 2.x | 回放脚本 |

手机上额外放置了：`frida-server`（`/data/local/tmp/frida-server`）、Charles 根证书（参考课件流程），以及 `toybox nc` 做链路探测。

## 签名口径

```
请求体（/login）：
  pwd  = md5(明文密码)                          # e10adc3949ba59abbe56e057f20f883e
  sign = md5(t1 + user + pwd)                   # t1 为秒级时间戳
  POST user=justin&pwd=<pwd>&sign=<sign>&t1=<t1>

请求头（所有接口，拦截器统一注入）：
  ctime : 秒级时间戳
  hsign : md5(ctime + "SJH_2026_APP")
  X-Client : netapp/1.0 (okhttp)
  Authorization : Bearer <token>                # 登录成功后自动带上

服务端校验：
  before_request 校验 ctime 合法性 + 与服务端时间偏差 <= 300s + hsign
  /login         校验 t1 合法 + sign
  /films         校验 Bearer token
```

## 目录结构

```
安卓双签登录与拦截器Retrofit列表/
├── README.md
├── 验证记录.md                  # 9 项回放 + 抓包 + Frida + jadx 的原始证据
├── android/                     # 自建 App 源码（16 个 Java 类 + 资源）
│   ├── build.gradle
│   ├── settings.gradle
│   ├── gradle.properties
│   └── app/
│       ├── build.gradle
│       └── src/main/
│           ├── AndroidManifest.xml
│           ├── java/com/shenjiahang/netapp/...
│           └── res/...
├── server/                      # Flask 靶场
│   ├── app.py
│   ├── films.json               # 10 部电影数据
│   ├── make_covers.py           # 纯标准库生成封面 PNG
│   └── requirements.txt
├── scripts/                     # 复刻与验证脚本（均带学习用途声明）
│   ├── replay_sign.py           # Python 复刻双签 + 9 个正负用例
│   ├── capture_dump.py          # mitmproxy 抓包插件
│   ├── hook_okhttp.py           # Frida 注入器
│   └── hook_okhttp.js           # hook RealInterceptorChain.proceed
└── evidence/                    # 验证现场
    ├── capture_evidence.txt     # mitmproxy 抓到的 login/films 原文（token 已脱敏）
    ├── frida_evidence.txt       # hook 到的请求头与 body（token 已脱敏）
    ├── replay_out.txt           # 9 项用例输出
    ├── server_access_evidence.txt  # 服务端请求日志（token 已脱敏）
    ├── prefs_token.xml          # run-as 读到的 token 落盘（token 已脱敏）
    ├── build_evidence.txt
    ├── shot_list.png            # 列表页
    ├── shot_fail.png            # 密码错误提示
    ├── shot_retrofit.png        # Retrofit 链路登录成功
    └── charles_capture.png      # Charles 抓到手机到 8080 的流量
```

## 运行方式

### 1. 启动靶场

```powershell
cd server
pip install -r requirements.txt
python make_covers.py        # 首次生成 10 张封面
python app.py                # 0.0.0.0:8080
```

账号：`justin / 123456`、`alice / 888888`。

### 2. 构建并安装 App

```powershell
$env:JAVA_HOME="E:\webspider\Web_scraping\tools\jdk-17.0.20.1+1"
cd android
& "$env:USERPROFILE\.gradle\wrapper\dists\gradle-8.0-bin\ca5e32bp14vu59qr306oxotwh\gradle-8.0\bin\gradle.bat" assembleDebug --no-daemon
adb install -r app\build\outputs\apk\debug\app-debug.apk
```

先改 `net/NetConfig.java` 里的 `BASE_URL` 为电脑在手机同网段的 IP（本机为 `http://192.168.31.220:8080/`）。

### 3. 复刻签名回放

```powershell
cd scripts
python replay_sign.py                       # 默认打 192.168.31.220:8080
python replay_sign.py --base http://127.0.0.1:8080
```

### 4. Frida hook 真实请求

```powershell
adb shell "cd /data/local/tmp && ./frida-server -l 127.0.0.1:27043 &"
adb forward tcp:27043 tcp:27043
cd scripts
python -u hook_okhttp.py --seconds 30
# 期间在手机上点一次登录
```

### 5. mitmproxy 抓包

```powershell
cd scripts
mitmdump -q -p 8890 -s capture_dump.py --set confdir=./.mitm
# 手机端：adb shell settings put global http_proxy <电脑IP>:8890
# 抓完后恢复：adb shell settings put global http_proxy :0
```

## 验证结果摘要

| 验证项 | 结果 |
| --- | --- |
| 真机安装启动 | 通过（APK 3,218,261 字节） |
| 正确账号登录（OkHttp） | `code=100`，跳转列表页 |
| 密码错误 | `code=101`，登录页日志区提示 |
| Retrofit 登录链路 | HTTP 200，`code=100` |
| token 落盘 | `/data/data/com.shenjiahang.netapp/shared_prefs/sp_token.xml` 可 `run-as` 读出 |
| 列表加载 | `/films` 返回 10 条，ListView + Glide 封面正常 |
| 服务端双签校验 | `[HEADER-OK]` + `[LOGIN]` + `[LOGIN-OK]` + `[FILMS-OK]` 全链路日志 |
| Python 回放 9 项用例 | 通过 9 / 失败 0 |
| jadx 反编译定位 | 命中 `Signer`、`SignInterceptor`、`BASE_URL/SALT` 常量 |
| Frida hook | 打印出真实 `ctime/hsign/Authorization/User-Agent: okhttp/4.9.1` 与表单 body |
| 抓包 | mitmproxy 抓到 `POST /login` 与 `GET /films` 原文；Charles 抓到手机端流量 |

详细输出见 [验证记录.md](验证记录.md)。

## 逆向侧关键发现

- 反编译后签名入口集中在 `com.shenjiahang.netapp.net.Signer`：`bodySign` 与 `headerSign` 两个静态方法，字符串拼接顺序一目了然。
- 请求头的注入不在业务代码里，而在 `SignInterceptor`：`ctime`、`hsign`、`X-Client`、`Authorization` 统一加，业务层只写 URL 和表单。
- `BASE_URL` 与 `SALT` 是 `public static final` 常量，jadx 里直接可读，属于典型「硬编码密钥」反模式。
- Hook 点选 `okhttp3.internal.http.RealInterceptorChain.proceed(Request)`（OkHttp 4.x 包路径），能同时看到 login 与 films 的完整请求。

## 踩坑记录

1. **Flask 启动 UnicodeDecodeError**：Windows 中文主机名导致 werkzeug 调 `socket.getfqdn` 解码失败，在 `app.py` 里打补丁 `socket.getfqdn = lambda name="": "localhost"`。
2. **Frida 旧实例卡死**：手机上有旧 frida-server 占着 27042 但不响应，`kill -9` 无效；改用 `frida-server -l 127.0.0.1:27043` + `adb forward` 走新端口。
3. **OkHttp 4.x 类名迁移**：`okhttp3.RealInterceptorChain` 已移到 `okhttp3.internal.http.RealInterceptorChain`，hook 需要用候选类名列表尝试。
4. **Frida 按包名 attach 挂住**：改为 `adb shell pidof` 取 pid 再 `attach(pid)` 更稳定。
5. **课件自带的 `工具-自动抓包\auto_capture.ps1 -Watch` 计划任务**每 10 秒把手机全局代理强制设回 `电脑IP:8888` 并在 Charles 退出后自动拉起，导致 mitmproxy（8890）一直抓不到包。排查时先 `Disable-ScheduledTask AutoCapture-CharlesProxy`，抓完再 `Enable-ScheduledTask` 恢复。
6. **设备上 `settings put global http_proxy` 需要 App 进程重启才读取**：改代理后要 `force-stop` 再启动 App，否则 OkHttp 仍用旧代理。
7. **Windows 防火墙**：Charles 有历史放行规则，mitmproxy 的 8890 需要单独加入站规则（本次已加 `mitmproxy-8890-in`）。

## 合规声明

- 靶场为本机自建 Flask 服务，账号密码均为本地测试数据；不涉及任何线上站点。
- 抓包与 hook 仅针对自己编写的 App，单机、低频，不绕任何登录墙/付费墙。
- 抓到的 token 均为本地进程随机生成、重启即失效的测试值。
