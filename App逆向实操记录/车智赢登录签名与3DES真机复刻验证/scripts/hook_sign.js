// 车智赢复刻 App 的 Hook 脚本：验证登录链路上到底走了哪几个方法
// 用法：python scripts/02_frida_hook.py
Java.perform(function () {
    function log(name, detail) {
        // 用 send() 而不是 console.log()：frida 16 的 console.log 会直吐终端，
        // 不经过 Python 的 on_message 回调，日志落不了盘。
        send(name + " | " + detail);
    }

    var SecurityUtil = Java.use("com.autohome.ahkit.utils.SecurityUtil");
    SecurityUtil.encodeMD5.overload("java.lang.String").implementation = function (s) {
        var r = this.encodeMD5(s);
        log("encodeMD5", "in=" + s + " out=" + r);
        return r;
    };
    SecurityUtil.encode3Des.overload("android.content.Context", "java.lang.String").implementation = function (ctx, plain) {
        var r = this.encode3Des(ctx, plain);
        log("encode3Des", "plain=" + plain + " cipher=" + r);
        return r;
    };

    var AppUtils = Java.use("com.autohome.chezhiying.AppUtils");
    AppUtils.getUDID.overload("android.content.Context").implementation = function (ctx) {
        var r = this.getUDID(ctx);
        log("getUDID", "udid=" + r);
        return r;
    };

    var SignManager = Java.use("com.autohome.chezhiying.SignManager");
    SignManager.signByType.overload("int", "java.util.TreeMap").implementation = function (type, map) {
        var r = this.signByType(type, map);
        log("signByType", "type=" + type + " sign=" + r + " map=" + map);
        return r;
    };

    var AHAPIHelper = Java.use("com.autohome.ahkit.AHAPIHelper");
    AHAPIHelper.getDesKey.overload("android.content.Context").implementation = function (ctx) {
        var r = this.getDesKey(ctx);
        log("getDesKey", "key=" + r);
        return r;
    };

    // 课件里"搜到但登录不走到"的旧签名入口：挂上后应当一次都不打印
    AHAPIHelper.toSign.overload("android.content.Context", "java.util.TreeMap").implementation = function (ctx, map) {
        var r = this.toSign(ctx, map);
        log("toSign-旧入口", "hit! map=" + map);
        return r;
    };

    log("ready", "hooks installed");
});
