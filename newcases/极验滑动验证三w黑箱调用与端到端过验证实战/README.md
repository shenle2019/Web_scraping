# 极验滑动验证「三 w」黑箱调用 · 端到端过验证实战

> 来源课件：路飞学城《JS 逆向》Day29（第一个 w）、Day30（第二个 w）、Day31（第三个 w）三课整合
> 方案核心：**加密全黑箱**（Node 运行逆向还原后的 JS 生成三个 w），**编排与图像全 Python**（请求串联 / 图片乱序还原 / 缺口测距 / 轨迹生成）
> 验证结果：连续 **4 次端到端验证通过**，均成功拿到 `validate`（见 `output/result.json` 与 `output/run_*.txt`）

---

## 一、案例背景

极验 Demo 站（`www.geetest.com/demo`）滑动验证的完整请求链路上共有 **3 个 w 参数**，每一个都是「自定义Base64(AES-CBC(数据体, aeskey)) + RSA(aeskey)」同一套加密骨架，区别只在数据体：

| w | 触发时机 | 数据体内容 | 生成脚本 |
| --- | --- | --- | --- |
| w1 | 首次 `get.php` | 极验配置对象（fullpage 等） | `js/first_w.js` |
| w2 | 点击「验证」后 `ajax.php` | 点击指纹 13 键 + captcha_token(djb2) + 浏览器指纹 | `js/second_w.js` |
| w3 | 拖动滑块松手后 `ajax.php` | 滑动轨迹（差分编码 + 插字符双层） + userresponse 等 | `js/third_w.js` |

三个 w 共享同一个 aeskey 缓存机制，w1 的 aesKey 会被复用到 w2（本案例按课件行为保持一致）。

## 二、方案设计（按自己思路整合）

```
┌─────────────┐   JSON 参数    ┌──────────────────────┐
│  main.py    │ ──────────────▶│ node js/first_w.js    │──▶ {s, aesKey}
│  (Python)   │   JSON 结果    │ node js/second_w.js   │──▶ {w}
│             │ ◀──────────────│ node js/third_w.js    │──▶ {gt, challenge, w}
└─────┬───────┘                └──────────────────────┘
      │  requests 编排：注册 → gettype → w1 → w2 → get.php#2 → w3 → ajax.php
      │  图像处理：PIL 乱序还原(312→260) → OpenCV Canny+模板匹配测距 → ease_out_expo 轨迹生成
      ▼
  output/result.json（validate）+ 运行日志 + 过程图片
```

- **为什么不纯算**：三个 w 的加密依赖 AES/RSA/自定义Base64/djb2 等一堆算法栈，纯算重写成本高且易错；直接黑箱调用课件还原出的 JS（Node CLI 方式），Python 只管编排与"人类行为数据"（图片/轨迹）的构造；
- **为什么不用 execjs**：改用手写 `subprocess` 调用 Node CLI（`node xxx.js '{json}'`），依赖更少、编码更可控、每个脚本可独立调试；
- **JS 脚本改造**：三个脚本仅在尾部增加统一的 CLI 黑箱入口（`require.main === module` 保护），核心逻辑保持不动。

## 三、目录结构

```
极验滑动验证三w黑箱调用与端到端过验证实战/
├── main.py                 # 全流程编排（8 步）
├── js/
│   ├── first_w.js          # 第一个 w（黑箱入口）
│   ├── second_w.js         # 第二个 w（黑箱入口）
│   ├── third_w.js          # 第三个 w（黑箱入口）
│   ├── package.json        # crypto-js + node-jsencrypt
│   └── node_modules/       # 已在 .gitignore，首次运行需 npm install
├── output/
│   ├── result.json         # 最后一次运行的完整结果（含 validate）
│   ├── run_20261014_165819.txt  # 首次调试运行（遇上 cv2 中文路径坑）
│   ├── run_20261014_165830.txt  # 成功运行 1
│   ├── run_20261014_165837.txt  # 成功运行 2
│   ├── run_20261014_165839.txt  # 成功运行 3
│   ├── run_20261014_165936.txt  # 成功运行 4（result.json 对应本次）
│   └── imgs/               # bg.jpg（乱序）/ slice.jpg / new_bg_img.jpg（还原后）
└── README.md
```

## 四、运行方式

环境要求：Python 3（`requests`、`Pillow`、`numpy`、`opencv-python`）+ Node.js（依赖 `crypto-js`、`node-jsencrypt`）。

```bash
# 首次：安装 JS 依赖（或从任意含相同依赖的目录拷贝 node_modules）
cd js && npm install

# 运行全流程（在案例根目录）
python main.py
```

## 五、流程 8 步

| 步骤 | 数据包 | 关键动作 |
| --- | --- | --- |
| 1 | `register-slide-official` | 拿 gt / challenge |
| 2 | `gettype.php` | 探测核心 js |
| 3 | `get.php`（api.geetest.com） | 黑箱生成 w1 → 请求；返回的 `aesKey` 共享给 w2 |
| 4 | `ajax.php`（api.geevisit.com） | 黑箱生成 w2（点击验证）→ 响应 `result: slide` 表示进入滑块环节 |
| 5 | `get.php`（api.geevisit.com, slide3） | 拿 **new_challenge**（末尾多 2 位）/ `c` / `s` / 图片地址 |
| 6 | 本地处理 | 下载图片 → PIL 按还原顺序数组拼回（312→260）→ OpenCV 测距 → 生成缓动轨迹 |
| 7 | `ajax.php`（api.geevisit.com） | 黑箱生成 w3 → 请求（滑动验证） |
| 8 | 判定 | 响应包含 `validate` 即通过 |

## 六、验证结果（4/4 通过）

| 运行 | distance | 轨迹点 | passtime | 匹配度 | 响应 | validate |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 125 | 46 | 1428ms | 0.5175 | success:1 score:2 | `e0f3ff7ebb83ee4210ad424f7ef7b3ff` |
| 2 | 68 | 31 | 1020ms | 0.2828 | success:1 score:1 | `d794799b9bbead47c17b7e9de306692d` |
| 3 | 97 | 38 | 1248ms | 0.5450 | success:1 score:1 | `26b510be189a5bdab418232167972415` |
| 4 | 155 | 54 | 1691ms | 0.3468 | success:1 score:3 | `f40975491c437633dd13cf879f5500eb` |

注：日志与结果中的 `validate` 为极验服务端签发的单次验证凭证（用完即废，仅供学习记录）。

单轮全流程耗时约 **1.2~1.4s**（其中三次 Node 黑箱调用合计不到 0.3s），`score` 为极验行为评分（正常值）。

## 七、踩坑记录

1. **cv2.imread 在 Windows 下不支持中文路径**：首次运行报 `can't open/read file`（路径被按 ANSI 解码成乱码），改用 `cv2.imdecode(np.fromfile(path), cv2.IMREAD_COLOR)` 从内存解码绕过；
2. **execjs 依赖不可用时**：直接用 `subprocess.run(['node', script, json])` 调用 CLI，注意 `cwd=js/` 让 `require('node-jsencrypt')` 能命中 `js/node_modules`；
3. **c / s 必须动态提取**：来自第二个 `get.php` 响应，每次会话不同，不能写死；
4. **challenge 用对**：w3 全程使用 `get.php#2` 返回的 new_challenge（比原值多 2 位）。

## 八、合规声明

- 目标站点为极验官方 Demo（`www.geetest.com/demo`），仅用于本地学习与逆向技术验证；
- 未针对任何第三方业务系统，未做任何自动化高频请求（全流程单次 8 个请求）；
- 验证产物（validate/日志/图片）仅作学习记录。
