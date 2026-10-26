/*
 * 复刻 day18：hook 拦截器，看四个指纹头怎么进请求。
 * 对应课件 com.bilibili.okretro.f.c.e(builder)
 */
Java.perform(function () {
    var ReportInterceptor = Java.use("com.example.bililike.ReportInterceptor");
    ReportInterceptor.headers.implementation = function (profile) {
        console.log("[headers] Buvid     = " + profile.buvid.value);
        console.log("[headers] Device-ID = " + profile.deviceId.value);
        console.log("[headers] fp_local  = " + profile.fpLocal.value);
        console.log("[headers] fp_remote = " + profile.fpRemote.value);
        console.log("[headers] session_id= " + profile.sessionId.value);
        var map = this.headers(profile);
        console.log("[headers] map=" + map.toString());
        return map;
    };
    console.log("[*] header hook installed");
});
