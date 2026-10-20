# Android 随机看图 App 与登录联调（day09 实操复刻）

> 仅限学习研究，禁止商用。仓库不包含任何真实用户数据；案例使用的宝宝写真属于私人素材，已从代码库中排除，只保留处理脚本与图标生成脚本。

对照 `day09-安卓基础01` 课件的四段内容落地：

1. Java 常见加密概念（字节数组、UUID、随机值、时间戳、十六进制、MD5、Base64）——概念对照，不重复造轮子；
2. 安卓开发环境（Android Studio + SDK + Gradle + 真机）；
3. 第一个 App「点击按钮切换美女」——改造成随机不重复的「沈嘉杭呀」写真 App；
4. 登录案例（Android 表单 + HttpURLConnection + Flask 后端）——做成独立的联调 Demo，并补上课件的「显示网络图片」环节。

## 目录结构

```
Android随机看图App与登录联调/
├── app-shenjiahang/          主 App「沈嘉杭呀」（源码，不含私人照片）
│   ├── app/src/main/java/com/shenjiahang/babyalbum/MainActivity.java
│   ├── app/src/main/res/layout/activity_main.xml
│   ├── app/src/main/res/drawable*/  (渐变、胶囊、卡片描边、心形、图标前景)
│   ├── app/src/main/res/mipmap-*/   (PIL 生成的各密度桌面图标)
│   ├── tools/
│   │   ├── prepare_photos.py 素材处理：EXIF 校正 → 居中裁 3:4 → 1080×1440
│   │   └── make_icon.py      PIL 程序化生成自适应图标
│   └── ...
├── app-logindemo/            登录联调 Demo（HttpURLConnection + 网络图片）
├── server/app.py             Flask：/login、/ping、/photo
├── evidence/                 真实运行证据（构建日志、logcat、Flask 日志、截图、反编译产物）
└── docs/
    ├── 01-案例评测结果.md
    ├── 02-jadx差异对照.md
    └── 03-踩坑记录.md
```

## 一、工具安装与版本核对

| 环境 | 工具 | 版本 / 路径 | 状态 |
| --- | --- | --- | --- |
| PC | Android Studio | 2022.2.1（build AI-222.4459.24.2221.10121639），`D:\Android` | 已安装，与课件软件目录的安装包同版本 |
| PC | Android SDK Platform | android-33（另存 30/36） | 已安装 |
| PC | Build-Tools | 30.0.3 | 已安装 |
| PC | adb / platform-tools | 1.0.41（`D:\soft\platform-tools`） | 可用 |
| PC | Gradle | 8.0（wrapper 发行包已缓存） | 离线构建可用 |
| PC | JDK | 系统 1.8.0_371；AS 内置 JBR 17.0.6 | Gradle 8.0 用 JBR 17 启动 |
| PC | jadx | 1.4.7 CLI（`D:\soft\jadx-cli\bin\jadx.bat`） | 反编译成功 |
| PC | Python / Flask / Pillow | 3.8.8 / 3.0.3 / 10.4.0 | Flask 服务与图标脚本可用 |
| 手机 | Pixel 2（walleye） | Android 11，API 30，1080×1920 @420dpi | `adb devices` 在线 |
| 手机 | 主 App | `com.shenjiahang.babyalbum` v1.0 | 已安装并运行 |
| 手机 | 登录 Demo | `com.shenjiahang.logindemo` v1.0 | 已安装并运行 |

关于“不要更新 APK”：
day09 的 `软件/` 目录只有一个 `android-studio-2022.2.1.20-windows.exe`，没有附带任何第三方 APK。本次手机端只安装了两个自己构建的调试包，**没有安装、也没有更新任何第三方 App**，因此不涉及“断网登录绕过更新”的操作。后续若替换成带更新的目标 App，按“断网 → 登录 → 切到登录页 → 再联网”的顺序操作即可。

## 二、主 App「沈嘉杭呀」具体做了什么

### 1. 素材流水线（tools/prepare_photos.py）

原始照片来自私人目录，脚本只做三件事：

- 读取 EXIF 方向并校正（避免竖拍照片显示成横躺）；
- 居中裁剪成 3:4，缩放到 1080×1440，JPEG 质量 86；
- 输出到 `res/drawable-nodpi/photo_01.jpg … photo_11.jpg`，并生成清单 `photos_manifest.json`（原文件名、字节数、MD5）。

11 张处理完合计约 2.1 MB。`--placeholders` 参数可以在没有私人照片时生成纯色占位图，保证工程可直接编译。

### 2. 图标（tools/make_icon.py）

ImageGen 额度不足（返回 code 112），改用 PIL 程序化绘制，好处是可复现、无版权风险：

