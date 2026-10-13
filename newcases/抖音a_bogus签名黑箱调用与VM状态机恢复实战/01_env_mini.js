/**
 * 01_env_mini.js —— 补环境引擎（Day27 抖音 bdms 版，按自己的思路重写）
 * =========================================================
 * 职责：把 Node 全局环境改造成抖音 bdms（js_asset/source.js）期望的浏览器形态。
 *
 * 与课件 env.js 的差异（重写思路）：
 *   1) 修复优先：先物化 undici 惰性全局——课件 env.js 的 `delete Buffer` 在
 *      Node 20+ 下会在 bdms 初始化时触发 undici 惰性物化（client-h1.js 顶层
 *      Buffer.alloc）而整体崩溃 "Buffer is not defined"（Day26 同款坑）；
 *   2) 默认保留 Buffer：bdms 未检测 Buffer，删除只引入风险；
 *      需要抹特征时 DY_DELETE_BUFFER=1（此时已物化，删除安全）;
 *   3) 环境字段声明式注册（ENV_PLAN 表驱动）；
 *   4) 【实测驱动】按 bdms 真实采集痕迹补全：
 *      - screen 六项（availHeight/availLeft/availTop/availWidth/colorDepth/height）
 *        —— 实测 VM 拼出的指纹串 "0|0|0|0|0|0|0|0|1496|939|0|967|-1|-1|30|0|..."
 *        中 1496/939/967/30 即来自 screen；
 *      - innerWidth/innerHeight —— 实测 VM 查询过 window.innerWidth 且未补时被
 *        拼成 "undefined"；
 *      - navigator.platform = "MacIntel" —— 实测指纹串平台位为 "Win32"（Node
 *        原生 navigator.platform），补上 MacIntel 修正平台一致性；
 *      ★ 重大坑：Node 24 的 globalThis.navigator 是 getter-only accessor，
 *        普通赋值（sloppy 模式）会静默失败——补的 navigator 从未生效，
 *        bdms 采集到的仍是 Node 原生值（Win32 / Node.js/24）。
 *        必须 Object.defineProperty 强制覆盖（见下方统一注册循环）；
 *   5) 访问监控器用闭包工厂实现（替代课件 SetProxy 的 eval 拼字符串），
 *      由 DY_DEBUG 控制：0=关闭（默认，零开销）/ 1=核心对象 / 2=含 window。
 *
 * cookie 说明：默认填入"字段名齐全、值全占位"的演示 cookie（非真实凭证）；
 * 实盘用环境变量 DY_COOKIE 注入抓包 cookie（凭证不入库）。
 *
 * 用法：require("./01_env_mini.js") 即完成补环境（副作用式），
 *       随后 require("./js_asset/source.js") 挂载 bdms 虚拟机。
 */

// ---------- 0. 修复：物化 undici 惰性全局（必须最先执行） ----------
// Node 20+ 把 Headers/Request/Response/FormData/WebSocket 等 Web 全局做成
// "惰性物化"：首次被触及才加载 undici 打包模块链，链上 client-h1.js 顶层
// 执行 Buffer.alloc(0)。若 Buffer 已被删除再触发物化 => ReferenceError 崩溃。
// 这里在 Buffer 完好时主动完成加载（void Headers 一次即带动整条模块链）。
const materializeUndici = () => void globalThis.Headers;
materializeUndici();

// ---------- 1. window / global 桥接 ----------
globalThis.window = globalThis;   // window 指回 Node 全局对象（自引用）
delete globalThis.global;         // 抹掉 Node 特征：探测 "global" 应为未定义

if (process.env.DY_DELETE_BUFFER === "1") {
    delete globalThis.Buffer;     // 默认不删；开关打开时因第 0 步已物化，安全
}

// ---------- 2. 声明式环境注册表 ----------
const UA_PC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

