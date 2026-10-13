# 抖音 a_bogus 签名黑箱调用与 VM 状态机恢复实战

> 对应课件：《Day27：JS逆向爬虫基础案例08》（抖音 a_bogus 签名 / bdms 补环境 / execjs 联调）
>
> 交付形式：把课件案例**按自己的思路重写一遍**，组装成端到端可复现的实战项目：黑箱调用 bdms 资产产出 a_bogus、VM 状态机复位技术、补环境完整度矩阵实验、自建 mock 站三层校验、翻页采集管线。

## 一、项目思路

课件案例是「残环境 env.js + douyin.js 直调 + execjs 拼装」的最小演示，且直调存在坑（第二次调用返回 undefined）。本项目不逐行复刻，而是把它重构成一条工程化链路，并把「补环境到底补什么才对」做成可量化实验。

| 课件机制 | 对应课件 | 本项目重写思路 |
|---|---|---|
| 签名由 bdms 资产（VM 混淆）计算，算法不可读 | douyin.js | 不逆 VM：黑箱调用 + 声明式 `ENV_PLAN` 补环境（01） |
| 直调 `window.yuan._u` 第二次返回 undefined | 课件坑 | 提出**恢复法**：每次调用前把 VM 状态机复位到首帧快照（02） |
| 残环境（navigator 空对象 / screen 缺 width / 空 document） | env.js | **环境完整度矩阵实验**（04）：单字段组逐项补全，观察签名长度谱系 |
| execjs 驱动 JS 签名 | 联调 | 不依赖 execjs：Node CLI + base64 传 query（规避 Windows 引号坑） |
| 服务端校验 a_bogus | — | 自建 mock 站三层校验：形态护栏 + **复算比对** + replay（10） |

最终链路：**补环境（Node 黑箱调用）→ a_bogus CLI → mock 站三层校验 → 翻页 200 落盘 + 5 组反例全部 406**。

## 二、目录结构

```
抖音a_bogus签名黑箱调用与VM状态机恢复实战/
├── js_asset/
│   └── source.js              bdms 资产（课件复制，537KB，VM 混淆黑箱）
├── 01_env_mini.js             补环境引擎（ENV_PLAN 注册表 + defineProperty 统一注册 + 监控器）
├── 02_sign_engine.js          签名引擎（恢复法 VM 复位 + CLI/库双形态：--query-b64 / --ua / --count）
├── 03_sign_selftest.js        签名自检（课件坑复现 / 形态 5 断言 / 随机位 / 输入与 UA 绑定 / 压测）
├── 04_env_probe_worker.js     环境矩阵实验 worker（单变体一次签名，被 Python 编排调用）
├── 04_env_probe_matrix.py     环境矩阵编排（9 变体 × 独立 Node 进程，规避沙箱 spawn 限制）
├── 10_mock_server.py          本地 mock 站（端口 18990，三层校验 + 翻页数据 + 媒体直链 + --selftest）
├── 20_spider_pipeline.py      端到端管线（翻页 2 页 + 5 组风控反例 + 落盘）
├── 21_video_url_extract.py    视频 URL 提取与真实访问（提取直链 → 访问 → 下载落盘 output/videos/）
├── common.py                  公共辅助（LocalSite / Node 签名桥 / 发送原语）
├── run_log.py                 UTF-8 日志工具（生成 _run_*.txt）
└── _run_*.txt                 各脚本运行日志（作业验证结果，UTF-8）
```

## 三、验证结果汇总（全部通过）

| 脚本 | 验证内容（关键数据） | 结果 | 日志 |
|---|---|---|---|
| 04_env_probe_matrix.py | 9 变体环境矩阵：144(base) / 152(+screen8) / 160(+inner) / 164(full) 谱系；全部含共同段 `xow7zvMIubZsQJI` | 谱系清晰 | _run_04_env_matrix.txt |
| 03_sign_selftest.js | 恢复法 3 连签 164/164/164；形态 5 断言；同进程随机位 20 位；输入绑定 [25,26,40]；UA 绑定 [29,30,43]；20 连签 avg 0.9ms | 8 PASS / 0 FAIL | _run_03_sign_selftest.txt |
| 10_mock_server.py `--selftest` | 白名单探测 18 样本 → 22 位；真签名通过 / 篡改稳定位拒 / 乱串拒 / 残环境 144 拒 / 重放拒 / 翻页新签名通过 | 6 PASS | _run_10_mock_selftest.txt |
| 20_spider_pipeline.py | 翻页 200 + 6 条 × 2 页（游标 / has_more / ID 无重复）落盘；无签名 / 乱串 / 篡改 / 重放全部 406；健康检查 | 14 PASS / 0 FAIL | _run_20_pipeline.txt |
| 21_video_url_extract.py | 两页 12 条提取 48 条直链（play×24 / download×12 / cover×12）；48 次真实访问全部 200（累计 ~1.2MB）；12 个 mp4 下载落盘 output/videos/ | 5 PASS / 0 FAIL | _run_21_video_urls.txt |

