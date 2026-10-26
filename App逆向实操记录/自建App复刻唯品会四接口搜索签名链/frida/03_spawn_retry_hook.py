# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
03_spawn_retry_hook.py —— spawn 从启动阶段 hook，KeyInfo 类未加载时自动重试
"""
import frida
import subprocess
import sys
import time

pkg = "com.achievo.vipshop"
subprocess.getoutput(f"adb shell am force-stop {pkg}")

rdev = frida.get_usb_device(timeout=10)
pid = rdev.spawn([pkg])
session = rdev.attach(pid)

scr = r"""
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
script = session.create_script(scr)


def on_message(message, data):
    messages.append(str(message))
    print(message)


script.on("message", on_message)
script.load()
rdev.resume(pid)

# 观察 60 秒，每 2 秒检查进程真实存活
print("观察 60 秒 ...")
dead_at = None
for i in range(30):
    time.sleep(2)
    out = subprocess.getoutput(f'adb shell "ps -A | grep {pkg}"')
    if pkg not in out:
        dead_at = i * 2 + 2
        print(f"[第{dead_at}秒] 进程消失 -> 已被反调试击杀")
        break

if dead_at is None:
    print("[60秒后] 进程仍存活")
print("hook 消息条数:", len(messages))
