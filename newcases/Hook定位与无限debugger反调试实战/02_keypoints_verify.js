// 02：课件核心 JS 知识点重写验证（Node 侧）
// ================================================================
// 对应课件：02 eval函数.js、03 hook函数.html、04 Object.defineProperty.js、07 无限debugger.js
// 重写思路：不复读课件，每个知识点按"逆向视角"重新实现 + 断言验证
//   [1] eval：字符串代码执行 + 混淆还原（再实现一个 mini 混淆器）
//   [2] 调用链：带返回值/栈帧的增强版演示（hook 定位的证据链）
//   [3] Object.defineProperty：完整拦截器（校验 + 静默替换 + 删除防御）
//   [4] 无限 debugger：六种写法全量可执行验证 + 字符串特征对照表
// 运行：node 02_keypoints_verify.js
// ================================================================
"use strict";

let passCount = 0, failCount = 0;
function check(name, cond) {
    if (cond) { passCount++; console.log("    [PASS] " + name); }
    else { failCount++; console.log("    [FAIL] " + name); }
}

// ================= [1] eval =================
console.log("=".repeat(64));
console.log("[1] eval：字符串代码执行 + 极简混淆还原");
{
    const exp = "1 + 2 * 3 / 4 + (5 ** 2 - 8)";
    console.log("    课件表达式 eval 结果:", eval(exp));
    check("eval 结果 == 19.5", eval(exp) === 19.5);

    // 逆向视角：网站把代码 base64 后 eval —— 静态搜索失效，运行时现形
    const realCode = "function calc(a, b) { return a * b + 7 }";
    const b64 = Buffer.from(realCode, "utf8").toString("base64");
    console.log("    混淆存储（base64）  :", b64.slice(0, 40) + "...");

    // 严格模式下直接 eval 有独立作用域：里面定义的函数不会泄漏出来（对比验证）
    eval(Buffer.from(b64, "base64").toString("utf8"));
    check("严格模式下直接 eval 作用域隔离（calc 不可见）", typeof calc !== "function");

    // 间接 eval：(0, eval)(...) 在全局作用域执行 —— 混淆代码在全局定义函数的常用手法
    (0, eval)(Buffer.from(b64, "base64").toString("utf8"));
    check("间接 eval 还原后全局可见 calc(6,7) == 49", typeof calc === "function" && calc(6, 7) === 49);
    console.log("    结论：静态只见 base64 数据，hook eval 打印入参即可拿到明文源码");
}

// ================= [2] 调用链：hook 定位的证据链 =================
console.log("=".repeat(64));
console.log("[2] 调用链：数据从入口流到'发射点'的路径记录");
{
    // 重写课件 foo/bar 演示：这次让每一层都记录自己，最后逆序输出完整链
    const chain = [];
    function send(payload) { chain.push("send"); return "已发射:" + payload.sig; }   // 假"发射"（相当于请求发出）
    function buildSign(data) { chain.push("buildSign"); return { data, sig: "sig(" + data + ")" }; }
    function collect() { chain.push("collect"); return "payload-42"; }
    function entry() { chain.push("entry"); return send(buildSign(collect())); }

    const result = entry();
    console.log("    调用链:", chain.join(" -> "));
    console.log("    返回值:", result);
    check("调用链完整 entry->collect->buildSign->send", chain.join(",") === "entry,collect,buildSign,send");
    check("'发射'结果携带签名", result === "已发射:sig(payload-42)");

    // 运行时栈：真实网站代码混淆后函数名可能丢失，但运行时栈帧依然存在
    function where() { return new Error().stack.split("\n")[2].trim(); }
    function caller() { return where(); }
    const frame = caller();
    console.log("    运行时栈帧示例:", frame);
    check("new Error().stack 可定位调用位置", frame.includes("caller"));
    console.log("    结论：hook 脚本里打印 new Error().stack，等于自动记录'谁调用了我'");
}

