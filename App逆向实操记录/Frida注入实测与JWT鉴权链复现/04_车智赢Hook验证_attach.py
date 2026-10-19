# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""车智赢 attach 方案 hook 实测（对应课件 2-hook车智赢的密码-attach方案.py）。

做法与课件一致但在两点上做了实测增强：
  1. 先主动调用 encodeMD5("1111111")，不依赖 UI 操作即可验证方法可执行；
     本次实测输出 7fa8282ad93047a4d6fe6111c93b308a，与 day03 抓包密文一致。
  2. 再挂 implementation 等待真实登录触发。

实测结论（2026-10，车智赢 5.6.1 / Pixel 2 XL Android 11）：
  * 主动调用成功，说明 Java 层注入与目标方法定位都正确；
  * 点击登录后 app 主进程崩溃，crash buffer 回溯落在 /memfd:frida-agent-64.so，
    即应用带有 Frida 检测，真实调用路径无法在注入状态下走完。
运行前提：手机已启动 frida-server，app 处于运行状态，adb forward 27042/27043 已建立。
"""
import sys

import frida

HOOK_JS = """
Java.perform(function () {
    var SecurityUtil = Java.use("com.autohome.ahkit.utils.SecurityUtil");
    // 主动调用一次，验证静态方法可执行（不依赖 UI 操作）
    try {
        var active = SecurityUtil.encodeMD5("1111111");
        console.log("[ACTIVE] encodeMD5('1111111') = " + active);
    } catch (e) {
        console.log("[ACTIVE-ERR] " + e);
    }
    // 挂真实调用，捕获登录时的明文与密文
    SecurityUtil.encodeMD5.implementation = function (str) {
        console.log("[HOOK] encodeMD5 input=" + str);
        var res = this.encodeMD5(str);
        console.log("[HOOK] encodeMD5 output=" + res);
        return res;
    };
    console.log("[READY] hook installed");
});
"""


def main():
    rdev = frida.get_remote_device()
    # 车智赢进程名带加号；包名进程受保护，attach 会被拒绝
    for target in ["车智赢+", "com.che168.autotradercloud"]:
        try:
            session = rdev.attach(target)
            script = session.create_script(HOOK_JS)
            script.on("message", lambda msg, data, t=target: (print(t, msg), sys.stdout.flush()))
            script.load()
            print("[ATTACHED] " + target)
            sys.stdout.flush()
        except Exception as exc:
            print("[SKIP] " + target + " -> " + str(exc))
            sys.stdout.flush()

    print("[WAIT] 请手动点击登录按钮，观察 hook 输出；Ctrl+C 退出。")
    sys.stdout.flush()
    try:
        sys.stdin.read()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
