# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
02_attach_hook_original.py —— app 正常启动后 attach 延迟 hook getNavInfo（原版取证）
课件 day20 现象："hook 就闪退"，day21 3 用延迟 hook（dlopen 判断 so 后 do_hook）
"""
import frida
import subprocess
import sys
import time

pkg = "com.achievo.vipshop"

# 1. 正常启动 app 并等它进首页
subprocess.getoutput(f"adb shell am force-stop {pkg}")
subprocess.getoutput(f"adb shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
print("app 已启动，等待 15 秒进入首页...")
time.sleep(15)

# 2. attach（按 pid，frida 枚举不到 u0 用户进程名时用 pidof）
pids = subprocess.getoutput(f"adb shell pidof {pkg}").split()
print("pidof 结果:", pids)
if not pids:
    print("进程不存在，app 启动失败")
    sys.exit(1)
rdev = frida.get_usb_device(timeout=10)
proc = rdev.attach(int(pids[0]))
print("attach ok, pid=", pids[0])

scr = """
Java.perform(function () {
    var KeyInfo = Java.use("com.vip.vcsp.KeyInfo");
    KeyInfo.getNavInfo.implementation = function (ctx, str) {
        console.log("-----------------");
        console.log("参数==>", str);
        var res = this.getNavInfo(ctx, str);
        console.log("返回的值==>", res);
        return res;
    }
});
"""
messages = []
script = proc.create_script(scr)


def on_message(message, data):
    messages.append(str(message))
    print(message)


script.on("message", on_message)
script.load()
print("hook 已加载，观察 30 秒（期间可操作 app 触发请求）...")

for i in range(30):
    time.sleep(1)
    out = subprocess.getoutput(f'adb shell "ps -A | grep {pkg}"')
    if pkg not in out:
        print(f"[第{i+1}秒] 进程消失 -> 已被反调试击杀")
        break
else:
    out = subprocess.getoutput(f'adb shell "ps -A | grep {pkg}"')
    print("[30秒后] 进程仍存活:", pkg in out)

print("hook 消息条数:", len(messages))
