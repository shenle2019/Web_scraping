# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
01_hook_getnav_original.py —— 原版 APK 直接 hook KeyInfo.getNavInfo 取证反调试
对应课件：day20-唯品会01 代码 2-hook--getNavInfo查看返回值.py（现象：hook 就闪退）
"""
import frida
import sys
import time

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

script = session.create_script(scr)


def on_message(message, data):
    print(message, data)


script.on("message", on_message)
script.load()
rdev.resume(pid)

# 观察 25 秒：反调试 so 会杀掉进程
alive = True
for i in range(25):
    time.sleep(1)
    try:
        rdev.get_process(pkg)
        alive = True
    except frida.ProcessNotFoundError:
        alive = False
        break

print()
print("=" * 40)
print("结论: 进程", "仍存活(未被反调试击杀)" if alive else "已被 libmsaoaidsec.so 反调试击杀(与课件现象一致)")
print("=" * 40)
sys.exit(0)
