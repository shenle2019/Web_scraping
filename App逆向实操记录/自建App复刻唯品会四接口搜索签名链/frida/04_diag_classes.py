# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
04_diag_classes.py —— 诊断 com.vip.vcsp.KeyInfo 类加载情况
"""
import frida
import subprocess
import sys
import time

pkg = "com.achievo.vipshop"
rdev = frida.get_usb_device(timeout=10)
pids = subprocess.getoutput(f"adb shell pidof {pkg}").split()
if not pids:
    print("app 未运行，先启动")
    subprocess.getoutput(f"adb shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
    time.sleep(12)
    pids = subprocess.getoutput(f"adb shell pidof {pkg}").split()
print("pids:", pids)
session = rdev.attach(int(pids[0]))

scr = r"""
Java.perform(function () {
    var found = [];
    Java.enumerateLoadedClasses({
        onMatch: function (name) {
            if (name.indexOf("com.vip.vcsp") !== -1) {
                found.push(name);
            }
        },
        onComplete: function () {
            console.log("com.vip.vcsp 类数量:", found.length);
            found.forEach(function (n) { console.log("  ", n); });
        }
    });
});
"""
script = session.create_script(scr)
script.on("message", lambda m, d: print(m))
script.load()
time.sleep(8)
