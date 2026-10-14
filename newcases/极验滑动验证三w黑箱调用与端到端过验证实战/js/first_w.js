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
//node-jsencrypt:npm install node-jsencrypt
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
function $_HBX(e, t) {
        return e >> t & 1;
}
function $_GJr(e) {
    var t = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()';
    return e < 0 || e >= t['length'] ? '.' : t['charAt'](e);
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
function $_HED(e) { //参数e就是o
    var t = $_HCR(e);
    return t["res"] + t['end'];
}
    quanju = {
        $_EJa:{
        "gt": "ff3cd843746782b0e0f377c2d234d6a5",
        "challenge": "89289830ad1dff601441709e2f64aa95",
        "offline": false,
        "new_captcha": true,
        "product": "embed",
        "width": "300px",
        "https": true,
        "protocol": "https://",
        "type": "fullpage",
        "static_servers": [
            "static.geetest.com/",
            "static.geevisit.com/"
        ],
        "beeline": "/static/js/beeline.1.0.1.js",
        "voice": "/static/js/voice.1.2.4.js",
        "click": "/static/js/click.3.1.0.js",
        "fullpage": "/static/js/fullpage.9.1.9-eyz9lh.js",
        "slide": "/static/js/slide.7.9.2.js",
        "geetest": "/static/js/geetest.6.0.9.js",
        "aspect_radio": {
            "slide": 103,
            "click": 128,
            "voice": 128,
            "beeline": 50
        }
    }
}

function get_first_w(gt,challenge) {
    var t = quanju //Ze的对象
        , n = {
            "$_CAAM": 1716735387089,
            "protocol": "https://",
            "gt": gt,
            "challenge": challenge,
            "offline": false,
            "new_captcha": true,
            "product": "float",
            "width": "300px",
            "https": true,
            "type": "fullpage",
            "static_servers": [
                "static.geetest.com/",
                "static.geevisit.com/"
            ],
            "beeline": "/static/js/beeline.1.0.1.js",
            "voice": "/static/js/voice.1.2.4.js",
            "click": "/static/js/click.3.1.0.js",
            "fullpage": "/static/js/fullpage.9.1.9-eyz9lh.js",
            "slide": "/static/js/slide.7.9.2.js",
            "geetest": "/static/js/geetest.6.0.9.js",
            "aspect_radio": {
                "slide": 103,
                "click": 128,
                "voice": 128,
                "beeline": 50
            },
            "cc": 16,
            "supportWorker": true,
            "$_FFq": {
                "pt": 0
            },
            "aeskey": "f9eb99e0c1325916"
        }; //n是一个Qe对象

    var e = "-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1";
    t['$_CCFB'] = e,
    t['$_EJa']['cc'] = 16,
    t['$_EJa']['ww'] = true,
    t['$_EJa']['i'] = e;
    //逆向出r的值
    var r = $_CCGZ()
        //JSON.stringify将对象转换成字符串的形式
        , o = encrypt1(JSON['stringify'](t['$_EJa']), $_CCHE())
        //将o作为函数参数进行调用返回i
        , i = $_HED(o)
        , s = {
            'gt': gt,
            'challenge': challenge,
            'lang': 'zh-cn',
            'pt': 0,
            'client_type': 'web',
            'w': i + r
    }
    return {
        's':s,
        'aesKey':$_CCHE()
    };
}

// ============ CLI 黑箱入口：node first_w.js '{"gt":"..","challenge":".."}' ============
if (require.main === module) {
    const _p = JSON.parse(process.argv[2] || '{}');
    console.log(JSON.stringify(get_first_w(_p.gt, _p.challenge)));
}