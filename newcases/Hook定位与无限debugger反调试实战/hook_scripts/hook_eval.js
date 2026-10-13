// hook_scripts/hook_eval.js
// ================================================================
// Hook Eval（重写增强版）—— 让"隐形代码"现形
// 对应课件 01/02 eval 案例的实战化：混淆代码通过 eval/Function/atob
// 在运行时还原，静态搜索搜不到；这三个入口一 hook，明文立刻现形。
// 覆盖三个入口：
//   1. eval          —— 记录源码字符串
//   2. Function 构造器 —— 记录动态构造的函数源码
//   3. atob          —— 记录 base64 解码结果（eval(atob("...")) 的典型组合）
// 全量留痕到 window.__hookEval
// ================================================================
(function () {
    var records = [];
    window.__hookEval = records;

    // ---- 入口1：eval ----
    var rawEval = window.eval;
    window.eval = function (code) {
        try {
            var s = String(code);
            records.push({ type: "eval", code: s, time: Date.now() });
            console.log("[hook-eval] eval 入参（len=" + s.length + "）:\n" +
                s.slice(0, 600) + (s.length > 600 ? "\n...(截断)" : ""));
        } catch (e) {}
        return rawEval.call(this, code);
    };

    // ---- 入口2：Function 构造器（含显式 debugger 构造也会在此现形）----
    var rawFunction = window.Function;
    var WrappedFunction = function () {
        try {
            var src = Array.prototype.slice.call(arguments).join(",");
            records.push({ type: "Function", code: src, time: Date.now() });
            console.log("[hook-eval] Function 构造器源码: " + src.slice(0, 300));
        } catch (e) {}
        return rawFunction.apply(this, arguments);
    };
    WrappedFunction.prototype = rawFunction.prototype;
    window.Function = WrappedFunction;

    // ---- 入口3：atob ----
    var rawAtob = window.atob;
    window.atob = function (s) {
        var decoded = rawAtob.call(window, s);
        try {
            records.push({ type: "atob", code: String(decoded).slice(0, 5000), time: Date.now() });
            console.log("[hook-eval] atob 解码结果（前 300 字）:\n" + String(decoded).slice(0, 300));
        } catch (e) {}
        return decoded;
    };

    console.log("[hook-eval] 注入完成（eval + Function + atob 三入口）");
})();
