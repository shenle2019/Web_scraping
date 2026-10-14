// w = n["$_CICO"] //w对象中包含了_HCb，_HCb就是一个轨迹数组
// l = w["$_BBED"](w["$_FD_"](), n["$_CJk"]["c"], n["$_CJk"]["s"]);
function encrypt1(e, t, n) { //e是被加密的数据，t是加密的key，n就是空
    var CryptoJs = require('crypto-js')
    var key = t;
    key = CryptoJs.enc.Utf8.parse(key);

    var iv = '0000000000000000';
    iv = CryptoJs.enc.Utf8.parse(iv);

    var data = e;

    var r = CryptoJs.AES.encrypt(data,key,{
        iv:iv,
        mode:CryptoJs.mode.CBC
    });

    var o = r['ciphertext']['words'];
    var i = r['ciphertext']['sigBytes'];
    var s = [];
    var a = 0;
    for (; a < i; a++) {
        var _ = o[a >>> 2] >>> 24 - a % 4 * 8 & 255;
        s['push'](_);
    }
    return s;
}
function $_HED(e) { //参数e就是o
    var t = $_HCR(e);
    return t["res"] + t['end'];
}
function $_HCR(e, o) {
    var i = this;
    o || (o = i); //此处o == i == this
    for (var t = function(e, t) {
        //将下面for循环中带o[]的变量直接在console中获取值进行替换
        for (var n = 0, r = 24 - 1; 0 <= r; r -= 1)
            1 === $_HBX(t, r) && (n = (n << 1) + $_HBX(e, r));
        return n;
        }, n = '', r = '', s = e['length'], a = 0; a < s; a += 3) {
        var _;
        if (a + 2 < s)
            _ = (e[a] << 16) + (e[a + 1] << 8) + e[a + 2],
            n += $_GJr(t(_, 7274496)) + $_GJr(t(_, 9483264)) + $_GJr(t(_, 19220)) + $_GJr(t(_, 235));
        else {
            var c = s % 3;
            2 == c ? (_ = (e[a] << 16) + (e[a + 1] << 8),
            n += $_GJr(t(_, 7274496)) + $_GJr(t(_, 9483264)) + $_GJr(t(_, 19220)),
            r = '.') : 1 == c && (_ = e[a] << 16,
            n += $_GJr(t(_, 7274496)) + $_GJr(t(_, 9483264)),
            r = '.' + '.');
        }
    }
    return {
        "\u0072\u0065\u0073": n,
        "\u0065\u006e\u0064": r
    };
}
function $_GJr(e) {
    var t = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()';
    return e < 0 || e >= t['length'] ? '.' : t['charAt'](e);
}
function $_HBX(e, t) {
        return e >> t & 1;
}
function e() {
    return (65536 * (1 + Math['random']()) | 0)['toString'](16)['substring'](1);
}
function te() {
        return e() + e() + e() + e();
}
var my_this = {
    $_EIY:{
        'aeskey':undefined
    }
}
function $_CCHE(e) {
    //将te()返回的值赋值给了aeskey
    /*
        如果该表达返回结果为真this['$_EIY']['aeskey'] && !e，返回this['$_EIY']['aeskey']，
        否则执行(this['$_EIY']['aeskey'] = te())，返回this['$_EIY']['aeskey']
    * */
    return my_this['$_EIY']['aeskey'] && !e || (my_this['$_EIY']['aeskey'] = te()),
    my_this['$_EIY']['aeskey'];
}
var {RSAKey} = require('node-jsencrypt')

function $_CCGZ(e) { //参数e是空值
    var rsa = new RSAKey()
    rsa.setPublic('00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81','10001')
    //t就是使用encrypt加密后的结果
        var t = rsa['encrypt']($_CCHE());
    while (!t || 256 !== t['length'])
        t = rsa['encrypt']($_CCHE(!0));
    return t;
}


