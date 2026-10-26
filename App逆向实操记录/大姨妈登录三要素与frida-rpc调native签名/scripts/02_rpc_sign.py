# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

frida-rpc 黑箱取 sign：不硬跟 libCrypt.so 的算法，把拼接明文塞回 app 自己的
Crypt.encrypt_data(0, str, len) 执行，直接拿返回的 32 位签名。

前置：app 正在运行（任何页面都行），frida-server 已启动。
用法：python 02_rpc_sign.py "885105cf...e55user/login189****5221vz80nR0HLbmsZ4xP6TX30g=="
"""
import subprocess
import sys

import frida

PKG = "com.yoloho.dayima"

SCR = """
rpc.exports = {
    sign: function (j2, str, j3) {
        var res = null;
        Java.perform(function () {
            var Crypt = Java.use("com.yoloho.libcore.util.Crypt");
            res = Crypt.encrypt_data(j2, str, j3);
        });
        return res;
    }
};
"""


def rpc_sign(plain: str) -> str:
    out = subprocess.getoutput("adb shell pidof %s" % PKG).strip()
    if not out:
        raise SystemExit("app 未运行，先启动大姨妈")
    pid = int(out.split()[0])
    dev = frida.get_usb_device(timeout=10)
    session = dev.attach(pid)
    script = session.create_script(SCR)
    script.on("message", lambda msg, data: print(msg, data, flush=True))
    script.load()
    return script.exports_sync.sign(0, plain, len(plain))


def main():
    if len(sys.argv) < 2:
        raise SystemExit('用法: python 02_rpc_sign.py "拼接明文"')
    plain = sys.argv[1]
    sign = rpc_sign(plain)
    print("明文 =", plain)
    print("长度 =", len(plain))
    print("sign =", sign)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
