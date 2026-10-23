/*
 * 仅限学习研究，禁止商用
 * 真实得物 4.74.5：Hook newSign 的 Java 入口
 *   com.shizhuang.duapp.common.utils.RequestUtils.c(java.util.Map, long)
 * 课件踩坑：直接打印 Map 会显示 [object Object]，
 * 必须 Java.cast 成 HashMap 再遍历 entrySet。
 */

function ts() {
    var d = new Date();
    function p(n) { return n < 10 ? "0" + n : "" + n; }
    return p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds());
}

function log(msg) {
    console.log("[" + ts() + "] " + msg);
}

Java.perform(function () {
    var RequestUtils = Java.use("com.shizhuang.duapp.common.utils.RequestUtils");

    RequestUtils.c.overload("java.util.Map", "long").implementation = function (map, ts) {
        log("---- RequestUtils.c 命中 ----");
        try {
            // 课件踩坑：直接 console.log(map) 只会得到 [object Object]，
            // 这里用 keySet().toArray() 逐个取值，比 cast + entrySet 更稳。
            var keys = map.keySet().toArray();
            var pairs = [];
            for (var i = 0; i < keys.length; i++) {
                var k = "" + keys[i];
                pairs.push(k + "=" + map.get(keys[i]));
            }
            log("参数个数 = " + keys.length);
            log("参数 = " + pairs.join("&"));
        } catch (e) {
            log("遍历 Map 失败: " + e);
        }
        log("timestamp 实参 = " + ts);
        var sign = this.c(map, ts);
        log("newSign = " + sign);
        return sign;
    };
    log("Hook 就绪：RequestUtils.c(Map, long)");
});
