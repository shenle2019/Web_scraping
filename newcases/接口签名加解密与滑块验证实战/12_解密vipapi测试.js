// 用老版企名片 vipapi 的正确 key 测试解密（key 来源: 公开逆向案例文章）
const fs = require('fs');
eval(fs.readFileSync('分析素材/kt_module.js', 'utf8'));

const raw = JSON.parse(fs.readFileSync('分析素材/vipapi_sample.json', 'utf8'));
const enc = raw.encrypt_data;

const KEY = "5e5062e82f15fe4ca9d24bc5"; // 老版 vipapi key
const IV = "012345677890123";

const plain = kt(KEY, Buffer.from(enc, 'base64').toString('binary'), 0, 0, IV, 1);
console.log('解密输出长度:', plain.length);
console.log('前 300 字符:', plain.slice(0, 300));

try {
    const obj = JSON.parse(plain);
    console.log('\n=== JSON 解析成功！顶层键:', Object.keys(obj).join(', '));
    fs.writeFileSync('分析素材/vipapi_decrypted.json', plain);
    console.log('已保存 分析素材/vipapi_decrypted.json');
    // 打印部分内容
    const preview = JSON.stringify(obj, null, 1).slice(0, 800);
    console.log('\n内容预览:\n', preview);
} catch (e) {
    console.log('\nJSON 解析失败:', e.message);
}
