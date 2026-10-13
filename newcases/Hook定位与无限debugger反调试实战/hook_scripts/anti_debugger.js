// hook_scripts/anti_debugger.js
// ================================================================
// 无限 debugger 对抗（重写版）—— 思路：源头切断 + 全程留痕
// 对应课件业务场景：网站在 setInterval / setTimeout / Function 构造器 /
// eval 中埋入反复触发的 debugger，拖垮分析节奏。
// 对抗策略（按入口逐一去势）：
//   1. setInterval / setTimeout —— 回调源码含 "debugger" 时替换为空回调
//      （整条定时链掐断，且句柄返回不破坏调用方）
//   2. Function 构造器 —— 源码含 "debugger" 时返回空函数
//      （构造出来的"断点函数"被去势，但调用它的循环本身不断）
//   3. eval —— 源码含 "debugger" 时先剥离再执行
// 所有拦截次数留痕到 window.__antiStats
// 注意：无 DevTools/无 CDP 挂载时 debugger 语句本身是空操作；
//       本脚本的价值在于"防御有调试器场景"并保持页面功能完整。
// ================================================================
(function () {
    var stats = { intervalBlocked: 0, timeoutBlocked: 0, functionBlocked: 0, evalCleaned: 0 };
    window.__antiStats = stats;

    function hasDebugger(fn) {
        try {
            return typeof fn === "function" && fn.toString().indexOf("debugger") !== -1;
        } catch (e) { return false; }
    }

    // ---- 入口1：setInterval ----
    var rawSetInterval = window.setInterval;
    window.setInterval = function (fn, t) {
        if (hasDebugger(fn)) {
            stats.intervalBlocked++;
            console.log("[anti-debug] 掐断 setInterval 中的 debugger 回调（第 " + stats.intervalBlocked + " 次）");
            return rawSetInterval(function () {}, t);   // 空回调替代，句柄照常返回
        }
        return rawSetInterval.apply(this, arguments);
    };

    // ---- 入口2：setTimeout ----
    var rawSetTimeout = window.setTimeout;
    window.setTimeout = function (fn, t) {
        if (hasDebugger(fn)) {
            stats.timeoutBlocked++;
            console.log("[anti-debug] 掐断 setTimeout 中的 debugger 回调（第 " + stats.timeoutBlocked + " 次）");
            return rawSetTimeout(function () {}, t);
        }
        return rawSetTimeout.apply(this, arguments);
    };

    // ---- 入口3：Function 构造器 ----
    var rawFunction = window.Function;
    var WrappedFunction = function () {
        var src = Array.prototype.join.call(arguments, ",");
        if (src.indexOf("debugger") !== -1) {
            stats.functionBlocked++;
            console.log("[anti-debug] 去势 Function 构造器中的 debugger（第 " + stats.functionBlocked + " 次）");
            return rawFunction.call(this, "");           // 返回空函数
        }
        return rawFunction.apply(this, arguments);
    };
    WrappedFunction.prototype = rawFunction.prototype;
    window.Function = WrappedFunction;

    // ---- 入口4：eval ----
    var rawEval = window.eval;
    window.eval = function (code) {
        var s = String(code);
        if (s.indexOf("debugger") !== -1) {
            stats.evalCleaned++;
            s = s.replace(/debugger;?/g, ";");
            console.log("[anti-debug] 剥离 eval 源码中的 debugger（第 " + stats.evalCleaned + " 次）");
        }
        return rawEval.call(this, s);
    };

    console.log("[anti-debug] 对抗脚本已注入（四入口就位）");
})();
