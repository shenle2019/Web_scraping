# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
08_auto_hook_search.py —— 一体化取证：attach 三件套 hook + 脚本内自动触发搜索
用法（输出直接重定向存档）：
  python 08_auto_hook_search.py > evidence/hook_final.log 2>&1
"""
import frida
import subprocess
import sys
import time

pkg = "com.achievo.vipshop"

pids = subprocess.getoutput(f"adb shell pidof {pkg}").split()
if not pids:
    print("app 未运行")
    sys.exit(1)
rdev = frida.get_usb_device(timeout=10)
session = rdev.attach(int(pids[0]))
print("attach ok, pid=", pids[0], flush=True)

scr = r"""
Java.perform(function () {
    var KeyInfo = Java.use("com.vip.vcsp.KeyInfo");
    var TreeMap = Java.use('java.util.TreeMap');

    KeyInfo.getNavInfo.implementation = function (ctx, str) {
        console.log("[getNavInfo] 参数==>", str);
        var res = this.getNavInfo(ctx, str);
        console.log("[getNavInfo] 返回==>", res);
        return res;
    };

    KeyInfo.gsNav.implementation = function (ctx, map, str, z10) {
        var s = Java.cast(map, TreeMap).toString();
        if (s.indexOf("keyword") !== -1 || s.indexOf("search") !== -1) {
            console.log("[gsNav*搜索] 参数map==>", s);
            var res = this.gsNav(ctx, map, str, z10);
            console.log("[gsNav*搜索] 返回==>", res);
            return res;
        }
        return this.gsNav(ctx, map, str, z10);
    };

    KeyInfo.esNav.implementation = function (ctx, str, str2, str3, i10) {
        console.log("[esNav] 参数str==>", str);
        var res = this.esNav(ctx, str, str2, str3, i10);
        console.log("[esNav] 返回==>", res);
        return res;
    };
});
"""
script = session.create_script(scr)
script.on("message", lambda m, d: print(m, flush=True))
script.load()
print("hook 已安装，开始自动触发搜索...", flush=True)


def sh(cmd):
    return subprocess.getoutput(cmd)


# 1. 点"全部商品"入口进入结果列表，触发真实搜索请求
sh("adb shell input tap 68 1272")
print("已点全部商品，观察 60 秒...", flush=True)

dead_at = None
for i in range(30):
    time.sleep(2)
    out = sh(f'adb shell "ps -A | grep {pkg}"')
    if pkg not in out:
        dead_at = (i + 1) * 2
        print(f"[第{dead_at}秒] 进程消失 -> 已被反调试击杀", flush=True)
        break

print("== 观察结束：进程 %s ==" % ("存活（删 so 绕过反调试有效）" if dead_at is None
      else "第%d秒被杀" % dead_at), flush=True)
