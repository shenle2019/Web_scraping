# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
06_full_hook.py —— 删 libmsaoaidsec.so 后 attach 全套 hook（getNavInfo/gsNav/esNav）
对应课件：day20 2-hook-getNavInfo、4-hook-gsNNav；day21 4-hook-esNav
输出存档：_tmp_case/evidence/hook_removed_so.log
"""
import frida
import subprocess
import sys
import time

pkg = "com.achievo.vipshop"
LOG = r"E:\路飞学城\课件\APP逆向(12期)\_tmp_case\evidence\hook_removed_so.log"

# 1. 启动 app（不清数据，正常加载 KeyInfo）
subprocess.getoutput(f"adb shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
print("app 启动，等待 15 秒...")
time.sleep(15)

# 2. attach
pids = subprocess.getoutput(f"adb shell pidof {pkg}").split()
if not pids:
    print("app 未运行")
    sys.exit(1)
rdev = frida.get_usb_device(timeout=10)
session = rdev.attach(int(pids[0]))
print("attach ok, pid=", pids[0])

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
        console.log("[gsNav] 参数map==>", Java.cast(map, TreeMap).toString());
        console.log("[gsNav] 参数str==>", str, " z10==>", z10);
        var res = this.gsNav(ctx, map, str, z10);
        console.log("[gsNav] 返回==>", res);
        return res;
    };

    KeyInfo.esNav.implementation = function (ctx, str, str2, str3, i10) {
        console.log("[esNav] 参数str==>", str);
        console.log("[esNav] str2==>", str2, " str3==>", str3, " i10==>", i10);
        var res = this.esNav(ctx, str, str2, str3, i10);
        console.log("[esNav] 返回==>", res);
        return res;
    };
});
"""
logf = open(LOG, "w", encoding="utf-8")
msg_count = [0]


def on_message(message, data):
    line = str(message)
    msg_count[0] += 1
    print(line[:160])
    logf.write(line + "\n")
    logf.flush()


script = session.create_script(scr)
script.on("message", on_message)
script.load()
print("hook 三件套已安装，观察 120 秒（app 内操作会触发请求）...")

dead_at = None
for i in range(60):
    time.sleep(2)
    out = subprocess.getoutput(f'adb shell "ps -A | grep {pkg}"')
    if pkg not in out:
        dead_at = (i + 1) * 2
        print(f"[第{dead_at}秒] 进程消失 -> 已被反调试击杀")
        break

if dead_at is None:
    print("[120秒后] 进程仍存活（删 so 绕过反调试有效）")
logf.write(f"\n== 观察结束：进程 {'存活' if dead_at is None else '第%d秒被杀' % dead_at}，hook 消息 {msg_count[0]} 条 ==\n")
logf.close()
print("hook 消息条数:", msg_count[0])
print("日志已存:", LOG)
