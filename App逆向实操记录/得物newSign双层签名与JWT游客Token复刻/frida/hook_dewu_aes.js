/*
 * 仅限学习研究，禁止商用
 * 真实得物 4.74.5：把 newSign 的三段链路一次抓全
 *   1) com.duapp.aesjni.AESEncrypt.encode        —— Java 层入口（明文）
 *   2) libJNIEncrypt.so 的 AES_128_ECB_PKCS5Padding_Encrypt —— native 层（明文/key/密文）
 *   3) com.shizhuang.duapp.common.utils.RequestUtils.a(String) —— MD5（密文 -> newSign）
 */

function ts() {
    var d = new Date();
    function p(n) { return n < 10 ? "0" + n : "" + n; }
    return p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds());
}

function log(tag, msg) {
    console.log("[" + ts() + "][" + tag + "] " + msg);
}

Java.perform(function () {
    try {
        var AESEncrypt = Java.use("com.duapp.aesjni.AESEncrypt");
        AESEncrypt.encode.overload("java.lang.Object", "java.lang.String").implementation = function (obj, str) {
            log("AESEncrypt", "明文 = " + str);
            var out = this.encode(obj, str);
            log("AESEncrypt", "密文 = " + out);
            return out;
        };
        log("AESEncrypt", "Hook 就绪");
    } catch (e) {
        log("AESEncrypt", "Hook 失败: " + e);
    }

    try {
        var RequestUtils = Java.use("com.shizhuang.duapp.common.utils.RequestUtils");
        RequestUtils.a.overload("java.lang.String").implementation = function (str) {
            var out = this.a(str);
            log("MD5", "输入 = " + str);
            log("MD5", "newSign = " + out);
            return out;
        };
        log("MD5", "Hook 就绪");
    } catch (e) {
        log("MD5", "Hook 失败: " + e);
    }

    var attached = false;
    function hookNative(round) {
        if (attached) {
            return;
        }
        var addr = Module.findExportByName("libJNIEncrypt.so", "AES_128_ECB_PKCS5Padding_Encrypt");
        if (addr === null) {
            setTimeout(function () { hookNative(round + 1); }, 300);
            return;
        }
        attached = true;
        log("native", "命中导出函数 @" + addr + "（第 " + round + " 次轮询）");
        Interceptor.attach(addr, {
            onEnter: function (args) {
                try {
                    log("native", "明文 = " + args[0].readUtf8String());
                    log("native", "key  = " + args[1].readUtf8String());
                } catch (e) {
                    log("native", "读参数失败: " + e);
                }
            },
            onLeave: function (retval) {
                try {
                    log("native", "密文(Base64) = " + retval.readUtf8String());
                } catch (e) {
                    log("native", "读返回值失败: " + e);
                }
            }
        });
    }
    setTimeout(function () { hookNative(1); }, 300);
});
