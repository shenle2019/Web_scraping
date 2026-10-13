// hook_scripts/hook_cookie.js
// ================================================================
// Hook Cookie（重写增强版）—— 拦截 document.cookie 的所有写入
// 与课件版差异（我的实现思路）：
//   1. 透传原生 setter（不自己维护 _cookie 存储，页面既有行为零破坏）
//   2. 记录完整调用栈 new Error().stack —— 直接定位"谁写了 cookie"
//   3. 全量留痕到 window.__hookCookie，供自动化脚本读取
// ================================================================
(function () {
    var desc = Object.getOwnPropertyDescriptor(Document.prototype, "cookie")
            || Object.getOwnPropertyDescriptor(HTMLDocument.prototype, "cookie");
    if (!desc || !desc.set) {
        console.log("[hook-cookie] 未找到原生 cookie 描述符，注入失败");
        return;
    }
    var rawSet = desc.set;
    var rawGet = desc.get;
    var records = [];
    window.__hookCookie = records;

    Object.defineProperty(document, "cookie", {
        configurable: true,
        get: function () {
            return rawGet.call(document);
        },
        set: function (val) {
            try {
                var stack = (new Error()).stack || "(no stack)";
                records.push({ value: String(val), stack: stack, time: Date.now() });
                console.log("[hook-cookie] 捕获写入 #" + records.length + ": " + String(val));
                console.log("[hook-cookie] 调用栈:\n" + stack.split("\n").slice(0, 5).join("\n"));
            } catch (e) { /* 拦截过程绝不破坏页面 */ }
            return rawSet.call(document, val);
        }
    });

    console.log("[hook-cookie] 注入完成（等待页面写 cookie）");
})();
