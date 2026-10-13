/**
 * 02_sign_engine.js —— a_bogus 签名引擎（补环境 + bdms 黑箱调用 + VM 状态机恢复法）
 * =========================================================
 * 与课件 douyin.js 的差异（重写思路）：
 *   1) 【恢复法】课件直接调用有一个隐藏缺陷：bdms 的 window.yuan 是"有状态
 *      初始化流"的挂载点，首次调用后 _v 被推进到后续流程，直接二次调用返回
 *      undefined（课件只调一次所以没暴露）。本引擎在加载完成时保存首帧快照
 *      YUAN_SEED，每次签名前 window.yuan = YUAN_SEED 复位状态机（实测 2~6ms/次）；
 *   2) 【参数结构显式化】把课件的 arguments 数组语义写成常量与注释
 *      [0, 1, 14(方法号), query, "", UA]，UA 可注入（须与请求头一致）；
 *   3) 【工程化】query 支持 base64 传参（规避 Windows 命令行引号问题）、
 *      --count 进程内压测（复用同一 VM，考察恢复法性能）；
 *   4) 用 process.exitCode 而非 process.exit()，避免 stdout 被截断。
 *
 * CLI 用法：
 *   node 02_sign_engine.js --query-b64 <base64(query串)> [--ua <UA>] [--count N]
 * stdout 最后一行是 JSON（供 Python subprocess 解析）：
 *   count=1  : {"ok":true,"a_bogus":"...","len":140,"cost_ms":x}
 *   count>1  : {"ok":true,"count":N,"ok_count":N,"total_ms":x,"avg_ms":x,...}
 *
 * 作为模块：
 *   const engine = require("./02_sign_engine.js");
 *   engine.signOnce(queryString, ua) / engine.signMany(queryString, count, ua)
 */

// 补环境（副作用式：undici 物化修复 + window 桥接 + 环境注册）
const env = require("./01_env_mini.js");

// 挂载 bdms 虚拟机（执行到"创建函数"操作码时动态挂载 window.yuan）
require("./js_asset/source.js");

// ---------- VM 状态机：首帧快照 ----------
// window.yuan 是"有状态初始化流"的挂载点：每次调用后 VM 会把下一段状态重新
// set 回 window.yuan。加载刚完成时的挂载点即"初始入口"——这里保存快照，
// 每次签名前复位，实现无限次连续签名。
const YUAN_SEED = globalThis.window.yuan;

if (!YUAN_SEED || typeof YUAN_SEED !== "function" || !YUAN_SEED._v || !YUAN_SEED._u) {
    throw new Error("bdms 挂载点 window.yuan 结构不符合预期（_v/_u 缺失），资产可能已变更");
}

// a_bogus 例程的方法编号（实测 14 即 a_bogus；数组语义见文件头注释）
const METHOD_A_BOGUS = 14;

/**
 * 单次签名（恢复法：调用前复位 VM 状态机）
 * @param {string} queryString 待签名的完整 query 串（不含 a_bogus 自身）
 * @param {string} [ua] 浏览器 UA；默认取补环境引擎的 PC UA（须与请求头一致）
 */
function signOnce(queryString, ua) {
    globalThis.window.yuan = YUAN_SEED;   // ★ 状态机复位（关键）
    const r = globalThis.window.yuan._v;  // 复位后再快照
    const args = [0, 1, METHOD_A_BOGUS, String(queryString), "", ua || env.defaultUA];
    return (0, globalThis.window.yuan._u)(r[0], args, r[1], r[2], globalThis);
}

/**
 * 连续 count 次签名（同一进程复用 VM），返回统计
 */
function signMany(queryString, count, ua) {
    const results = [];
    const times = [];
    for (let i = 0; i < count; i++) {
        const t0 = Date.now();
        results.push(signOnce(queryString, ua));
        times.push(Date.now() - t0);
    }
    const okCount = results.filter((x) => typeof x === "string" && x.length > 0).length;
    const total = times.reduce((a, b) => a + b, 0);
    return {
        ok: okCount === count,
        count: count,
        ok_count: okCount,
        sample: results[0],
        samples: results,          // 全量样本（供白名单探测/位级比对使用）
        len: results[0] ? results[0].length : 0,
        total_ms: total,
        avg_ms: Math.round((total / count) * 100) / 100,
        min_ms: Math.min.apply(null, times),
        max_ms: Math.max.apply(null, times),
        all_same: results.every((x) => x === results[0]),
    };
}

// ---------- CLI ----------
function fromB64(s) {
    return Buffer.from(s, "base64").toString("utf-8");
}

function main(argv) {
    const opt = {};
    for (let i = 0; i < argv.length; i++) {
        const a = argv[i];
        if (a === "--query-b64") opt.queryB64 = argv[++i];
        else if (a === "--ua") opt.ua = argv[++i];
        else if (a === "--count") opt.count = parseInt(argv[++i], 10);
    }
    if (!opt.queryB64) {
        console.error("用法: node 02_sign_engine.js --query-b64 <base64(query)> [--ua <UA>] [--count N]");
        return 2;
    }
    const query = fromB64(opt.queryB64);
    const count = opt.count > 1 ? opt.count : 1;

    if (count === 1) {
        const t0 = Date.now();
        const aBogus = signOnce(query, opt.ua);
        const out = { ok: typeof aBogus === "string" && aBogus.length > 0,
                      a_bogus: aBogus, len: aBogus ? aBogus.length : 0,
                      cost_ms: Date.now() - t0 };
        console.log(JSON.stringify(out));
        return out.ok ? 0 : 1;
    }
    const stat = signMany(query, count, opt.ua);
    console.log(JSON.stringify(stat));
    return stat.ok ? 0 : 1;
}

if (require.main === module) {
    // 注意：用 exitCode 而非 process.exit()，避免异步 stdout 被截断
    process.exitCode = main(process.argv.slice(2));
}

module.exports = {
    signOnce: signOnce,
    signMany: signMany,
    YUAN_SEED: YUAN_SEED,
    METHOD_A_BOGUS: METHOD_A_BOGUS,
    env: env,
};
