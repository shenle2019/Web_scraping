/*
 * 仅限学习研究，禁止商用
 * 在真实得物 4.74.5 里定位 newSign 的 Java 入口：
 * 课件里是 WebRequestInterceptor -> RequestUtils.c(hashMap2, currentTimeMillis)
 * 这里先枚举类名/方法，确认混淆后的真实类名与签名
 */

Java.perform(function () {
    var hits = [];
    Java.enumerateLoadedClassesSync().forEach(function (name) {
        if (name.indexOf("RequestUtils") >= 0 || name.indexOf("WebRequestInterceptor") >= 0) {
            hits.push(name);
        }
    });
    console.log("[enumerate] 命中类数 = " + hits.length);
    hits.forEach(function (name) {
        console.log("[class] " + name);
        try {
            var cls = Java.use(name);
            cls.class.getDeclaredMethods().forEach(function (m) {
                console.log("    " + m.toString());
            });
        } catch (e) {
            console.log("    读取方法失败: " + e);
        }
    });
});
