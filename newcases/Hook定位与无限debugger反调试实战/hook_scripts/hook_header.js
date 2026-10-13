// hook_scripts/hook_header.js
// ================================================================
// Hook Header（重写增强版）—— 拦截 XHR / fetch 的请求头设置
// 与课件版差异（我的实现思路）：
//   1. 同时覆盖 XMLHttpRequest.prototype.setRequestHeader 与 window.fetch
//      （现代站点两条路都可能走，只 hook 一条会漏）
//   2. 记录完整调用栈 —— 直接定位签名头生成函数
//   3. 全量留痕到 window.__hookHeader，供自动化脚本读取
//   4. apply/原始引用透传，功能零破坏
// ================================================================
(function () {
    var records = [];
    window.__hookHeader = records;

    function record(type, name, value, stack) {
        records.push({ type: type, name: String(name), value: String(value), stack: stack, time: Date.now() });
        console.log("[hook-header] " + type + " set: " + name + " = " + value);
        console.log("[hook-header] 调用栈:\n" + String(stack).split("\n").slice(0, 5).join("\n"));
    }

    // ---- 通路1：XMLHttpRequest ----
    var rawSetHeader = XMLHttpRequest.prototype.setRequestHeader;
    XMLHttpRequest.prototype.setRequestHeader = function (name, value) {
        try { record("XHR", name, value, (new Error()).stack); } catch (e) {}
        return rawSetHeader.apply(this, arguments);
    };

    // ---- 通路2：fetch ----
    if (typeof window.fetch === "function") {
        var rawFetch = window.fetch;
        window.fetch = function (input, init) {
            try {
                var headers = (init && init.headers) ||
                    (input && typeof input === "object" && input.headers);
                if (headers) {
                    if (typeof Headers !== "undefined" && headers instanceof Headers) {
                        headers.forEach(function (v, k) { record("fetch", k, v, (new Error()).stack); });
                    } else if (Array.isArray(headers)) {
                        headers.forEach(function (kv) { record("fetch", kv[0], kv[1], (new Error()).stack); });
                    } else {
                        Object.keys(headers).forEach(function (k) { record("fetch", k, headers[k], (new Error()).stack); });
                    }
                }
            } catch (e) {}
            return rawFetch.apply(this, arguments);
        };
    }

    console.log("[hook-header] 注入完成（XHR + fetch 双通路）");
})();
