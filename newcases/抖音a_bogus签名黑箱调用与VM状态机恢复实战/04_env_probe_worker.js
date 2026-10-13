/**
 * 04_env_probe_worker.js —— 单变体补环境探针（被 04_env_probe_matrix.py 调用）
 * =========================================================
 * 背景：签名长度/主体由"补环境字段完整度"决定（黑箱实测谱系）：
 * 残环境 base → 144；+screen8 → 152；+inner → 160；full → 164。
 * （修复 navigator 的 defineProperty 坑后 base 由 140 变 144——普通赋值
 * 静默失败时 navigator={} 实际从未生效，见 01_env_mini.js 注释。）
 *
 * 本 worker 负责"单个变体的一次签名"；变体矩阵由 Python 编排器
 * （04_env_probe_matrix.py）用 subprocess 隔离调用——保证每个变体一个
 * 全新 Node 进程，环境互不污染。
 *
 * 用法：node 04_env_probe_worker.js <变体名>
 * 变体：base|keepbuf|inner|navi|screen8|doc|loc|storage|full
 * 输出：一行 JSON {"v":..., "len":..., "sig":"..."}
 */

const VARIANT = process.argv[2] || "base";

// 统一测试 query（与 query 内容无关已由观察证明）
const Q = "device_platform=webapp&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=170400&cookie_enabled=true&screen_width=1496&screen_height=967&browser_language=zh-CN&platform=PC&webid=7371422219199055371&msToken=XBPLACEHOLDER";
const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

// 0) undici 物化修复（否则 delete Buffer 后崩溃——两课连发的同款坑）
void globalThis.Headers;

// ★ 关键：Node 24 的 globalThis.navigator 是 getter-only accessor，
// 普通赋值静默失败——所有全局一律用 defineProperty 覆盖。
function setGlobal(name, value) {
    Object.defineProperty(globalThis, name, {
        value: value, writable: true, configurable: true, enumerable: true,
    });
}

// 1) 复刻课件 env.js 残环境（sloppy 隐式赋值，与课件等价）
window = globalThis;
delete globalThis.global;
if (VARIANT !== "keepbuf" && VARIANT !== "full") delete globalThis.Buffer;
setGlobal("requestAnimationFrame", function () {});
setGlobal("XMLHttpRequest", function () {});
setGlobal("navigator", {});
setGlobal("screen", { availHeight: 939, availLeft: 0, availTop: 28, availWidth: 1496, colorDepth: 30, height: 967 });
setGlobal("document", {});

// 2) 按变体逐项补全
const V = (name) => VARIANT === name || VARIANT === "full";
if (V("inner")) {
    setGlobal("innerWidth", 1496); setGlobal("innerHeight", 967);
    setGlobal("outerWidth", 1496); setGlobal("outerHeight", 967);
    setGlobal("devicePixelRatio", 2);
}
if (V("navi")) {
    setGlobal("navigator", {
        appCodeName: "Mozilla", appName: "Netscape",
        appVersion: UA.replace("Mozilla/", ""), userAgent: UA,
        webdriver: false, language: "zh-CN", languages: ["zh-CN", "zh"],
        platform: "MacIntel", hardwareConcurrency: 10, deviceMemory: 8, onLine: true,
    });
}
if (V("screen8")) {
    globalThis.screen.width = 1496;
    globalThis.screen.pixelDepth = 30;
}
if (V("doc")) {
    setGlobal("document", {
        createElement: function (ele) {
            if (ele === "canvas") return { getContext: function () {} };
            return {};
        },
        documentElement: {},
        cookie: "__ac_nonce=0000000000000000000000; ttwid=1%7C0000000000000000000000000000",
    });
}
if (V("loc")) {
    setGlobal("location", {
        href: "https://www.douyin.com/", origin: "https://www.douyin.com",
        protocol: "https:", host: "www.douyin.com", hostname: "www.douyin.com",
        port: "", pathname: "/", search: "", hash: "", ancestorOrigins: {},
    });
}
if (V("storage")) {
    setGlobal("localStorage", { getItem: function () { return null; }, setItem: function () {}, removeItem: function () {} });
    setGlobal("sessionStorage", { getItem: function () { return null; }, setItem: function () {}, removeItem: function () {} });
}

// 3) 挂载 bdms + 一次签名（复刻课件调用形态）
require("./js_asset/source.js");
const r = window.yuan._v;
const sig = (0, window.yuan._u)(r[0], [0, 1, 14, Q, "", UA], r[1], r[2], globalThis);
console.log(JSON.stringify({ v: VARIANT, len: sig ? sig.length : -1, sig: sig || "" }));
