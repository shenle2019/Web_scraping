# -*- coding: utf-8 -*-
# 仅限学习研究，禁止商用
"""day05 三个 APP 的 Frida 实时 hook（attach 中文进程名）。

用法：
    python day05_hooks.py --target aiqiu
    python day05_hooks.py --target niaodaifu --out ..\\capture\\尿大夫_hook输出.txt
    python day05_hooks.py --target partner

说明：
- attach 的目标是 APP 的中文进程名（爱安丘 / 尿大夫 / 油联合伙人），
  不是包名；包名 attach 会报 ProcessNotFoundError。
- hook 点与 jadx 反编译结论一一对应：
    aiqiu     : EncryptUtil.getMD5 / EncryptUtil.aesPassword
    niaodaifu : SafeUtils.getSign(long)
    partner   : Md5.md5 / RequestParamsWrapper.sign
- 同时挂 OkHttp RealInterceptorChain.proceed 打印 URL/Headers/Body/Response；
  尿大夫使用其他网络库，该 hook 会 ClassNotFound，属正常现象。
"""
import argparse
import io
import sys
import time
from datetime import datetime

import frida

TARGETS = {
    "aiqiu": "爱安丘",
    "niaodaifu": "尿大夫",
    "partner": "油联合伙人",
}

OKHTTP_JS = """
    try {
        var Chain = Java.use("okhttp3.internal.http.RealInterceptorChain");
        var proceed = Chain.proceed.overload("okhttp3.Request");
        proceed.implementation = function (request) {
            var url = request.url().toString();
            send("[HTTP] " + request.method() + " " + url);
            var headers = request.headers();
            for (var i = 0; i < headers.size(); i++) {
                send("[HDR] " + headers.name(i) + ": " + headers.value(i));
            }
            var body = request.body();
            if (body !== null) {
                try {
                    var ct = String(body.contentType());
                    if (ct.indexOf("multipart") < 0) {
                        var Buffer = Java.use("okio.Buffer");
                        var buffer = Buffer.$new();
                        body.writeTo(buffer);
                        send("[BODY] " + buffer.readUtf8());
                    }
                } catch (e) { send("[BODY-ERR] " + e); }
            }
            var resp = this.proceed(request);
            send("[RESP] " + resp.code() + " " + url);
            try {
                if (url.indexOf("login") >= 0) {
                    send("[RESP-BODY] " + resp.peekBody(1048576).string());
                }
            } catch (e) { send("[RESP-BODY-ERR] " + e); }
            return resp;
        };
        send("[HOOK] OkHttp ok");
    } catch (e) { send("[HOOK-ERR] OkHttp " + e); }
"""

TARGET_JS = {
    "aiqiu": """
    try {
        var EncryptUtil = Java.use("com.iqilu.core.util.EncryptUtil");
        EncryptUtil.getMD5.implementation = function (str) {
            var res = this.getMD5(str);
            send("[GETMD5] in=" + str + " out=" + res);
            return res;
        };
        EncryptUtil.aesPassword.implementation = function (str) {
            var res = this.aesPassword(str);
            send("[AESPWD] in=" + str + " out=" + res);
            return res;
        };
        send("[HOOK] EncryptUtil ok");
    } catch (e) { send("[HOOK-ERR] EncryptUtil " + e); }
""",
    "niaodaifu": """
    try {
        var SafeUtils = Java.use("com.uulife.medical.utils.SafeUtils");
        SafeUtils.getSign.implementation = function (j) {
            var res = this.getSign(j);
            send("[SIGN] time=" + j + " sign=" + res);
            return res;
        };
        send("[HOOK] SafeUtils ok");
    } catch (e) { send("[HOOK-ERR] SafeUtils " + e); }
""",
    "partner": """
    try {
        var Md5 = Java.use("com.yltx.oil.partner.utils.Md5");
        Md5.md5.implementation = function (str) {
            var res = this.md5(str);
            send("[MD5] in=" + str + " out=" + res);
            return res;
        };
        send("[HOOK] Md5 ok");
    } catch (e) { send("[HOOK-ERR] Md5 " + e); }

    try {
        var Wrapper = Java.use("com.yltx.oil.partner.data.network.interceptors.RequestParamsWrapper");
        Wrapper.sign.overload("java.lang.String").implementation = function (str) {
            var res = this.sign(str);
            send("[SIGN] in=" + str + " out=" + res);
            return res;
        };
        send("[HOOK] RequestParamsWrapper.sign ok");
    } catch (e) { send("[HOOK-ERR] sign " + e); }
""",
}


def build_js(target):
    return "Java.perform(function () {" + OKHTTP_JS + TARGET_JS[target] + "});"


def main():
    parser = argparse.ArgumentParser(description="day05 Frida hook（仅限学习研究）")
    parser.add_argument("--target", required=True, choices=sorted(TARGETS))
    parser.add_argument("--out", default=None, help="日志同时写入该文件")
    args = parser.parse_args()

    sink = None
    if args.out:
        sink = io.open(args.out, "w", encoding="utf-8")
        sink.write("# day05 hook 实时日志\n")
        sink.write("# 目标: %s (%s)\n" % (args.target, TARGETS[args.target]))
        sink.write("# 开始: %s\n\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sink.flush()

    def emit(text):
        line = "[%s] %s" % (datetime.now().strftime("%H:%M:%S"), text)
        print(line, flush=True)
        if sink:
            try:
                sink.write(line + "\n")
                sink.flush()
            except Exception as exc:
                print("[SINK-ERR] %s" % exc, flush=True)

    def on_message(message, data):
        if message.get("type") == "send":
            emit(str(message.get("payload")))
        else:
            emit("ERROR " + str(message))

    device = frida.get_remote_device()
    process_name = TARGETS[args.target]
    session = device.attach(process_name)
    script = session.create_script(build_js(args.target))
    script.on("message", on_message)
    script.load()
    emit("[READY] attached %s" % process_name)
    print("现在去手机上点击登录，Ctrl+C 结束。", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        if sink:
            sink.write("\n# 结束: %s\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            sink.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