const ENV_PLAN = {
    // 屏幕尺寸（与课件抓包一致：1496x967 / colorDepth 30）
    screen: {
        availHeight: 939,
        availLeft: 0,
        availTop: 28,
        availWidth: 1496,
        colorDepth: 30,
        height: 967,
        width: 1496,
        pixelDepth: 30,
    },
    // 视口尺寸（实测 VM 读取过 window.innerWidth）
    innerWidth: 1496,
    innerHeight: 967,
    outerWidth: 1496,
    outerHeight: 967,
    devicePixelRatio: 2,

    // 文档对象
    document: (function () {
        // 演示 cookie：字段名齐全、值全占位（非任何真实凭证）。
        const PLACEHOLDER_COOKIE = [
            "__ac_nonce=0000000000000000000000",
            "__ac_signature=_02B4Z6wo00f01",
            "ttwid=1%7C0000000000000000000000000000",
            "s_v_web_id=verify_00000000_00000000_0000_0000_0000_000000000000",
            "msToken=0000000000000000000000000000000000000000000000000000000000000000",
            "device_web_cpu_core=10",
            "device_web_memory_size=8",
            "dy_swidth=1496",
            "dy_sheight=967",
        ].join("; ");
        return {
            createElement: function (ele) {
                if (ele === "canvas") return { getContext: function () {} };
                return {};
            },
            documentElement: {},
            cookie: process.env.DY_COOKIE || PLACEHOLDER_COOKIE,
        };
    })(),

    // 浏览器标识
    navigator: {
        appCodeName: "Mozilla",
        appName: "Netscape",
        appVersion: UA_PC.replace("Mozilla/", ""),
        userAgent: UA_PC,
        webdriver: false,
        language: "zh-CN",
        languages: ["zh-CN", "zh"],
        platform: "MacIntel",           // 修正实测发现的 "Win32" 泄漏
        hardwareConcurrency: 10,
        deviceMemory: 8,
        onLine: true,
    },

    // 页面地址（与签名目标站一致）
    location: {
        ancestorOrigins: {},
        href: "https://www.douyin.com/",
        origin: "https://www.douyin.com",
        protocol: "https:",
        host: "www.douyin.com",
        hostname: "www.douyin.com",
        port: "",
        pathname: "/",
        search: "",
        hash: "",
    },

    // 异步调度（课件 env.js 同款：空实现即可，bdms 未依赖其回调结果）
    requestAnimationFrame: function () {},
    cancelAnimationFrame: function () {},
    XMLHttpRequest: function () {},

    // 本地存储 / 扩展
    localStorage: {
        getItem: function () { return null; },
        setItem: function () {},
        removeItem: function () {},
    },
    sessionStorage: {
        getItem: function () { return null; },
        setItem: function () {},
        removeItem: function () {},
    },
    external: {},
};

// 统一用 defineProperty 注册：Node 24 的 navigator 是 getter-only accessor，
// 普通赋值静默失败；defineProperty 对 accessor 与普通属性都可靠生效。
for (const key of Object.keys(ENV_PLAN)) {
    Object.defineProperty(globalThis, key, {
        value: ENV_PLAN[key],
        writable: true,
        configurable: true,
        enumerable: true,
    });
}

// ---------- 3. 访问监控器（可选，闭包工厂版 SetProxy） ----------
const DEBUG_LEVEL = Number(process.env.DY_DEBUG || 0);

function logAccess(name, op, prop, value) {
    if (value !== null && typeof value === "object") return;   // 降噪：对象只看键名
    const shown = typeof value === "string" ? JSON.stringify(value).slice(0, 90) : value;
    console.log(`[env] ${op} ${name}.${String(prop)} = ${shown}`);
}

function makeSpy(name, target) {
    return new Proxy(target, {
        get(t, prop, receiver) {
            logAccess(name, "get", prop, t[prop]);
            return t[prop];
        },
        set(t, prop, value, receiver) {
            logAccess(name, "set", prop, value);
            return Reflect.set(t, prop, value, receiver);
        },
    });
}

if (DEBUG_LEVEL >= 1) {
    for (const key of ["document", "navigator", "location", "screen"]) {
        globalThis[key] = makeSpy(key, globalThis[key]);
    }
}
if (DEBUG_LEVEL >= 2) {
    globalThis.window = makeSpy("window", globalThis.window);  // 深度调试，日志量大
}

// ---------- 4. 诊断导出 ----------
module.exports = {
    materializeUndici: materializeUndici,
    debug: DEBUG_LEVEL,
    defaultUA: UA_PC,
    summary: function () {
        return {
            global_deleted: typeof global === "undefined",
            buffer_alive: typeof Buffer !== "undefined",
            webdriver: globalThis.navigator.webdriver,
            platform: globalThis.navigator.platform,
            ua_tail: String(globalThis.navigator.userAgent).slice(-40),
            screen: { w: globalThis.screen.width, h: globalThis.screen.height, d: globalThis.screen.colorDepth },
            inner: [globalThis.innerWidth, globalThis.innerHeight],
            cookie_source: process.env.DY_COOKIE ? "env:DY_COOKIE" : "placeholder",
            env_keys: Object.keys(ENV_PLAN),
        };
    },
};