## 四、复现方式

```powershell
# 依赖：Python 3.8+、Node 18+、requests

# 1) 签名引擎自检（Node：补环境 + 恢复法）
node 03_sign_selftest.js

# 2) 补环境完整度矩阵实验（9 变体 × 独立进程）
python 04_env_probe_matrix.py

# 3) mock 站三层校验自测
python 10_mock_server.py --selftest

# 4) 端到端管线（自动启停 mock 站；翻页 + 反例）
python 20_spider_pipeline.py

# 5) 视频 URL 提取与真实访问下载（产出 output/video_urls.txt 等记录）
python 21_video_url_extract.py

# 生成 UTF-8 验证日志（或直接查看已有 _run_*.txt）
python run_log.py 20_pipeline.txt -- python -X utf8 20_spider_pipeline.py

# 人工浏览：python 10_mock_server.py  ->  http://127.0.0.1:18990/
```

## 五、关键技术说明

- **补环境完整度决定签名形态（本项目矩阵实测）**：残环境签名 144 字符；单补屏幕组（screen.width/pixelDepth）→ 152；单补视口组（innerWidth/innerHeight/outerWidth/outerHeight/devicePixelRatio）→ 160；全部补全 → 164。navigator / document / location / localStorage / Buffer 单独补删**不改变形态**。所有形态共享同一主体段，证明同源 bdms 模板，长度差异来自环境字段分支。
- **Node 24 navigator 是 getter-only accessor（本项目最大暗坑）**：`globalThis.navigator` 只有 getter、可配置，普通赋值**静默失败**——课件式 `navigator = {...}` 从未生效，签名采集到的始终是 Node 原生值（platform="Win32"、UA 尾部 "Node.js/24"）。修复 = 全部环境字段统一 `Object.defineProperty` 注册。此坑曾让实验矩阵得出错误结论（base 140 vs 144），修复后谱系重排。
- **VM 状态机复位（恢复法）**：bdms 直调第一次成功、第二次返回 undefined（内部状态已推进）。工程解 = 模块加载时对 `window.yuan` 取首帧快照，每次签名前 `window.yuan = SEED` 复位——单次 ~1ms，20 连签 18ms，为高频签名铺路。
- **进程级副本位与白名单探测策略**：30 进程实验测得跨进程摆动位全集 22 位 = [0-15, 44, 45, 50, 51, 160, 161]。其中 44/45/50/161 取值空间仅 4 种（像进程级 2bit 变量副本）、低变率——**3 进程探测会漏采 pos44**（曾致 mock 用例误拒），改为 12 独立进程 + 同进程 6 样本两两 diff 取并集后稳定覆盖。
- **mock 站三层校验的近似与局限**：① 形态护栏（len==164 / idx16-17=="5-" / 末位"=" / 字符集）；② 复算比对——用「请求 query（剥除 a_bogus）+ 请求头 UA」调 02 引擎复算，差异位必须 ⊆ 随机位白名单（实测同输入复算差异只有随机位）；③ replay 防护（一次性凭证语义）。局限：黑箱条件下服务端不能真实验签，复算等价于「能算出同样的签名」，这正是真实站密钥壁垒所在。
- **视频 URL 提取与下载演练（本地自造闭环）**：mock 数据的 video 字段复刻真实 API 形态（play_addr ×2 / download_addr / cover），直链指向 mock 站自身的 /video 与 /cover 路由（确定性伪随机字节，同一 URL 恒定产出）；21 管线完成「提取 → 逐条真实访问 → 主链字节下载落盘」闭环，48 次访问全 200、12 个 mp4 入库 output/videos/，全程不涉及任何真实站点与真实视频。
- **中文 Windows + Python 3.8 的 http.server 坑**：默认 `server_bind` 调 `socket.getfqdn(host)`，中文主机名经 gethostbyaddr 返回 GBK 字节 → `UnicodeDecodeError` → 服务绑定前崩溃。修复 = 覆写 `server_bind` 绕过 getfqdn（改用 IP 作 server_name）。
- **沙箱 spawn 限制的工程绕行**：Node `child_process.spawn` 在此环境不可用（`AssignProcessToJobObject: (50)`），环境矩阵改为「JS worker + Python subprocess 编排」双文件结构，顺带获得「每变体一个全新 Node 进程」的隔离保证。
- **CLI 工程细节**：query 用 base64 传参（规避 Windows 引号转义）；`-X utf8` + `PYTHONIOENCODING` 对齐中文编码。

## 六、合规声明

本项目所有请求只发往**本地模拟站**（`127.0.0.1:18990`），页面、接口、演示数据、视频/封面媒体字节全部自造（确定性伪随机生成）；bdms 资产仅用于本地离线计算（不发起任何真实站点请求）；课程资产与验证数据仅用于逆向技术学习与课件作业验证，采集输出目录 `output/`（含下载的视频字节）不入库。