- 奶油粉渐变底 + 倾斜拍立得相框 + 抽象宝宝头像 + 心形/星芒点缀；
- 拆成“透明前景 motif + 渐变背景”两部分，符合 Android 8.0+ 自适应图标规范；
- 输出 `mipmap-mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi/ic_launcher.png` 与 `drawable-nodpi/ic_launcher_foreground.png`；
- `mipmap-anydpi-v26/ic_launcher.xml` 组合前景与 `bg_icon.xml` 渐变背景。

### 3. 随机逻辑：洗牌袋，不重复

直接用 `Random.nextInt()` 会连续抽到同一张，观感差。改成“洗牌袋”：

```java
private int nextIndex() {
    if (bag.isEmpty()) {
        for (int i = 0; i < PHOTOS.length; i++) bag.add(i);
        Collections.shuffle(bag, random);
        // 新一轮的第一张不要和上一轮最后一张相同
        if (bag.size() > 1 && bag.get(0) == current) {
            Collections.swap(bag, 0, bag.size() - 1);
        }
    }
    return bag.remove(0);
}
```

这样 11 张图一轮内必定各出现一次，跨轮也不会连着重复。

### 4. 切换动效

- 卡片先淡出并缩到 0.97（120 ms），换图后淡入回 1.0（260 ms，Decelerate）；
- 每次换图重置 `ImageView` 缩放，再启动 9 秒 1.0 → 1.05 的线性推镜（Ken Burns），静态照片有缓慢呼吸感；
- 计数胶囊 `10 / 11` 换数字时做 0.9 → 1.0 的弹一下；
- 按钮点击有 0.96 回弹 + `performHapticFeedback(1)` 震动反馈；
- 进入页面时卡片 `alpha 0 → 1`、`translationY 22dp → 0`，520 ms 入场。

### 5. 界面（activity_main.xml）

- 背景：`bg_window.xml` 垂直渐变（奶油白 → 浅粉），叠两个大半径光晕 View 做柔焦；
- 标题：serif 28sp「沈嘉杭呀」，副标题「宝宝写真 · 随机一刻」；
- 卡片：MaterialCardView，3:4 比例、26dp 圆角、12dp 阴影、1dp 白色描边，内部 ImageView `centerCrop`；
- 卡片底部叠一层渐变遮罩 + 白色小字「沈嘉杭呀 · 宝宝写真」；
- 右上角计数胶囊 `bg_chip.xml`，底部渐变胶囊按钮 `bg_button.xml`（心形 drawableStart、minWidth 220dp）；
- 状态栏奶油色 + 深色图标，导航栏浅粉，整体竖屏锁定。

### 6. 构建

```powershell
$env:JAVA_HOME="D:\Android\jbr"
C:\Users\Administrator\.gradle\wrapper\dists\gradle-8.0-bin\ca5e32bp14vu59qr306oxotwh\gradle-8.0\bin\gradle.bat `
  -p .\app-shenjiahang assembleDebug --offline --no-daemon --console=plain
```

结果：`BUILD SUCCESSFUL in 28s`，APK 7,284,880 字节，MD5 `5C3905661145E59C1682745803792848`。

## 三、登录联调 Demo（可选附录）

> 本次要求以图片 App 为主，登录案例不作为必做项。这部分是实现图片 App 时顺带跑通的联调验证，代码与证据保留在仓库里，供参考，不影响主 App 的结论。

### 1. Flask 端（server/app.py）

- `POST /login`：读取 `application/x-www-form-urlencoded` 的 `username/password`；`justin/123` 返回 `{"code":100,"msg":"登录成功","token":...}`，其余返回 `{"code":101,"msg":"用户名或密码错误"}`；token 每次启动随机生成；
- `GET /ping`：连通性探针；
- `GET /photo`：用 Pillow 动态画一张 720×960 渐变图返回，专门验证课件的“显示网络图片”；
- 中文 Windows 主机名下 `socket.getfqdn` 会按 GBK 解码抛 `UnicodeDecodeError`，启动前替换成带兜底的版本。

### 2. Android 端（LoginActivity.java）

- 原生 `HttpURLConnection`，POST 表单，连接/读取超时各 8 秒；
- 网络请求在子线程，结果通过 `Handler(Looper.getMainLooper())` 切回主线程更新 UI；
- 界面上两个按钮分别提交正确密码和固定错误密码，直接对照 `code=100 / code=101`；
- 第三个按钮从 `/photo` 下载图片，`BitmapFactory.decodeStream` 解码后显示，同时把尺寸和耗时写进结果框与 logcat；
- `AndroidManifest.xml` 声明 `INTERNET`，并设置 `android:usesCleartextTraffic="true"` 允许明文 HTTP（仅调试用）。

### 3. 真机连本机服务

```powershell
adb reverse tcp:8080 tcp:8080
```

手机访问 `http://127.0.0.1:8080` 即电脑的 Flask。这一步比让手机连局域网 IP 更稳，不受代理和防火墙影响。

