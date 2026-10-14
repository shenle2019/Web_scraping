/*
 * zhihu_sign.js —— 知乎 x-zse-96 签名本地计算入口（补环境黑箱调用版）
 *
 * 路线（最省力，不做纯算）：
 *   require env.js    → 建环境（window / __ZH__.zse 三表 / DOM 桩 / 固定随机）
 *   require mod.js    → 注册业务 chunk（含模块 1514：zse 签名模块，内含字节码 VM）
 *   require loader.js → webpack runtime 初始化，暴露 yuan.loader（被改造过的 require）
 *   yuan.loader(1514).ZP(md5hex) → 签名主体（不含 "2.0_" 前缀，前缀由调用方拼接）
 *
 * 用法一（批量 JSON）: node zhihu_sign.js '["md5串1","md5串2"]'
 *   输出: ["签名1","签名2"]
 * 用法二（stdin 逐行）: echo md5串 | node zhihu_sign.js -
 *   输出: 每行一个签名
 */
require("./env");
require("./mod");
require("./loader");

var ZP = yuan.loader(1514)["ZP"];
var args = process.argv[2];

if (!args) {
    console.error('用法: node zhihu_sign.js \'["md5串",...]\' 或 node zhihu_sign.js - < md5列表');
    process.exit(1);
}

if (args === "-") {
    // stdin 模式：每行一个 md5，逐行输出签名
    var lines = require("fs").readFileSync(0, "utf-8").trim().split(/\r?\n/);
    lines.forEach(function (line) {
        if (line.trim()) console.log(ZP(line.trim()));
    });
} else {
    // 批量模式：JSON 数组进，JSON 数组出
    var md5List = JSON.parse(args);
    console.log(JSON.stringify(md5List.map(function (s) { return ZP(s); })));
}
