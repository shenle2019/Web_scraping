/**
 * 01_env_mini.js —— 补环境引擎（按自己的思路重写版）
 * =========================================================
 * 职责：把 Node 全局环境改造成目标 JSVMP（js_asset/source.js）期望的浏览器形态。
 *
 * 与课件 env.js 的差异（重写思路，5 点）：
 *   1) 修复优先：先物化 undici 惰性全局（Node 20+ 下删除 Buffer 后再触发
 *      undici 物化会因 "Buffer is not defined" 整体崩溃——完整定位见
 *      JS逆向经典案例/Proxy代理与补环境及JSVMP签名还原/学习笔记.md 第六节）；
 *   2) 默认保留 Buffer：本 VM 未检测 Buffer，删除只会引入风险；
 *      需要抹除特征时打开 XHS_DELETE_BUFFER=1（此时物化已完成，删除也安全）；
 *   3) 环境字段声明式注册（ENV_PLAN 表驱动），替代散落的手工赋值；
 *   4) 访问监控器用闭包工厂实现（替代课件 eval 拼字符串方案），
 *      由环境变量 XHS_DEBUG 控制：0=关闭（默认，零开销）/ 1=核心对象 / 2=含 window；
 *   5) 【矩阵实测发现】cookie 字段完整性直接决定签名完整度：
 *      空 cookie → 简化签名（3 字段无 appId，payload 272 hex）；
 *      含 xsecappid 等 9 字段 → 完整签名（4 字段含 appId，payload 384 hex）。
 *      因此 document.cookie 默认填入“结构完整、值全占位”的演示值；
 *      实盘时用环境变量 XHS_COOKIE 注入抓包的真实 cookie（凭证不入库）。
 *
 * 用法：require("./01_env_mini.js") 即完成补环境（副作用式），
 *       随后 require("../js_asset/source.js") 挂载 VM。
 */

// ---------- 0. 修复：物化 undici 惰性全局（必须最先执行） ----------
// Node 20+ 把 Headers/Request/Response/FormData/WebSocket 等 Web 全局做成
// "惰性物化"：首次被触及才加载 undici 打包模块链，而链上 client-h1.js 顶层
// 执行 Buffer.alloc(0)。若 Buffer 已被删除再触发物化 => ReferenceError 崩溃。
// 这里在 Buffer 完好时主动完成加载（void Headers 一次即可带动整条模块链）。
const materializeUndici = () => void globalThis.Headers;
materializeUndici();

// ---------- 1. window / global 桥接 ----------
// 等价于课件的 window = global / delete global / delete Buffer，
// 这里统一用 globalThis 属性写法：不依赖 sloppy 模式，严格模式同样合法。
globalThis.window = globalThis;              // 全局 window 指向 Node 全局对象（自引用）
delete globalThis.global;                    // 抹掉 Node 特征：站点若探测 "global" 应"未定义"

if (process.env.XHS_DELETE_BUFFER === "1") {
    delete globalThis.Buffer; // 默认不删；开关打开时因第 0 步已物化，删除安全
}

// ---------- 2. 声明式环境注册表 ----------
const ENV_PLAN = {
    // 画布 / 媒体（指纹补全）
    CanvasRenderingContext2D: {},
    HTMLCanvasElement: {},
    devicePixelRatio: 2,
    AudioContext: function () {},

    // 文档
    document: (function () {
        // cookie 演示值：9 字段结构完整、值全占位的假 cookie（非任何真实凭证）。
        // 【矩阵实测】cookie 字段完整性决定签名完整度：
        //   空 cookie               → 简化签名：3 字段，payload 272 位 hex
        //   含 xsecappid 等 9 字段   → 完整签名：4 字段（含 appId），payload 384 位 hex
        // 实盘：export XHS_COOKIE="<抓包的真实 cookie>" 注入（保持凭证不入库）。
        const PLACEHOLDER_COOKIE = [
            "abRequestId=00000000-0000-0000-0000-000000000000",
            "a1=0000000000000000000000000000000000000000000000000000",
            "webId=00000000000000000000000000000000",
            "gid=0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "xsecappid=xhs-pc-web",
            "webBuild=4.16.0",
            "unread={%22ub%22:%220000000000000000000000%22%2C%22ue%22:%220000000000000000000000%22%2C%22uc%22:0}",
            "websectiga=0000000000000000000000000000000000000000000000000000000000000000",
            "sec_poison_id=00000000-0000-0000-0000-000000000000",
        ].join("; ");
        return {
            createElement: function (ele) {
                if (ele === "canvas") return { getContext: function () {} };
                if (ele === "div") return {};
                return {};
            },
            documentElement: {},
            cookie: process.env.XHS_COOKIE || PLACEHOLDER_COOKIE,
        };
    })(),

    // 浏览器标识（反自动化检测的关键字段 webdriver）
    navigator: {
        appCodeName: "Mozilla",
        appName: "Netscape",
        appVersion: "5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        webdriver: false,
        language: "zh-CN",
        languages: ["zh-CN", "zh"],
        platform: "MacIntel",
    },

    // 页面地址（与签名目标站保持一致）
    location: {
        ancestorOrigins: {},
        href: "https://www.xiaohongshu.com/explore",
        origin: "https://www.xiaohongshu.com",
        protocol: "https:",
        host: "www.xiaohongshu.com",
        hostname: "www.xiaohongshu.com",
        port: "",
        pathname: "/explore",
        search: "",
        hash: "",
    },

    // 屏幕信息
    screen: { width: 1792, height: 1120, colorDepth: 24, availWidth: 1792, availHeight: 1055 },

    // 扩展信息 / 本地存储
    external: {},
    localStorage: {
        getItem: function () {},
        setItem: function () {},
        removeItem: function () {},
    },
};

for (const key of Object.keys(ENV_PLAN)) {
    globalThis[key] = ENV_PLAN[key];
}

// ---------- 3. 访问监控器（可选，闭包工厂版 SetProxy） ----------
const DEBUG_LEVEL = Number(process.env.XHS_DEBUG || 0);

function logAccess(name, op, prop, value) {
    if (value !== null && typeof value === "object") return;           // 降噪：对象只看键名
    const shown = typeof value === "string" ? JSON.stringify(value).slice(0, 80) : value;
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
    for (const key of ["document", "navigator", "location"]) {
        globalThis[key] = makeSpy(key, globalThis[key]);
    }
}
if (DEBUG_LEVEL >= 2) {
    globalThis.window = makeSpy("window", globalThis.window); // 深度调试用，日志量大
}

// ---------- 4. 诊断导出 ----------
module.exports = {
    materializeUndici: materializeUndici,
    debug: DEBUG_LEVEL,
    envKeys: Object.keys(ENV_PLAN),
    summary: function () {
        return {
            global_deleted: typeof global === "undefined",
            buffer_alive: typeof Buffer !== "undefined",
            webdriver: globalThis.navigator.webdriver,
            ua_tail: String(globalThis.navigator.userAgent).slice(-40),
            href: globalThis.location.href,
            cookie_fields: String(globalThis.document.cookie).split("; ").filter(Boolean).length,
            cookie_source: process.env.XHS_COOKIE ? "env:XHS_COOKIE" : "placeholder",
            env_keys: Object.keys(ENV_PLAN),
        };
    },
};
