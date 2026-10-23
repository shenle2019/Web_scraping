/*
 * 仅限学习研究，禁止商用
 * 复刻课件里对得物 newSign 的两层 Hook：
 *   1) Java 层：SignUtils.plain / SignUtils.newSign —— 看参与签名的参数与最终签名
 *   2) native 层：libJNIEncrypt.so 的 AES_128_ECB_PKCS5Padding_Encrypt —— 看明文、key、密文
 * 附带：Hook UpdateDialog.show 直接跳过强制更新弹窗（对应课件的绕过思路）
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
    // ---------- 1. 跳过强制更新弹窗 ----------
    try {
        var UpdateDialog = Java.use("com.repl.dewu.update.UpdateDialog");
        UpdateDialog.show.implementation = function (activity, latest) {
            log("UpdateDialog", "命中 show()，服务端要求升级到 " + latest + "，Hook 直接跳过，不弹窗");
        };
        log("UpdateDialog", "Hook 就绪：com.repl.dewu.update.UpdateDialog.show");
    } catch (e) {
        log("UpdateDialog", "Hook 失败: " + e);
    }

    // ---------- 2. Java 层签名 ----------
    try {
        var SignUtils = Java.use("com.repl.dewu.util.SignUtils");
        SignUtils.plain.overload("java.util.Map").implementation = function (map) {
            var out = this.plain(map);
            log("SignUtils.plain", "排序拼接串 = " + out);
            return out;
        };
        SignUtils.newSign.overload("java.util.Map").implementation = function (map) {
            var out = this.newSign(map);
            log("SignUtils.newSign", "newSign = " + out);
            return out;
        };
        log("SignUtils", "Hook 就绪：plain / newSign");
    } catch (e) {
        log("SignUtils", "Hook 失败: " + e);
    }

    // ---------- 3. native 层 AES ----------
    // 注意：libJNIEncrypt.so 是第一次签名时才 dlopen 的，
    // Hook 脚本注入时它还没加载，必须轮询等它出现，否则 findExportByName 返回 null。
    var attached = false;
    function hookNative(round) {
        if (attached) {
            return;
        }
        var addr = Module.findExportByName("libJNIEncrypt.so", "AES_128_ECB_PKCS5Padding_Encrypt");
        if (addr === null) {
            if (round === 1) {
                log("native", "libJNIEncrypt.so 尚未加载，开始轮询等待");
            }
            setTimeout(function () { hookNative(round + 1); }, 300);
            return;
        }
        attached = true;
        log("native", "AES_128_ECB_PKCS5Padding_Encrypt @ " + addr + "（第 " + round + " 次轮询命中）");
        Interceptor.attach(addr, {
            onEnter: function (args) {
                try {
                    var plain = args[0].readUtf8String();
                    var key = args[1].readUtf8String();
                    log("native", "明文 = " + plain);
                    log("native", "key  = " + key);
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
