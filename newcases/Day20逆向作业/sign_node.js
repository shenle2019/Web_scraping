// 建设库 sign 算法 Node 复刻（使用内置 crypto，无需 crypto-js）
// 原始算法来源: Day21 课件 05 jianzhushe.js
const crypto = require('crypto');

const md5 = (s) => crypto.createHash('md5').update(s).digest('hex');

// 参数 key 排序
const Ou = (e) => {
    const t = [];
    let n = 0;
    for (const i in e) t[n++] = i;
    return t.sort();
};

// 值序列化（数组: 清理 null 后 JSON.stringify 并剥离首尾引号/空白; 对象: JSON.stringify; 其他: 原样）
const ku = function e(t) {
    let n;
    if (Array.isArray(t)) {
        for (const r in (n = new Array(), t)) {
            const o = t[r];
            for (const i in o)
                null == o[i] ? delete t[r][i] : Array.isArray(t[r][i]) && e(t[r][i]);
        }
        return (n = t), JSON.stringify(n).replace(/^(\s|")+|(\s|")+$/g, "");
    }
    return (n = t && t.constructor === Object ? JSON.stringify(t) : t);
};

const Cu = (e) => {
    const t = Ou(e);
    let n = "";
    for (const i in t) {
        const r = ku(e[t[i]]);
        null != r && "" != r.toString() && (n += t[i] + "=" + r + "&");
    }
    return n;
};

const Su = (e, t, time) => md5(t + e + time);

function getSign(param, time) {
    const t = Cu(param);
    return Su(
        "ghaepVf6IhcHmgnk4NCTXLApxQkBcvh1",
        Su("mwMlWOdyM7OXbjzQPulT1ndRZIAjShDB",
            Su("ZuSj0gwgsKXP4fTEz55oAG2q2p1SVGKK", t, time), time), time);
}

// 与课件 test.py 历史值对照: time=1713265415045, page=3, 期望 sign=8d57e9c98a0c4e753cc08475d8016099
const param = {
    eid: "",
    achievementQueryType: "and",
    achievementQueryDto: [],
    personnelQueryDto: { queryType: "and" },
    aptitudeQueryDto: {
        queryType: "and",
        nameStr: "",
        aptitudeQueryType: "and",
        businessScopeQueryType: "or",
        filePlaceType: "1",
        aptitudeDtoList: [{ codeStr: "", queryType: "and", aptitudeType: "qualification" }],
        aptitudeSource: "new",
    },
    page: { page: 3, limit: 20, field: "", order: "" },
};
const T = 1713265415045;
const sign = getSign(param, T);
console.log("序列化串:", Cu(param));
console.log("复刻 sign:", sign);
console.log("课件历史值:", "8d57e9c98a0c4e753cc08475d8016099");
console.log("一致:", sign === "8d57e9c98a0c4e753cc08475d8016099");
module.exports = { getSign, Cu };
