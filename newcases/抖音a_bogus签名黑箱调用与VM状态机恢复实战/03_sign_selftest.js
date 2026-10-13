/**
 * 03_sign_selftest.js —— 签名引擎自检（真实性/恢复法/位级观察）
 * =========================================================
 * 检查项：
 *   A. 课件坑复现观察：不做复位连调两次（课件调用形态）——观察第 2 次行为
 *   B. 恢复法：连续 3 次签名全部成功（本引擎核心改进）
 *   C. 形态不变量：len=160 / idx16-17="5-" / 末位 "=" / 字符集合法 /
 *      含本工程环境（full）的稳定主体（与 04 实验 REF_160 对齐）
 *   D. 随机位测量：同输入 6 次签名的逐位统计 → 输出随机位集合
 *   E. 输入绑定观察：query 改 platform=PC→PC2 的差异位集合
 *   F. UA 绑定观察：UA 改 TestUA 的差异位集合
 *   G. 压测：连续 20 次签名耗时统计
 *
 * 输出：[PASS]/[FAIL] 逐项 + 末尾统计
 */

const eng = require("./02_sign_engine.js");

const Q = "device_platform=webapp&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=170400&cookie_enabled=true&screen_width=1496&screen_height=967&browser_language=zh-CN&platform=PC&webid=7371422219199055371&msToken=XBPLACEHOLDER";
const UA = eng.env.defaultUA;
const UA2 = "TestUA/1.0";
// 本工程环境（full：屏幕/视口/navigator 等补齐）的稳定主体（164 环境实测段）
const REF164 = "xow7zvMIubZsQJIeujy4hbTp/hrQC98qwf98wL/2AksjSkKl5Q5xSSs1XHtLhgJU0Omkt-CFx2RkBRrPw8yyOcSYLk09xrmd38eqVxO9Ev";
const ALLOWED = new Set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/-=".split(""));

let nPass = 0, nFail = 0;
function check(name, cond, extra) {
    if (cond) nPass++; else nFail++;
    console.log("  [%s] %s%s", cond ? "PASS" : "FAIL", name, extra ? "   " + extra : "");
    return cond;
}
function hr(t) { console.log("=".repeat(72)); console.log(t); console.log("=".repeat(72)); }
function diffPos(a, b) {   // 两个等长字符串的逐位差异位置
    const out = [];
    for (let i = 0; i < Math.min(a.length, b.length); i++) if (a[i] !== b[i]) out.push(i);
    return out;
}

// ---------- A. 课件坑复现观察（不做复位，跟随 window.yuan 直调） ----------
hr("A. 课件坑复现观察：直调（不恢复）连调两次");
function directCall() {   // 完全复刻课件 douyin.js 的调用形态（不复位）
    const r = globalThis.window.yuan._v;
    return (0, globalThis.window.yuan._u)(r[0], [0, 1, 14, Q, "", UA], r[1], r[2], globalThis);
}
let d1 = null, d2 = null, d2err = null;
try { d1 = directCall(); } catch (e) { d1 = "EXC:" + e.message; }
try { d2 = directCall(); } catch (e) { d2err = e.message; }
console.log("  直调#1:", typeof d1 === "string" ? ("成功 len=" + d1.length) : ("异常 " + d1));
console.log("  直调#2:", d2err ? ("抛异常: " + d2err.slice(0, 90)) : (d2 === undefined ? "undefined（复现课件坑：VM 状态已推进）" : ("string len=" + (d2 && d2.length))));
console.log("  ※ 此组为观察项，不参与 PASS/FAIL（行为取决于 VM 内部状态推进）");

// ---------- B. 恢复法 ----------
hr("B. 恢复法：连续 3 次签名（每次调用前复位 VM）");
const s3 = [];
for (let i = 0; i < 3; i++) s3.push(eng.signOnce(Q));
check("连续 3 次均产出 string", s3.every((x) => typeof x === "string" && x.length > 0),
    s3.map((x) => (x ? x.length : "X")).join("/"));

// ---------- C. 形态不变量 ----------
hr("C. 形态不变量（用 B 组样本）");
const sample = s3[0];
check("len == 164（full 环境形态）", sample.length === 164, "len=" + sample.length);
check("idx16-17 == '5-'", sample.slice(16, 18) === "5-", "'" + sample.slice(16, 18) + "'");
check("末位 == '='", sample.slice(-1) === "=", "尾3='" + sample.slice(-3) + "'");
check("字符集合法(A-Za-z0-9+/-=)", Array.from(sample).every((c) => ALLOWED.has(c)));
check("含 full 环境稳定主体(164 基准)", sample.includes(REF164));

// ---------- D. 随机位测量 ----------
hr("D. 随机位测量：同输入 10 次签名逐位统计");
const batch = [];
for (let i = 0; i < 10; i++) batch.push(eng.signOnce(Q));
const randPos = [];
for (let i = 0; i < 164; i++) {
    const set = new Set(batch.map((s) => s[i]));
    if (set.size > 1) randPos.push(i);
}
console.log("  随机位(%d) = [%s]", randPos.length, randPos.join(","));
check("随机位数量 <= 40（结构性占位量级）", randPos.length <= 40, "count=" + randPos.length);
const stableSeg = 164 - randPos.length;
console.log("  稳定位 %d/164；主体区(30~120)随机位 = [%s]",
    stableSeg, randPos.filter((p) => p >= 30 && p <= 120).join(","));

// ---------- E. 输入绑定观察 ----------
hr("E. 输入绑定观察：platform=PC -> PC2");
const q2 = Q.replace("platform=PC&", "platform=PC2&");
const bA = [eng.signOnce(Q), eng.signOnce(Q)];
const bB = [eng.signOnce(q2), eng.signOnce(q2)];
const inputDiff = diffPos(bA[0], bB[0]).filter((p) => !randPos.includes(p));
console.log("  query2 =", q2.slice(0, 90) + "...");
console.log("  排除随机位后差异位 = [%s]", inputDiff.join(","));

// ---------- F. UA 绑定观察 ----------
hr("F. UA 绑定观察：默认 UA -> TestUA/1.0");
const bC = [eng.signOnce(Q, UA2), eng.signOnce(Q, UA2)];
const uaDiff = diffPos(bA[0], bC[0]).filter((p) => !randPos.includes(p));
console.log("  排除随机位后差异位 = [%s]", uaDiff.join(","));

// ---------- G. 压测 ----------
hr("G. 压测：连续 20 次签名");
const stat = eng.signMany(Q, 20);
check("20 次全部成功", stat.ok, "ok_count=" + stat.ok_count);
console.log("  耗时 total=%dms avg=%sms min=%dms max=%dms", stat.total_ms, stat.avg_ms, stat.min_ms, stat.max_ms);

// ---------- H. 环境诊断 ----------
hr("H. 补环境诊断摘要");
console.log(" ", JSON.stringify(eng.env.summary()));

hr("结果汇总");
console.log("  PASS %d / %d", nPass, nPass + nFail);
console.log("=".repeat(72));
process.exitCode = nFail === 0 ? 0 : 1;
