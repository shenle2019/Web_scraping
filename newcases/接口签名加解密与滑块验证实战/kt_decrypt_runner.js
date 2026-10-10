// 案例3 企名片：用提取的原版 JS kt 函数解密 vipapi 样本
// 用法: node kt_decrypt_runner.js
const fs = require('fs');

// 1. 加载提取出的 kt+Tt 函数模块（含 function 定义）
const ktSrc = fs.readFileSync('分析素材/kt_module.js', 'utf8');
eval(ktSrc);

// 2. 读取样本，找到加密字段
const raw = fs.readFileSync('分析素材/vipapi_sample.json', 'utf8');
const sample = JSON.parse(raw);

// 递归找 encrypt 字段
function findEnc(o) {
    if (o && typeof o === 'object') {
        for (const k of Object.keys(o)) {
            if (typeof o[k] === 'string' && k.toLowerCase().includes('encrypt')) return o[k];
            const r = findEnc(o[k]);
            if (r) return r;
        }
    }
    return null;
}
const enc = findEnc(sample);
if (!enc) { console.log('未找到加密字段'); process.exit(1); }
console.log('加密串长度:', enc.length);

// 3. 调原版 JS 解密：kt(key, atob(data), 0=解密, 0=ECB, iv, 1=pkcs7去padding)
const plain = kt("50e2673ff3ecb6e82f15fe4c", Buffer.from(enc, 'base64').toString('binary'), 0, 0, "012345677890123", 1);
console.log('解密成功，明文长度:', plain.length);

// 4. 验证是 JSON 并保存
let parsed;
try {
    parsed = JSON.parse(plain);
    console.log('JSON 解析成功! 顶层键:', Object.keys(parsed).slice(0, 10));
} catch (e) {
    console.log('JSON 解析失败:', e.message);
    parsed = null;
}
fs.writeFileSync('分析素材/vipapi_decrypted_node.json', plain);
console.log('已保存 分析素材/vipapi_decrypted_node.json');
console.log('明文前 400 字符:\n', plain.slice(0, 400));
