# -*- coding: utf-8 -*-
"""仅限学习研究，禁止商用。

大姨妈 v8.6.0 登录链路 PC 复刻（黑箱为主，只把可复算的部分放本地）：

  1) device  ：hook 抓到 sha1 拼接明文，本地 sha1 复算应与 app 的 deviceCode 一致
  2) password：AES-128-CBC/PKCS5，key = md5(手机号)[:16]，iv = yoloho_dayima!%_（固定）
  3) sign    ：拼接 device + "user/login" + 手机号 + 密码密文，
               交给 app 的 native 方法 Crypt.encrypt_data(0, str, len) 算（frida-rpc）
  4) 用同样的 query/body 向 https://uicapi.yoloho.com/user/login 发一次真实请求

账号密码自己传，不写死在脚本里。单次请求，低频学习用途。
用法：python 03_replay_login.py <手机号> <密码> [--out 结果文件]
"""
import base64
import hashlib
import os
import subprocess
import sys
import time

import frida
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ---------- 本机手机实测参数（Pixel 2 / Android 11） ----------
DEVICE = "885105cf0494dd2301b70faf94b0b39d41540e55"
DEVICE_PLAIN = (
    "null437474656aa92b44walleyegooglearm64-v8awalleyeRP1A.201005.004.A1abf"
    "arm873RP1A.201005.004.A1GooglePixel 2walleyerelease-keysuserandroid-build"
    "EE:FA:A8:03:A9:1002:00:00:00:00:00"
)
ANDROID_ID = "437474656aa92b44"
MAC = "EE:FA:A8:03:A9:10"
MODEL = "Pixel 2"
SDKVER = 30
RELEASEVER = 11
SCREEN_W, SCREEN_H = 1080, 1920
DENSITY = "2.625"
BRAND = "google"

LOGIN_URL = "https://uicapi.yoloho.com/user/login"
IV = "yoloho_dayima!%_"
PKG = "com.yoloho.dayima"

RPC_SCR = """
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


def aes_pwd(phone: str, pwd: str):
    key = hashlib.md5(phone.encode()).hexdigest()[:16]
    cipher = AES.new(key.encode(), AES.MODE_CBC, IV.encode())
    return key, base64.b64encode(cipher.encrypt(pad(pwd.encode(), 16))).decode()


def rpc_sign(plain: str) -> str:
    out = subprocess.getoutput("adb shell pidof %s" % PKG).strip()
    if not out:
        raise SystemExit("app 未运行，先启动大姨妈（frida-server 也要在跑）")
    pid = int(out.split()[0])
    dev = frida.get_usb_device(timeout=10)
    session = dev.attach(pid)
    script = session.create_script(RPC_SCR)
    script.load()
    return script.exports_sync.sign(0, plain, len(plain))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_path = None
    if "--out" in sys.argv:
        out_path = sys.argv[sys.argv.index("--out") + 1]
        args = [a for a in args if a != out_path]
    if len(args) < 2:
        raise SystemExit("用法: python 03_replay_login.py <手机号> <密码> [--out 结果文件]")
    phone, pwd = args[0], args[1]

    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    # 1) device 复算
    calc = hashlib.sha1(DEVICE_PLAIN.encode()).hexdigest()
    log("[1] device 明文 = %s" % DEVICE_PLAIN)
    log("    本地 sha1 = %s" % calc)
    log("    app deviceCode = %s  一致: %s" % (DEVICE, calc == DEVICE))

    # 2) 密码 AES
    key, cipher = aes_pwd(phone, pwd)
    log("[2] 密码 key = %s  iv = %s" % (key, IV))
    log("    密码密文 = %s" % cipher)

    # 3) sign 交给 app 的 native 方法
    plain = "%suser/login%s%s" % (DEVICE, phone, cipher)
    sign = rpc_sign(plain)
    log("[3] sign 明文 = %s" % plain)
    log("    sign = %s" % sign)

    # 4) 真实请求
    params = {
        "device": DEVICE, "ver": 860, "screen_width": SCREEN_W,
        "screen_height": SCREEN_H, "model": MODEL, "sdkver": SDKVER,
        "platform": "android", "releasever": RELEASEVER, "channel": 360,
        "latt": 0, "lngt": 0, "networkType": 0, "token": "", "userStatus": 0,
    }
    data = {
        "username": phone, "password": cipher, "sign": sign,
        "androidid": ANDROID_ID, "mac": MAC, "imei": "",
        "density": DENSITY, "brand": BRAND,
    }
    resp = requests.post(
        LOGIN_URL, params=params, data=data, timeout=20,
        headers={"User-Agent": "dayima/8.6.0 (Android 11; Pixel 2)"},
    )
    log("[4] POST %s" % LOGIN_URL)
    log("    HTTP %s" % resp.status_code)
    log("    %s" % resp.text[:2000])

    # 结果落盘
    if out_path:
        with open(out_path, "a", encoding="utf-8") as f:
            f.write("\n===== %s =====\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
            f.write("\n".join(lines) + "\n")
        log("结果已追加到 %s" % os.path.abspath(out_path))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
