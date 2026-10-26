# 司小宝 HMAC-SHA1 签名与 RSA 十六进制双层加密

> 本目录所有代码仅限学习研究，禁止商用。登录链路全部打在本地 mock 服务端，未使用真实账号访问线上站点。

## 一、案例目标

复刻 day24 司小宝（`cmt.chinaway.com.lite` v4.0.9）的登录加密链路，并复现课件里的 ptrace 占坑反调试与两种绕过方式：

1. `sign`：`quote_plus(base64(HMAC-SHA1(key, "POST\n{ts}\n/inside.php")))`
2. `mobile` / `password`：`hex_upper(base64(RSA/ECB/PKCS1Padding(明文)))`
3. ptrace 占坑：App 起一个同名子进程先占住主进程，frida 附加上不去
4. 绕过：`kill -9` 占坑进程 / `spawn` 抢跑

## 二、课件结论（读课件后整理）

| 项目 | 结论 |
| --- | --- |
| 接口 | `https://g7s.ucenter.huoyunren.com/inside.php`，POST |
| 固定 query | `t=json`、`m=mobileinfo`、`f=driverLogin`、`app=1`、`ua=android`、`appclientversion=4.0.9`、`referer=d507c00281c733bd693e5049ea33ad7e` |
| 签名 key | `1KMrg0dfufc0wpnXEJacEQX1YEUYA0Ja`（hook `q.p0` 拿到） |
| 签名消息 | `POST\n{13 位毫秒时间戳}\n/inside.php` |
| 课件真值 | ts=`1694450485059` → `5VnGRNih2xWwXIF3QeuAYdD7j%2F4%3D` |
| 账密加密 | 1024 位 RSA 公钥，PKCS1 v1.5，base64 后再逐字节转大写 hex（课件的 `c()`） |
| 反调试 | 双进程 + ptrace 占坑；直接附加报 `system restrictions`，运行中的 frida-agent 会被打崩 |

## 三、实现思路

线上服务端私钥不可得，因此：

- **签名密钥保持课件原值**，并先用课件 hook 出来的真值做自检，保证算法逐位一致；
- **RSA 用本地生成的 1024 位密钥对**（位数与课件公钥一致），服务端持私钥解密，客户端从 `/__mock/pubkey` 取公钥——验证的是"客户端加密方式"，不涉及线上密钥。

```
01_sign_login.py ──POST /inside.php──> mock_server.py（127.0.0.1:8018）
       │                                     │ 校验 sign / 时间戳 / referer
       └─ RSA 加密 mobile+password            └─ RSA 私钥解密 → 比对本地假账号
02_ptrace_occupy.py / 03_spawn_attach.py ──frida──> 真机司小宝（只做附加测试，不登录）
```

## 四、运行方式

```powershell
python mock_server.py 8018

# 四组用例：正常登录 / 密码错误 / 篡改签名 / 过期时间戳
python 01_sign_login.py --out evidence_01_sign_login.log

# 真机 ptrace 占坑与 spawn 绕过（需先启动 App 并同意隐私协议）
python 02_ptrace_occupy.py --out evidence_02_ptrace.log
python 03_spawn_attach.py  --out evidence_03_spawn.log
```

依赖：`requests`、`pycryptodome`、`frida`（设备上需先起 hluda/frida-server）。

## 五、实测结果

### 1) 加密链路（本地 mock）

```
== 1. 签名算法自检 ==
ts=1694450485059 期望=5VnGRNih2xWwXIF3QeuAYdD7j%2F4%3D 计算=5VnGRNih2xWwXIF3QeuAYdD7j%2F4%3D -> 一致
密钥位数=1024
mobile 密文长度=344（hex）  password 密文长度=344
== 3. 正常登录 ==  {'code': 0, 'msg': 'ok', 'data': {'token': '74985d73...', 'uid': 10086}}
== 4. 密码错误 ==  {'code': 1001, 'msg': '用户名或密码错误'}
== 5. 篡改签名 ==  {'code': 1002, 'msg': '签名错误'}
== 6. 过期时间戳 == {'code': 1003, 'msg': '时间戳过期'}
结论：PASS 四组用例全部符合预期
```

证据：[evidence/01_sign_login.txt](evidence/01_sign_login.txt)

### 2) ptrace 占坑（真机 Android 11）

```
pid=29330 ppid=18487 name=cmt.chinaway.com.lite      # 主进程
pid=29374 ppid=29330 name=cmt.chinaway.com.lite      # 占坑子进程
附加结果=失败 ProcessNotFoundError: process not found
kill -9 29374 -> 剩余进程：无
主进程 29330 随 tracer 一起退出，符合 ptrace 语义
结论：PASS ptrace 占坑复现（双进程 + 附加被拒）
```

证据：[evidence/02_ptrace.txt](evidence/02_ptrace.txt)

### 3) spawn 抢跑绕过

```
spawn pid=29056
消息：{'type': 'send', 'payload': {'tag': 'hook', 'msg': 'loaded classes = 15874'}}
6 秒后进程：'29056 29103'
结论：PASS spawn 抢跑注入成功
```

证据：[evidence/03_spawn.txt](evidence/03_spawn.txt)

## 六、文件说明

| 文件 | 作用 |
| --- | --- |
| `mock_server.py` | 本地 mock：HMAC 验签、时间戳窗口、RSA 解密、假账号校验 |
| `01_sign_login.py` | 签名自检 + RSA/hex 加密 + 四组用例 |
| `02_ptrace_occupy.py` | 复现双进程占坑、附加被拒、kill tracer 的连带退出 |
| `03_spawn_attach.py` | spawn 抢跑注入验证 |
| `evidence/` | 运行日志（.txt 规避仓库 `*.log` 忽略规则） |

> `mock_rsa_private.pem` / `mock_rsa_public.pem` 由服务端首次启动时本地生成，属于测试密钥，不入库。

## 七、结论

- 司小宝的签名是**标准 HMAC-SHA1 + base64 + urlencode**，消息体只有 method/时间戳/path 三段，重放窗口由服务端时间戳控制。
- 账密是**非对称加密**而非哈希：客户端只拿公钥，抓包只能拿到密文，必须调用 App 或公钥加密才能构造请求。
- 反调试用 ptrace 占坑，特点是"tracer 死则 tracee 死"，所以 `kill -9` 占坑进程会让 App 一起退出；课件推荐的 **spawn 抢跑**才是稳定方案，实测注入后 hook 消息正常返回、进程存活。
