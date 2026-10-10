// p78：Day24 课件（惠农网 huiNong）签名算法离线验证 —— Node 原版路线
// ---------------------------------------------------------------------
// 1) 直接 eval 课件原版 huiNong.js，调用原版 get_sign() 获取权威基准签名
//    （固定样本 nonce/timestamp/deviceId/secret 均从课件源码动态提取）
// 2) 用课件原版函数（cryptoMd5 / cryptoSha1 / cryptoSha384 / window.v 大整数）
//    复算分段值 L/B/N/C15/D/F，与 get_sign 内部 console.log 输出对照
// 3) 直接 eval 课件原版 huiNong2.js，调用 get_header() 生成动态请求头：
//    校验各字段格式（nonce 32 hex / traceid 16 位 36 进制 / sign 96 hex 等）
//    并用课件函数对动态输入复算签名做二次对照
// 4) 全部结果写 _day24_hn_node_result.json，供 p79（Python 复刻）逐项比对
// 运行：node p78_day24_hn_verify.js
const fs = require("fs");
const path = require("path");

const KDIR = "E:\\路飞学城\\课件\\JS逆向\\Day24：JS逆向爬虫基础案例05";
const code1 = fs.readFileSync(path.join(KDIR, "huiNong.js"), "utf8");
const code2raw = fs.readFileSync(path.join(KDIR, "huiNong2.js"), "utf8");
// huiNong2.js 末尾自带 console.log(get_header())，去掉避免重复执行
const code2 = code2raw.replace(/console\.log\(get_header\(\)\)\s*$/, "");

// 捕获 console.log 输出，避免课件内部调试输出干扰
function runSilenced(fn) {
  const orig = console.log;
  const buf = [];
  console.log = function () {
    buf.push(Array.from(arguments).map(String).join(" "));
  };
  let value;
  try {
    value = fn();
  } finally {
    console.log = orig;
  }
  return { value, logs: buf };
}

function pick(src, pat) {
  const m = src.match(pat);
  return m ? m[1] : null;
}

// ---------------- 第一部分：固定样本（课件原版 get_sign） ----------------
const sample = {
  nonce: pick(code1, /"nonce":\s*"([0-9a-f]+)"/),
  timestamp: pick(code1, /"timestamp":\s*"(\d+)"/),
  deviceId: pick(code1, /"deviceId":\s*"([^"]+)"/),
  secret: pick(code1, /"secret":\s*"([^"]+)"/),
  secretType: Number(pick(code1, /"secretType":\s*(\d+)/)),
};

const r1 = runSilenced(() => {
  eval(code1);
  const origSign = get_sign();                   // 课件原版权威基准
  // 分段复算用 re 前缀命名：课件函数体里 L/B/N/C/D/F/sign 是隐式全局赋值，
  // 若此处声明同名 const 会触发作用域链 TDZ 报错
  const reL = cryptoMd5(sample.nonce);           // 分段复算（同为课件函数）
  const reB = cryptoSha1(sample.timestamp);
  const reN = cryptoMd5(sample.nonce + sample.deviceId);
  const reC = cryptoSha1(sample.secret + sample.timestamp);
  const reC15 = reC.substring(reC.length - 16, reC.length - 1);
  const reD = window.v(reC15, true, 16).toUnsigned().toString(10);
  const reF = [reL, reB, reN, reD].reduce((t, e) => t + "!" + e);
  const reSign = cryptoSha384(reF);
  return { sign: origSign, L: reL, B: reB, N: reN, C15: reC15, D: reD, F: reF, signRe: reSign };
});
const s1 = r1.value;

// 解析 get_sign 内部 console.log 输出的中间值（课件自证）
const fromLogs = {};
for (const ln of r1.logs) {
  const m = ln.match(/^(L|B|N|C|D|sign):\s*(\S+)$/);
  if (m) fromLogs[m[1]] = m[2];
  else if (ln.includes("!") && /^[0-9a-f!]+$/.test(ln)) fromLogs.F = ln;
}

