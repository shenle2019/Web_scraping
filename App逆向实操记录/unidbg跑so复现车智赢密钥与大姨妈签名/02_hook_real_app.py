# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

用车智赢真机 App 交叉验证 unidbg 的结果：直接调用 CheckSignUtil.get3desKey(null)。
只调静态方法拿密钥，不登录、不发请求。

用法：python 02_hook_real_app.py [--out 结果日志]
"""
import argparse
import io
import os
import subprocess
import sys
import time

PKG = "com.che168.autotradercloud"
SCR = """
rpc.exports = {
    key: function () {
        var out = null;
        Java.perform(function () {
            var C = Java.use("com.autohome.ahkit.jni.CheckSignUtil");
            out = C.get3desKey(null);
        });
        return out;
    }
};
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    logs = []

    def log(line):
        line = line if isinstance(line, str) else str(line)
        print(line)
        logs.append(line)

    subprocess.run(["adb", "shell", "am", "force-stop", PKG], capture_output=True)
    import frida
    dev = frida.get_usb_device(timeout=8)
    pid = dev.spawn([PKG])
    log("spawn pid=%s" % pid)
    session = dev.attach(pid)
    script = session.create_script(SCR)
    script.on("message", lambda m, d: log("消息：%s" % m))
    script.load()
    dev.resume(pid)
    key = None
    for i in range(10):
        time.sleep(1)
        try:
            key = script.exports.key()
            if key:
                break
        except Exception as exc:
            log("第%d次调用未就绪：%s" % (i + 1, type(exc).__name__))
    log("真机 get3desKey = %r" % key)
    log("结论：%s" % ("PASS 真机调用成功" if key else "FAIL 真机调用失败"))
    try:
        session.detach()
    except Exception:
        pass
    subprocess.run(["adb", "shell", "am", "force-stop", PKG], capture_output=True)
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(logs) + "\n")
        print("已写入 %s" % os.path.abspath(args.out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
