/**
 * 02_xhs_sign_cli.js —— X-s 签名引擎（CLI + 库双形态）
 * =========================================================
 * 职责：组装 补环境(01_env_mini.js) + JSVMP(js_asset/source.js)，
 *       对外提供 get_headers(path, bodyObj) —— 与课件 xhs.js 同款调用。
 *
 * CLI 用法（Python 侧经 subprocess 调用）：
 *   node 02_xhs_sign_cli.js --path /api/sns/web/v1/homefeed --body-b64 <base64(JSON)>
 *   node 02_xhs_sign_cli.js --path ... --body-b64 ... --count 200      # 进程内连续压测
 *
 * 输出（stdout 最后一行，单行 JSON，便于 Python 解析）：
 *   {"ok":true,"X-s":"XYW_...","X-t":1791877456185,"cost_ms":3.1}
 *   压测模式：{"ok":true,"count":200,"ok_count":200,"total_ms":...,"avg_ms":...,...}
 *
 * 细节说明：
 *   - body 用 base64 传参：规避 Windows 命令行引号转义问题（PowerShell + JSON 的经典坑）；
 *   - 结果用 process.exitCode 而非 process.exit()：避免异步 stdout 缓冲被截断
 *     （"崩溃时 console.log 来不及 flush 导致零输出"是同一类坑）。
 */
const path = require("path");

// 1) 补环境（副作用式生效） 2) 挂载 JSVMP（挂载后 globalThis._webmsxyw 可用）
require("./01_env_mini.js");
require(path.join(__dirname, "js_asset", "source.js"));

/** 与课件 xhs.js 完全同款：VM 装配出来的签名函数 */
function get_headers(c, i) {
    return globalThis._webmsxyw(c, i);
}

/** 签名 + 计时包装。body 可为对象或紧凑 JSON 字符串（与课件一致传对象） */
function sign(p, body) {
    const bodyObj = typeof body === "string" ? JSON.parse(body) : body;
    const t0 = process.hrtime.bigint();
    const r = get_headers(p, bodyObj);
    const t1 = process.hrtime.bigint();
    return { "X-s": r["X-s"], "X-t": r["X-t"], cost_ms: Number(t1 - t0) / 1e6 };
}

// ---------- CLI ----------
function parseArgs(argv) {
    const out = {};
    for (let k = 0; k < argv.length; k++) {
        const a = argv[k];
        if (a.startsWith("--")) out[a.slice(2)] = argv[k + 1];
    }
    return out;
}

function main(argv) {
    const args = parseArgs(argv);
    const pathVal = args["path"];
    const b64 = args["body-b64"];
    if (!pathVal || !b64) {
        console.error("用法: node 02_xhs_sign_cli.js --path <接口路径> --body-b64 <base64(JSON)> [--count N]");
        return 2;
    }
    const bodyObj = JSON.parse(Buffer.from(b64, "base64").toString("utf8"));
    const count = Number(args["count"] || 1);

    if (count > 1) {
        // 压测模式：单进程内连续签名（排除进程启动开销）
        const t0 = Date.now();
        let okCount = 0;
        let first = null;
        let last = null;
        let err = null;
        for (let k = 0; k < count; k++) {
            try {
                const r = sign(pathVal, bodyObj);
                if (k === 0) first = r;
                last = r;
                okCount++;
            } catch (e) {
                err = e.message;
                break;
            }
        }
        const total = Date.now() - t0;
        console.log(JSON.stringify({
            ok: okCount === count,
            count: count,
            ok_count: okCount,
            total_ms: total,
            avg_ms: okCount ? +(total / okCount).toFixed(3) : null,
            first_payload_head: payloadHead(first),
            last_payload_head: payloadHead(last),
            err: err,
        }));
    } else {
        const r = sign(pathVal, bodyObj);
        console.log(JSON.stringify({
            ok: true,
            "X-s": r["X-s"],
            "X-t": r["X-t"],
            cost_ms: +r.cost_ms.toFixed(3),
        }));
    }
    return 0;
}

function payloadHead(r) {
    if (!r) return null;
    try {
        const obj = JSON.parse(Buffer.from(r["X-s"].slice(4), "base64").toString("utf8"));
        return obj.payload.slice(0, 32);
    } catch (e) {
        return null;
    }
}

if (require.main === module) {
    process.exitCode = main(process.argv.slice(2));
}

module.exports = { get_headers: get_headers, sign: sign };
