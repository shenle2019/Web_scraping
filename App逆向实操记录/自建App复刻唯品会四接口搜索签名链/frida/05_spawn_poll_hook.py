# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
05_spawn_poll_hook.py —— spawn 后轮询重试 hook KeyInfo.getNavInfo（冷启动握手取证）
"""
import frida
import subprocess
import sys
import time

pkg = "com.achievo.vipshop"
subprocess.getoutput(f"adb shell pm clear {pkg}")   # 清数据 => 强制冷启动注册握手
subprocess.getoutput(f"adb shell am force-stop {pkg}")

rdev = frida.get_usb_device(timeout=10)
pid = rdev.spawn([pkg])
session = rdev.attach(pid)

scr = r"""
rpc.exports.tryHook = function () {
    try {
        var KeyInfo = Java.use("com.vip.vcsp.KeyInfo");
        KeyInfo.getNavInfo.implementation = function (ctx, str) {
            console.log("-----------------");
            console.log("参数==>", str);
            var res = this.getNavInfo(ctx, str);
            console.log("返回的值==>", res);
            return res;
        };
        return "HOOK_OK";
    } catch (e) {
        return "NOT_YET: " + e;
    }
};
"""
messages = []
script = session.create_script(scr)


def on_message(message, data):
    messages.append(str(message))
    print(message)


script.on("message", on_message)
script.load()
rdev.resume(pid)

# 每 2 秒重试 hook，直到成功或超时
hooked = False
for i in range(30):
    time.sleep(2)
    r = script.exports_sync.try_hook()
    print(f"[第{(i+1)*2}秒]", r)
    if r == "HOOK_OK":
        print(f"[第{(i+1)*2}秒] hook 安装成功")
        hooked = True
        break

if not hooked:
    print("60 秒内未 hook 成功")

# 继续观察 40 秒进程存活与消息
for i in range(20):
    time.sleep(2)
    out = subprocess.getoutput(f'adb shell "ps -A | grep {pkg}"')
    if pkg not in out:
        print(f"[第{i*2}秒] 进程消失 -> 已被反调试击杀")
        break
else:
    print("[观察结束] 进程仍存活")
print("hook 消息条数:", len(messages))
