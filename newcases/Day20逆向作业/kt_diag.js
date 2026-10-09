// 解密函数自洽诊断：1) 往返测试 2) 密文精确分析
const fs = require('fs');
eval(fs.readFileSync('分析素材/kt_module.js', 'utf8'));

const KEY = "50e2673ff3ecb6e82f15fe4c";
const IV = "012345677890123";

console.log('=== 1. 自洽往返测试（加密→解密）===');
const msg = '{"hello":"世界","n":123}';
// 加密: kt(key, plain, 1=加密, 0=ECB, iv, 1=padding)
const encTest = kt(KEY, msg, 1, 0, IV, 1);
console.log('明文:', msg, '| 长度', msg.length);
console.log('加密输出长度:', encTest.length, '| 前16字符码点:', Array.from(encTest.slice(0,16)).map(c=>c.charCodeAt(0)).join(','));
const decTest = kt(KEY, encTest, 0, 0, IV, 1);
console.log('往返解密:', JSON.stringify(decTest), '| 一致:', decTest === msg);

// 换用 base64 中间层（模拟真实链路: atob→kt）
const b64 = Buffer.from(encTest, 'binary').toString('base64');
console.log('base64(加密结果):', b64.slice(0, 60));
const back = kt(KEY, Buffer.from(b64, 'base64').toString('binary'), 0, 0, IV, 1);
console.log('base64 链路往返:', JSON.stringify(back), '| 一致:', back === msg);

console.log('\n=== 2. 真实样本密文精确分析 ===');
const rawText = fs.readFileSync('分析素材/vipapi_sample.json', 'utf8');
const sample = JSON.parse(rawText);
function findEnc(o) {
    if (o && typeof o === 'object') {
        for (const k of Object.keys(o)) {
            if (typeof o[k] === 'string' && k.toLowerCase().includes('encrypt')) return o[k];
            const r = findEnc(o[k]); if (r) return r;
        }
    }
    return null;
}
const enc = findEnc(sample);
console.log('JSON.parse 后全长:', enc.length, '| 末10字符:', JSON.stringify(enc.slice(-10)));
console.log('含非标准 base64 字符:', (enc.match(/[^A-Za-z0-9+/=]/g) || []).length);
const bytes = Buffer.from(enc, 'base64');
console.log('Buffer.from base64 解码字节数:', bytes.length, '| %8 =', bytes.length % 8, '| %16 =', bytes.length % 16);
console.log('密文前 16 字节 hex:', bytes.slice(0, 16).toString('hex'));

console.log('\n=== 3. 用该密文尝试解密 ===');
const encBin = bytes.toString('binary');
const out = kt(KEY, encBin, 0, 0, IV, 1);
console.log('解密输出长度:', out.length);
console.log('前 120 字符码点:', Array.from(out.slice(0, 120)).map(c=>c.charCodeAt(0)).join(','));
console.log('是否为可打印 ASCII 开头:', /^[\x20-\x7e]/.test(out) ? "是" : "否");
