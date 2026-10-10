// =====================================================================
// qmp_n0_verify.js —— 直接调用企名片打包 JS 中的原版解密函数验证脚本
// =====================================================================
// 用途：从打包 JS 中按括号配对提取的 N0/B0 函数（见 qmp_js_funcs/），
//       在 Node 中 eval 后直接调用，解密 vipapi 接口的实时 encrypt_data。
//       证明"不重写算法、直接执行打包产物函数"同样可以解密真实数据。
//
// 用法：node qmp_n0_verify.js
// 依赖：qmp_js_funcs/N0_des3.js、qmp_js_funcs/B0_key_schedule.js（同目录）
//
// 合规声明：仅限个人学习研究，禁止商用；单次低频请求（约 1 次/运行）。
// =====================================================================
const fs = require("fs");
const path = require("path");

const BASE = __dirname;
const KEY = "5e5062e82f15fe4ca9d24bc5";        // 实测本接口（vipapi）所用 3DES 密钥
const IV = "012345677890123";                  // 打包 JS 中的 IV 参数（ECB 模式未参与运算）
const API = "https://vipapi.qimingpian.cn/Activity/channelInformationByChannelName";

// ---- 1. 加载打包 JS 中提取的原版函数 ----
const n0Src = fs.readFileSync(path.join(BASE, "qmp_js_funcs", "N0_des3.js"), "utf8");
const b0Src = fs.readFileSync(path.join(BASE, "qmp_js_funcs", "B0_key_schedule.js"), "utf8");
eval(n0Src + "\n" + b0Src);
console.log("[1] 已加载原版函数: typeof N0 = " + typeof N0 + ", typeof B0 = " + typeof B0);

// ---- 2. 抓取实时密文 ----
(async () => {
  const resp = await fetch(API, {
    method: "POST",
    headers: {
      "accept": "application/json, text/plain, */*",
      "origin": "https://www.qimingpian.com",
      "referer": "https://www.qimingpian.com/",
      "content-type": "application/x-www-form-urlencoded",
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    },
    body: "channel_name=24%E6%96%B0%E5%A3%B0&page=1&num=20&unionid=", // channel_name=24新声
  });
  const j = await resp.json();
  const enc = j.encrypt_data;
  console.log("[2] 实时响应: status=" + j.status + " encrypt_data长度=" + (enc ? enc.length : 0));
  if (!enc) {
    console.log("    响应异常: " + JSON.stringify(j).slice(0, 200));
    return;
  }

  // ---- 3. 直接调用原版 N0 解密（等价于页面中的 V0 函数） ----
  const bin = Buffer.from(enc, "base64").toString("binary");
  const plain = N0(KEY, bin, 0, 0, IV, 1);
  const data = JSON.parse(plain);
  const list = data.list || [];
  console.log("[3] 解密成功: 顶层keys=" + Object.keys(data).join(",") + " list条数=" + list.length);
  console.log("    首条: [" + list[0].create_time + "] " + (list[0].content || "").slice(0, 48));

  // ---- 4. 保存明文结果 ----
  const outDir = path.join(BASE, "output");
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, "qmp_n0_js_decrypted_sample.json");
  fs.writeFileSync(outFile, JSON.stringify({ 来源: API, 密钥: KEY, 条数: list.length, 数据: list },
    null, 1), "utf8");
  console.log("[4] 已保存: " + outFile);
})();