function X(e){
    // 引入 crypto 模块
	const crypto = require('crypto');
    // 创建一个 MD5 加密对象
    const md5 = crypto.createHash('md5');
    // 更新要加密的数据
    md5.update(e);
    // 计算 MD5 值并以十六进制编码输出
    const result = md5.digest('hex');
    return result;
}
function $_BBED(t, e, n) {
    if (!e || !n)
        return t;
    var r, i = 0, o = t, s = e[0], a = e[2], _ = e[4];
    while (r = n['substr'](i, 2)) {
        i += 2;
        var c = parseInt(r, 16)
          , u = String['fromCharCode'](c)
          , l = (s * c * c + a * c + _) % t['length'];
        o = o['substr'](0, l) + u + o['substr'](l);
    }
    return o;
}
function ct(t) {
    //去除控制流无用代码
    this['$_BCAO'] = t || [];
}
ct.prototype = {
    '$_CAE':function(t) {
                //对该函数直接反混淆即可，无需其他操作
                //此处的this就是ct
                var e = this['$_BCAO'];
                if (e['map'])
                    return new ct(e['map'](t));
                for (var n = [], r = 0, i = e['length']; r < i; r += 1)
                    n[r] = t(e[r], r, this);
                return new ct(n);
            }
}
function $_FD_(guiji) {
    function n(t) {
        var e = '()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr'
          , n = e["length"]
          , r = ''
          , i = Math["abs"](t)
          , o = parseInt(i / n);
        n <= o && (o = n - 1),
        o && (r = e["charAt"](o));
        var s = '';
        return t < 0 && (s += '!'),
        r && (s += '$'),
        s + r + e['charAt'](i %= n);
    }
    var t = function(t) {
        for (var e, n, r, i = [], o = 0, s = 0, a = t['length'] - 1; s < a; s++)
            e = Math['round'](t[s + 1][0] - t[s][0]),
            n = Math['round'](t[s + 1][1] - t[s][1]),
            r = Math['round'](t[s + 1][2] - t[s][2]),
            0 == e && 0 == n && 0 == r || (0 == e && 0 == n ? o += r : (i['push']([e, n, r + o]),
            o = 0));
        return 0 !== o && i['push']([e, n, o]),
        i;
    }(guiji)
      , r = []
      , i = []
      , o = [];
    return new ct(t)['$_CAE'](function(t) {
        var e = function(t) {
            for (var e = [[1, 0], [2, 0], [1, -1], [1, 1], [0, 1], [0, -1], [3, 0], [2, -1], [2, 1]], n = 0, r = e['length']; n < r; n++)
                if (t[0] == e[n][0] && t[1] == e[n][1])
                    return 'stuvwxyz~'[n];
            return 0;
        }(t);
        e ? i['push'](e) : (r['push'](n(t[0])),
        i['push'](n(t[1]))),
        o['push'](n(t[2]));
    }),
    r['join']('') + '!!' + i['join']('') + '!!' + o['join']('');
}
function H(t, e) {
    //去除控制流代码然后反混淆
    for (var n = e['slice'](-2), r = [], i = 0; i < n['length']; i++) {
        var o = n['charCodeAt'](i);
        r[i] = 57 < o ? o - 87 : o - 48;
    }
    n = 36 * r[0] + r[1];
    var s, a = Math['round'](t) + n, _ = [[], [], [], [], []], c = {}, u = 0;
    i = 0;

    for (var l = (e = e['slice'](0, -2))['length']; i < l; i++)
        c[s = e['charAt'](i)] || (c[s] = 1,
        _[u]['push'](s),
        u = 5 == ++u ? 0 : u);
    var h, f = a, d = 4, p = '', g = [1, 2, 5, 10, 50];
    while (0 < f)
            0 <= f - g[d] ? (h = parseInt(Math['random']() * _[d]['length'], 10),
        p += _[d][h],
        f -= g[d]) : (_['splice'](d, 1),
        g['splice'](d, 1),
        d -= 1);
    return p;

}
//对该函数进行反混淆后结果如下：函数自定义名字为get_third_w携带了3个参数，首先先搞清楚这3各参数是啥
function get_third_w(t, n,guiji,c,s,gt,challenge) { //t滑动距离，e就是基于滑动轨迹进行处理后的一组结果，n滑动总耗时
    var tt = $_FD_(guiji)
    var e = $_BBED(tt,c,s);
    var i = {
        'lang':'zh-cn',
        'gt':gt,
        'challenge':challenge
    }
        , o = {
            'lang': 'zh-cn',
            //H函数需要逆向
            'userresponse': H(t, i['challenge']),
            'passtime': n,
            'imgload': 137,
            'aa': e, //需要逆向
            'ep': {
    "v": "7.9.2",
    "$_BIE": false,
    "me": true,
    "tm": {
        "a": 1717333662229,
        "b": 1717333662827,
        "c": 1717333662834,
        "d": 0,
        "e": 0,
        "f": 1717333662232,
        "g": 1717333662232,
        "h": 1717333662232,
        "i": 1717333662232,
        "j": 1717333662232,
        "k": 0,
        "l": 1717333662492,
        "m": 1717333662825,
        "n": 1717333662923,
        "o": 1717333662838,
        "p": 1717333663138,
        "q": 1717333663138,
        "r": 1717333663138,
        "s": 1717333664398,
        "t": 1717333664398,
        "u": 1717333664398
    },
    "td": -1
}
    };
    o['h9s9'] = '1816378497'


    o['rp'] = X(i['gt'] + i['challenge']['slice'](0, 32) + o['passtime']);
    var u = $_CCGZ()
        , l = encrypt1(JSON['stringify'](o), $_CCHE())
        , h = $_HED(l)
        , f = {
        'gt': gt,
        'challenge': challenge,
        'lang': 'zh-cn',
        '$_BCN': 0,
        'client_type': 'web',
        "w": h + u
    };
    return f;
}

// ============ CLI 黑箱入口：node third_w.js '{"distance":..,"passtime":..,"guiji":[..],"c":[..],"s":"..","gt":"..","challenge":".."}' ============
if (require.main === module) {
    const _p = JSON.parse(process.argv[2] || '{}');
    const _f = get_third_w(_p.distance, _p.passtime, _p.guiji, _p.c, _p.s, _p.gt, _p.challenge);
    console.log(JSON.stringify(_f));
}

