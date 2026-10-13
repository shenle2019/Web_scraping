/**
 * 03_sign_selftest.js —— 签名引擎自检（Node 直接运行）
 * =========================================================
 * 用同一份 JSVMP 资产，验证补环境引擎产出的签名是否满足：
 *   T1 结构正确：XYW_ 前缀 + base64(JSON 四字段) + payload 384 位 hex + X-t 毫秒时间戳
 *   T2 确定性：同输入多次签名 payload 是否一致（纯函数性观察）；换输入 payload 必变
 *   T3 稳定性：连续 N 次签名无异常，输出平均耗时（含 VM 挂载开销剔除说明）
 *
 * 用法：node 03_sign_selftest.js [--count 200]
 */
const { sign } = require("./02_xhs_sign_cli.js");
const env = require("./01_env_mini.js");

const PATH = "/api/sns/web/v1/homefeed";
const BODY = {
    cursor_score: "",
    num: 35,
    refresh_type: 1,
    note_index: 27,
    unread_begin_note_id: "",
    unread_end_note_id: "",
    unread_note_count: 0,
    category: "homefeed.food_v3",
    search_key: "",
    need_num: 10,
    image_formats: ["jpg", "webp", "avif"],
    need_filter_image: false,
};

let pass = 0;
let fail = 0;
function check(name, cond) {
    console.log("  [%s] %s", cond ? "PASS" : "FAIL", name);
    cond ? pass++ : fail++;
    return cond;
}

function decodeXs(xs) {
    return JSON.parse(Buffer.from(xs.slice(4), "base64").toString("utf8"));
}

function hr(title) {
    console.log("=".repeat(64));
    console.log(title);
    console.log("=".repeat(64));
}

function main() {
    const argv = process.argv.slice(2);
    const countIdx = argv.indexOf("--count");
    const stressCount = countIdx >= 0 ? Number(argv[countIdx + 1] || 200) : 200;

    hr("03 签名引擎自检（补环境 + JSVMP）");

    // ---------- 环境诊断 ----------
    console.log("[环境摘要] " + JSON.stringify(env.summary()));

    // ---------- T1 结构校验 ----------
    console.log("\n--- T1 结构校验 ---");
    const r1 = sign(PATH, BODY);
    console.log("  X-s 全串长度 = %d，前缀 = %s...", r1["X-s"].length, r1["X-s"].slice(0, 12));
    console.log("  X-t = %s（%s）", r1["X-t"], new Date(Number(r1["X-t"])).toISOString());
    check("X-s 以 XYW_ 开头", r1["X-s"].startsWith("XYW_"));
    const obj1 = decodeXs(r1["X-s"]);
    check("base64 段可解码为 JSON 且含四字段", ["signSvn", "signType", "appId", "payload"].every((k) => k in obj1));
    console.log("  解码字段 = " + JSON.stringify({ signSvn: obj1.signSvn, signType: obj1.signType, appId: obj1.appId }));
    check("appId = xhs-pc-web（cookie 字段完整时出现）", obj1.appId === "xhs-pc-web");
    check("payload 为 384 位十六进制（完整签名）", /^[0-9a-f]{384}$/.test(obj1.payload));
    check("X-t 在合理时间窗内（±60 秒）", Number(r1["X-t"]) > Date.now() - 60000 && Number(r1["X-t"]) <= Date.now() + 1000);
    console.log("  单次签名耗时 = %s ms", r1.cost_ms);
    check("单次签名耗时 < 100ms", r1.cost_ms < 100);

    // ---------- T2 确定性观察 ----------
    // 【实测结论】payload 含时间/熵成分：前 32 位（输入指纹段）跨调用稳定，尾部每次变化
    console.log("\n--- T2 确定性观察 ---");
    const infos = [];
    for (let k = 0; k < 3; k++) {
        const pl = decodeXs(sign(PATH, BODY)["X-s"]).payload;
        infos.push({ head: pl.slice(0, 32), tail: pl.slice(-16) });
    }
    console.log("  同输入 3 次：\n    头32 = %s\n    尾16 = %s", infos.map((x) => x.head).join("\n           "), infos.map((x) => x.tail).join(" | "));
    check("同输入多次 payload 头 32 位稳定（输入指纹段）", infos[0].head === infos[1].head && infos[1].head === infos[2].head);
    check("同输入多次 payload 尾部变化（时间/熵成分）", infos[0].tail !== infos[1].tail || infos[1].tail !== infos[2].tail);
    const other = decodeXs(sign(PATH, Object.assign({}, BODY, { num: 36 }))["X-s"]).payload;
    console.log("  变更输入(num 35→36) 头32 = %s", other.slice(0, 32));
    check("变更输入后 payload 指纹段变化", other.slice(0, 32) !== infos[0].head);

    // ---------- T3 稳定性压测 ----------
    console.log("\n--- T3 稳定性压测（进程内连续 %d 次）---", stressCount);
    let okN = 0;
    let errMsg = null;
    const t0 = Date.now();
    for (let k = 0; k < stressCount; k++) {
        try {
            sign(PATH, BODY);
            okN++;
        } catch (e) {
            errMsg = e.message;
            break;
        }
    }
    const total = Date.now() - t0;
    const avg = okN ? total / okN : 0;
    console.log("  成功 " + okN + "/" + stressCount + "，总耗时 " + total + " ms，平均 " + avg.toFixed(3) + " ms/次" + (errMsg ? ("，中断原因: " + errMsg) : ""));
    check("连续 " + stressCount + " 次签名全部成功", okN === stressCount);
    check("平均单次签名耗时 < 50ms（JSVMP 解释执行量级）", avg < 50);

    // ---------- 结论 ----------
    hr("03 结论: " + (fail === 0 ? "全部通过（" + pass + " PASS / 0 FAIL）" : pass + " PASS / " + fail + " FAIL"));
    return fail === 0 ? 0 : 1;
}

process.exitCode = main();
