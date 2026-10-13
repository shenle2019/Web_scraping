// 【本地模拟站】main.js
// ================================================================
// 本文件模拟一个"有风控的真实站点"的完整链路（全部为本地自造数据）：
//   ① 密钥与哈希函数经 base64 混淆，运行时 eval 还原（对应课件 eval 案例）
//   ② 生成访问令牌写入 cookie access_token（对应课件 hook cookie 案例）
//   ③ 数据接口请求携带 X-Sign 签名头（对应课件 hook header 案例）
//   ④ 双链无限 debugger 反调试（对应课件 07 无限debugger 案例）
// ================================================================

(function () {

    // ============ ① 混淆段：eval 还原密钥与哈希函数 ============
    var _blob = "ZnVuY3Rpb24gc2VjSGFzaChzKXt2YXIgaDE9NTM4MSxoMj0xMzE7Zm9yKHZhciBpPTA7aTxzLmxlbmd0aDtpKyspe3ZhciBjPXMuY2hhckNvZGVBdChpKTtoMT0oKGgxPDw1KStoMStjKT4+PjA7aDI9KChoMjw8NCkraDIrYyk+Pj4wO31yZXR1cm4oIjAwMDAwMDAwIitoMS50b1N0cmluZygxNikpLnNsaWNlKC04KSsoIjAwMDAwMDAwIitoMi50b1N0cmluZygxNikpLnNsaWNlKC04KTt9dmFyIFNFQ1JFVF9DPSJoay1kZW1vLWNvb2tpZS1zYWx0LTIwMjYiO3ZhciBTRUNSRVRfUz0iaGstZGVtby1zaWduLXNhbHQtMjAyNiI7";
    eval(atob(_blob));
    // 还原出：secHash(s) / SECRET_C / SECRET_S

    // ============ ② 写入访问令牌 cookie ============
    var day = new Date().toISOString().slice(0, 10);          // UTC yyyy-mm-dd
    var accessToken = secHash("atk|" + day + "|" + SECRET_C);
    document.cookie = "access_token=" + accessToken + "; path=/";
    console.log("[target] access_token 已写入 cookie: " + accessToken);

    // ============ ③ 反调试：两条无限 debugger 链 ============
    window.__dbgTick = 0;

    // 链1：setInterval + 明文 debugger（回调源码里直接含 debugger 关键字）
    setInterval(function () {
        window.__dbgTick++;
        console.log("[target] 链1 setInterval-debugger #" + window.__dbgTick);
        debugger;
    }, 700);

    // 链2：Function 构造器（源码中没有 debugger 明文）+ setTimeout 递归
    // 注意：先构造好匿名的 debugger 函数，递归函数的源码里只出现 _f.call()
    // （日志文案刻意不含 "debugger" 字样，用于验证"掐断构造器、但链本身不断"）
    var _f = Function("debugger");
    (function loop() {
        _f.call();
        window.__dbgTick++;
        console.log("[target] 链2 构造器型断点 #" + window.__dbgTick);
        setTimeout(loop, 800);
    })();

    // ============ ④ 拉取商品数据（携带 X-Sign 签名头） ============
    function fetchGoods() {
        var page = 1;
        var ts = Date.now();
        var sign = secHash("page=" + page + "&ts=" + ts + "|" + SECRET_S);
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/api/goods?page=" + page + "&ts=" + ts);
        xhr.setRequestHeader("X-Sign", sign);
        xhr.onload = function () {
            var statusEl = document.getElementById("status");
            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                var list = document.getElementById("goods-list");
                data.items.forEach(function (it) {
                    var li = document.createElement("li");
                    li.className = "goods-item";
                    li.setAttribute("data-id", String(it.id));
                    li.textContent = it.name;
                    var sp = document.createElement("span");
                    sp.className = "price";
                    sp.textContent = "\u00a5" + it.price;
                    li.appendChild(sp);
                    list.appendChild(li);
                });
                statusEl.textContent = "\u5171 " + data.items.length + " \u6761\u5546\u54c1\uff08\u670d\u52a1\u7aef\u8fd4\u56de\uff09";
            } else {
                statusEl.textContent = "\u62c9\u53d6\u5931\u8d25: HTTP " + xhr.status;
            }
        };
        xhr.onerror = function () {
            document.getElementById("status").textContent = "\u7f51\u7edc\u9519\u8bef";
        };
        xhr.send();
    }

    fetchGoods();

})();