// ---------------- 第二部分：动态请求头（课件原版 get_header） ----------------
const r2 = runSilenced(() => {
  eval(code2);
  const h = get_header();
  const nonce = h["X-CLIENT-NONCE"];
  const tpl = (code2raw.match(/"([xy]{32})"/) || [])[1] || "";
  const yPos = [];
  for (let i = 0; i < tpl.length; i++) if (tpl[i] === "y") yPos.push(i);
  const checks = {
    nonce_32hex: /^[0-9a-f]{32}$/.test(nonce),
    nonce_var_positions_8b: yPos.map((i) => "89ab".includes(nonce[i])),
    sid_format: /^S_[0-9A-Z]{16}$/.test(h["X-CLIENT-SID"]),
    traceid_16_u36: /^[0-9A-Z]{16}$/.test(h["X-B3-TRACEID"]),
    time_13digit: /^\d{13}$/.test(h["X-CLIENT-TIME"]),
    sign_96hex: /^[0-9a-f]{96}$/.test(h["X-Client-Sign"]),
  };
  // traceid 前 9 位 36 进制可还原时间戳；SID 内嵌 time-1000
  checks.trace_ts_consistent =
    Math.abs(parseInt(h["X-B3-TRACEID"].slice(0, 9), 36) - Number(h["X-CLIENT-TIME"])) < 5000;
  checks.sid_ts_consistent =
    Math.abs(parseInt(h["X-CLIENT-SID"].slice(2, 11), 36) - (Number(h["X-CLIENT-TIME"]) - 1000)) < 5000;
  // 动态输入复算签名（课件函数，同样用 re 前缀规避 TDZ）
  const reL = cryptoMd5(h["X-CLIENT-NONCE"]);
  const reB = cryptoSha1(h["X-CLIENT-TIME"]);
  const reN = cryptoMd5(h["X-CLIENT-NONCE"] + h["X-CLIENT-ID"]);
  const reC = cryptoSha1(sample.secret + h["X-CLIENT-TIME"]);
  const reC15 = reC.substring(reC.length - 16, reC.length - 1);
  const reD = window.v(reC15, true, 16).toUnsigned().toString(10);
  const reF = [reL, reB, reN, reD].reduce((t, e) => t + "!" + e);
  const reSign = cryptoSha384(reF);
  return { header: h, checks, yPositions: yPos, signRe: reSign };
});
const s2 = r2.value;

// ---------------- 输出 ----------------
const result = {
  module: "p78 Day24 惠农网签名离线验证（Node 原版路线）",
  source_js: path.join(KDIR, "huiNong.js") + " + huiNong2.js",
  fixed_sample: {
    input: sample,
    get_sign_logs: r1.logs,
    segments_recomputed: {
      L: s1.L, B: s1.B, N: s1.N, C15: s1.C15, D: s1.D, F: s1.F,
    },
    segments_matched_with_original_logs: {
      L: fromLogs.L === s1.L, B: fromLogs.B === s1.B, N: fromLogs.N === s1.N,
      C: fromLogs.C === s1.C15, D: fromLogs.D === s1.D, F: fromLogs.F === s1.F,
    },
    sign_from_original_get_sign: s1.sign,
    sign_from_segments: s1.signRe,
    original_equals_segments: s1.sign === s1.signRe,
    sign_length: s1.sign.length,
  },
  dynamic_header: {
    header: s2.header,
    nonce_y_positions: s2.yPositions,
    checks: s2.checks,
    sign_recomputed: s2.signRe,
    sign_match_dynamic: s2.signRe === s2.header["X-Client-Sign"],
  },
};

const out = path.join(__dirname, "_day24_hn_node_result.json");
fs.writeFileSync(out, JSON.stringify(result, null, 2), "utf8");

console.log("=== p78 Node 原版路线验证结果 ===");
console.log("[1] 固定样本 get_sign()（课件原版）:");
console.log("    sign =", s1.sign);
console.log("    分段复算一致 =", s1.sign === s1.signRe);
console.log("    与课件内部日志逐段一致 =",
  JSON.stringify(result.fixed_sample.segments_matched_with_original_logs));
console.log("    L =", s1.L);
console.log("    B =", s1.B);
console.log("    N =", s1.N);
console.log("    C15 =", s1.C15);
console.log("    D =", s1.D);
console.log("[2] 动态请求头 get_header()（课件原版）:");
console.log("    nonce =", s2.header["X-CLIENT-NONCE"]);
console.log("    traceid =", s2.header["X-B3-TRACEID"], " sid =", s2.header["X-CLIENT-SID"]);
console.log("    checks =", JSON.stringify(s2.checks));
console.log("    动态输入复算签名一致 =", result.dynamic_header.sign_match_dynamic);
console.log("[3] 结果已写入:", out);