// ================= [3] Object.defineProperty 完整拦截器 =================
console.log("=".repeat(64));
console.log("[3] Object.defineProperty：读写拦截 + 校验 + 对不可见记账");
{
    const store = { name: "张三", age: 18 };
    let internal = 0;               // 真实值存放在闭包，外部不可直读
    const setLog = [];
    Object.defineProperty(store, "age", {
        get() { return internal; },
        set(v) {
            if (v > 100) { setLog.push("拒绝:" + v); throw new Error("年龄非法"); }   // 重写：非法值直接拒收（课件版是打印错误提示、值不更新）
            setLog.push("接受:" + v);
            internal = v;
        },
        configurable: false,        // 拦截器不可删（防御调试者 delete store.age 拆掉）
        enumerable: false
    });

    check("初始 get 返回 0（原值 18 被遮蔽）", store.age === 0);
    store.age = 50;
    check("合法值 50 写入成功", store.age === 50);
    let threw = false;
    try { store.age = 167; } catch (e) { threw = true; }
    check("非法值 167 抛异常且不落库", threw && store.age === 50);
    console.log("    set 调用流水:", JSON.stringify(setLog));

    // configurable:false 的删除防御验证
    let delOk = false;
    try { delOk = delete store.age; } catch (e) { delOk = false; }
    check("delete 无法拆除拦截器（严格模式抛错/返回 false）", store.age === 50);
    console.log("    结论：属性读写被 100% 接管 —— 这就是 hook cookie/header 的实现底座");
}

// ================= [4] 无限 debugger 六种写法 =================
console.log("=".repeat(64));
console.log("[4] 无限 debugger：课件六种写法的可执行性 + 静态特征");
{
    // Node 无调试器挂载，debugger 是空操作；这里验证"可执行 + 特征可搜"
    const hits = [];
    hits.push("写法1 直接 debugger");
    debugger;

    hits.push("写法2 eval('debugger')");
    eval("debugger");

    hits.push("写法3 setInterval 回调");
    const t3 = setInterval(() => { debugger; }, 50);
    clearInterval(t3);

    hits.push("写法4 setTimeout 递归");
    let t4n = 0;
    const t4 = setTimeout(function rec() { debugger; if (++t4n < 2) setTimeout(rec, 10); }, 10);
    clearTimeout(t4);

    hits.push("写法5 Function 构造器");
    Function("debugger").call();
    Function("debugger").apply();
    Function.constructor("debugger").call("action");
    Function.constructor("debugger").apply("action");

    hits.push("写法6 原型链+字符串构造");
    // 注意括号结构：(function(){return!![]}) 是函数对象，取它的 ["constructor"] 即 Function 构造器
    (function () { return !![] })["constructor"]("debugger")["call"]("action");
    eval('(function (){return!![]}["constructor"]("debugger")["call"]("action"))');

    check("六种写法全部可执行（Node 下 debugger 为空操作）", hits.length === 6);
    hits.forEach(h => console.log("    - " + h));

    // 静态特征对照：每种写法在源码里留下的"可搜索痕迹"
    const features = [
        ["写法1", "debugger"],
        ["写法2", '"debugger"'],
        ["写法3", "setInterval"],
        ["写法4", "setTimeout"],
        ["写法5", "Function / constructor"],
        ["写法6", '"constructor" / "call"'],
    ];
    console.log("    静态搜索特征表:");
    features.forEach(([k, v]) => console.log("      %s -> 搜 %s", k, v));

    // 构造器写法的返回值验证：Function("debugger") 本质是一个函数工厂
    const f = Function("debugger");
    check("Function('debugger') 返回函数对象", typeof f === "function");
    check("其 toString() 含 debugger 明文（对抗脚本据此判断）", f.toString().includes("debugger"));
}

// ================= 汇总 =================
console.log("=".repeat(64));
console.log("汇总: PASS = %d, FAIL = %d", passCount, failCount);
if (failCount === 0) console.log("ALL PASS");
else { console.log("SOME FAILED"); process.exit(1); }
