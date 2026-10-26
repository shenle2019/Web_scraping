# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
01b_hook_getnav_check.py —— 修正版取证：用 ps 判定真实存活，记录 hook 输出
"""
import frida
import sys
import time
import subprocess

pkg = "com.achievo.vipshop"
rdev = frida.get_usb_device(timeout=10)
pid = rdev.spawn([pkg])
session = rdev.attach(pid)

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
script = session.create_script(scr)


def on_message(message, data):
    messages.append(str(message))
    print(message)


script.on("message", on_message)
script.load()
rdev.resume(pid)

# 观察 20 秒，用 adb ps 判定真实存活
time.sleep(20)
out = subprocess.getoutput("adb shell \"ps -A | grep vipshop\"")
alive = "com.achievo.vipshop" in out
print()
print("=" * 50)
print("adb ps 结果:")
print(out)
print("=" * 50)
print("真实结论: 进程", "存活" if alive else "已被杀")
print("hook 消息条数:", len(messages))
print("=" * 50)
