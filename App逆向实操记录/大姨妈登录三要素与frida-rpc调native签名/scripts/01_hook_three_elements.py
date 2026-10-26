# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

大姨妈 v8.6.0 登录三要素取证脚本（root 检测绕过 + device / password / sign 全 hook）

背景：
  手机已 root（Magisk），app 冷启动会走 MiscUtil.isRooted()/isSimulator()，
  命中后弹“手机不安全”强制退出；另外启动时会弹更新弹窗挡住登录页。
  处理方式：断网启动（svc wifi disable / svc data disable）绕更新弹窗，
  再用本脚本 hook 掉 root/模拟器检测。

hook 点（都在 app 自己的代码里，算法不硬跟）：
  1) com.yoloho.libcore.util.MiscUtil.isRooted / isSimulator  -> false
     com.mobile.auth.gatewayauth.manager.SystemManager.checkEnvSafe -> null
  2) device：PeriodAPIV2.setDeviceCode 内置标志位，配合
     java.security.MessageDigest.update 抓 sha1 的拼接明文，并读 getDeviceCode()
  3) password：com.yoloho.libcore.util.AESUtil.encrypt(str, key, iv)
  4) sign：com.yoloho.libcore.util.Crypt.encrypt_data(j2, str, j3)  -> native

用法：
  python 01_hook_three_elements.py spawn 900     # 冷启动并 hook（先断网）
  python 01_hook_three_elements.py attach 600    # app 已停在登录页时直接 attach
"""
import sys
import time

import frida

PKG = "com.yoloho.dayima"

SCR = """
Java.perform(function () {
    // ---------- 1. root / 模拟器检测绕过 ----------
    var MiscUtil = Java.use("com.yoloho.libcore.util.MiscUtil");
    MiscUtil.isRooted.implementation = function () { return false; };
    MiscUtil.isSimulator.implementation = function (ctx) { return false; };
    try {
        var SystemManager = Java.use("com.mobile.auth.gatewayauth.manager.SystemManager");
        SystemManager.checkEnvSafe.implementation = function () { return null; };
    } catch (e) {}

    // ---------- 2. device ----------
    var PeriodAPIV2 = Java.use("com.yoloho.controller.api.PeriodAPIV2");
    var inSetDeviceCode = false;
    PeriodAPIV2.setDeviceCode.implementation = function () {
        inSetDeviceCode = true;
        console.log('[device] >>> setDeviceCode 被调用');
        var r = this.setDeviceCode();
        inSetDeviceCode = false;
        console.log('[device] deviceCode = ' + this.getDeviceCode());
        return r;
    };
    var MessageDigest = Java.use("java.security.MessageDigest");
    var ByteString = Java.use("com.android.okhttp.okio.ByteString");
    MessageDigest.update.overload("[B").implementation = function (data) {
        if (inSetDeviceCode) {
            console.log('[device] sha1 明文 ==> ' + ByteString.of(data).utf8());
        }
        return this.update(data);
    };

    // ---------- 3. password ----------
    try {
        var AESUtil = Java.use("com.yoloho.libcore.util.AESUtil");
        AESUtil.encrypt.implementation = function (str, str2, str3) {
            var res = this.encrypt(str, str2, str3);
            console.log('[password] 明文=' + str + ' key=' + str2 + ' iv=' + str3 +
                        ' 密文=' + res);
            return res;
        };
    } catch (e) { console.log('[password] hook 失败: ' + e); }

    // ---------- 4. sign ----------
    try {
        var Crypt = Java.use("com.yoloho.libcore.util.Crypt");
        Crypt.encrypt_data.implementation = function (j2, str, j3) {
            var res = this.encrypt_data(j2, str, j3);
            console.log('[sign] j2=' + j2 + ' 明文=' + str + ' 长度=' + j3 +
                        ' 结果=' + res);
            return res;
        };
    } catch (e) { console.log('[sign] hook 失败: ' + e); }

    console.log('[hook] 全部 hook 已安装，请点“确定”登录');
});
"""


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "spawn"
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    dev = frida.get_usb_device(timeout=10)

    if mode == "spawn":
        pid = dev.spawn([PKG])
        print("spawn ok, pid =", pid, flush=True)
        session = dev.attach(pid)
        script = session.create_script(SCR)
        script.on("message", lambda msg, data: print(msg, data, flush=True))
        script.load()
        dev.resume(pid)
    else:
        import subprocess
        out = subprocess.getoutput("adb shell pidof %s" % PKG).strip()
        if not out:
            raise SystemExit("app 未运行，先用 spawn 模式")
        pid = int(out.split()[0])
        session = dev.attach(pid)
        print("attach ok, pid =", pid, flush=True)
        script = session.create_script(SCR)
        script.on("message", lambda msg, data: print(msg, data, flush=True))
        script.load()

    print("观察 %d 秒，请在手机上操作登录..." % seconds, flush=True)
    for i in range(seconds // 5):
        time.sleep(5)
        print("...已观察 %d 秒" % ((i + 1) * 5), flush=True)
    print("== 观察结束 ==", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