## 四、真实评测结果（摘要）

主 App 是本次交付重点；登录 Demo 的结果作为附录一并列出。完整表格见 [docs/01-案例评测结果.md](docs/01-案例评测结果.md)。

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| 主 App 构建 | 成功，28 s，7.28 MB | `evidence/build_app.log` |
| 主 App 权限 | 0 个 uses-permission | `evidence/apk_badging.txt` |
| 主 App 冷启动 | 552 / 556 / 589 ms（首次 576 ms） | 本文档实测记录 |
| 换图交互 | 10/11 → 7/11（按钮）→ 9/11（点卡片） | 真机点击 + 截图（含私人照片，未入库） |
| 登录 Demo 构建 | 成功，12 s，25,042 字节 | `evidence/build_logindemo.log` |
| 正确密码 | HTTP 200，`code=100`，41 ms | `evidence/logcat_login.txt`、`evidence/shot_login_ok.png` |
| 错误密码 | HTTP 200，`code=101`，40 ms | `evidence/logcat_login.txt`、`evidence/shot_login_wrong.png` |
| 网络图片 | 720×960，67 ms，Flask 记录 `GET /photo 200` | `evidence/logcat_photo.txt`、`evidence/shot_network_photo.png` |
| jadx 反编译 | 739 个类，`MainActivity` 142 行 | `evidence/jadx_MainActivity.java` |
| 服务端 UA 记录 | `Dalvik/2.1.0 (Linux; U; Android 11; Pixel 2 ...)` | `evidence/flask_first_run.err.log` |

## 五、jadx 对照结论（摘要）

详细对照见 [docs/02-jadx差异对照.md](docs/02-jadx差异对照.md)。七类可稳定观察到的差异：

1. 多 dex 标注 `/* loaded from: classes3.dex */`；
2. lambda 脱糖为 `$$ExternalSyntheticLambdaN`，方法名被改写成 `m30lambda$onCreate$1$comshenjiahangbabyalbumMainActivity`；
3. 常量内联：`performHapticFeedback(1)`、`setDuration(520L)`、`9000L`；
4. 可变参数变成 `new Object[]{Integer.valueOf(...)}`；
5. 泛型擦除：`new ArrayList()`、`new Object[]{...}`；
6. 非法 Java 标识符被重命名，并留下 `reason: not valid java name`；
7. 继承链注解展开为 `@Override // androidx.fragment.app.FragmentActivity, ...`，源码里的 `AppCompatActivity` 继承关系被完整暴露。

## 六、隐私与合规

- 宝宝写真属于私人素材，**没有**进入代码库；`.gitignore` 明确排除 `photo_*.jpg`；
- 主 App 的真机截图包含照片，同样没有入库；入库的只有登录 Demo 的截图（纯 UI）；
- Flask 的 token 是每次启动随机生成的本地演示值，不连接任何外部服务；
- 未安装、未更新任何第三方 APK，未对任何线上服务发起请求；
- 所有脚本仅用于本地学习联调，禁止商用。

## 七、复现步骤

```powershell
# 以下命令都在记录根目录执行；gradle 完整路径见上文构建一节

# 1. 准备素材（没有私人照片时用占位图）
cd app-shenjiahang
python tools\prepare_photos.py --src "D:\你的照片目录" --out app\src\main\res\drawable-nodpi
python tools\prepare_photos.py --placeholders --out app\src\main\res\drawable-nodpi

# 2. 生成图标（直接写入 res/mipmap-* 与 drawable-nodpi）
python tools\make_icon.py

# 3. 复制 local.properties（sdk.dir 指向本机 SDK）
copy local.properties.example local.properties

# 4. 构建并安装主 App
$env:JAVA_HOME="D:\Android\jbr"
C:\Users\Administrator\.gradle\wrapper\dists\gradle-8.0-bin\ca5e32bp14vu59qr306oxotwh\gradle-8.0\bin\gradle.bat -p . assembleDebug --offline
adb install -r app\build\outputs\apk\debug\app-debug.apk

# 5. 起后端；另一台机器上构建并安装登录 Demo
cd ..
python server\app.py
adb reverse tcp:8080 tcp:8080
cd app-logindemo
copy local.properties.example local.properties
C:\Users\Administrator\.gradle\wrapper\dists\gradle-8.0-bin\ca5e32bp14vu59qr306oxotwh\gradle-8.0\bin\gradle.bat -p . assembleDebug --offline
adb install -r app\build\outputs\apk\debug\app-debug.apk
```
