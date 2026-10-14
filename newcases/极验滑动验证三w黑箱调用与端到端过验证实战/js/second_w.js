function $_HED(e) {
    //其中HCN之前定义过了，直接用即可
    //var t = this['$_HCN'](e);
    var t = $_HCN(e);
    return t['res'] + t['end'];
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
function get_H_value(e){
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
function $_GHQ(e) {
    //反混淆后，无需额外逆向处理，所有变量都是已知的
    for (var t = [], n = 0, r = e['length']; n < r; n += 1)
        t['push'](e['charCodeAt'](n));
    return t;
}
//从first_w.js中复制的
function $_GJr(e) {
    //删除前5行，然后进行反混淆
    //var t = this['$_GAc']; //直接在console中运行this[]返回结果如下
    var t = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()'
    return e < 0 || e >= t['length'] ? '.' : t['charAt'](e);
}
//从first_w.js中复制的
function $_HBX(e, t) {
    return e >> t & 1;
}
function $_HCN(e, o) {
    var i = this;
    o || (o = i);
    for (var t = function(e, t) {
        //此处打上断点，可知o['$_GGY']就是24，将其进行替换
        for (var n = 0, r = 24 - 1; 0 <= r; r -= 1)
            //逆向i['$_HBX']函数，该函数在first_w.js中逆向过了，复制过来直接使用即可
            1 === $_HBX(t, r) && (n = (n << 1) + $_HBX(e, r));
        return n;
    }, n = '', r = '', s = e['length'], a = 0; a < s; a += 3) {
        var _;
        if (a + 2 < s)
            _ = (e[a] << 16) + (e[a + 1] << 8) + e[a + 2],
            //o['$_GCw']就是7274496，进行全局替换
            //o['$_GDc']就是9483264，进行全局替换
            //o['$_GEf']就是19220，进行全局替换
            //o['$_GFT']就是235，进行全局替换
            //o['$_GBt']就是'.' ，进行全局替换

            //$_GJr函数逆向：在first_w.js中逆向过，直接复制过来即可使用
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
function get_p_value(e){
    //逆向此处的this['$_GHQ']和this['$_HCN']
    //此处打上断点，进入到this['$_GHQ']和this['$_HCN']函数定义位置进行逆向
    //逆向后，替换下面的this['$_GHQ']和this['$_HCN']
    var t = $_HCN($_GHQ(e));
    return t['res'] + t['end'];
}

function $_DJS(e) {
    this['$_BAEy'] = e || [];
}
$_DJS.prototype = {
    "$_EBs":function(e) {
        var t = this['$_BAEy'];
        if (t['map'])
            return new $_DJS(t['map'](e));
        for (var n = [], r = 0, o = t['length']; r < o; r += 1)
            n[r] = e(t[r], r, this);
        return new $_DJS(n);
    }
}
function get_n_value() {
    var n = this
      , r = {}
      , o = [];
    var arr = [
    "textLength",
    "HTMLLength",
    "documentMode",
    "A",
    "ARTICLE",
    "ASIDE",
    "AUDIO",
    "BASE",
    "BUTTON",
    "CANVAS",
    "CODE",
    "IFRAME",
    "IMG",
    "INPUT",
    "LABEL",
    "LINK",
    "NAV",
    "OBJECT",
    "OL",
    "PICTURE",
    "PRE",
    "SECTION",
    "SELECT",
    "SOURCE",
    "SPAN",
    "STYLE",
    "TABLE",
    "TEXTAREA",
    "VIDEO",
    "screenLeft",
    "screenTop",
    "screenAvailLeft",
    "screenAvailTop",
    "innerWidth",
    "innerHeight",
    "outerWidth",
    "outerHeight",
    "browserLanguage",
    "browserLanguages",
    "systemLanguage",
    "devicePixelRatio",
    "colorDepth",
    "userAgent",
    "cookieEnabled",
    "netEnabled",
    "screenWidth",
    "screenHeight",
    "screenAvailWidth",
    "screenAvailHeight",
    "localStorageEnabled",
    "sessionStorageEnabled",
    "indexedDBEnabled",
    "CPUClass",
    "platform",
    "doNotTrack",
    "timezone",
    "canvas2DFP",
    "canvas3DFP",
    "plugins",
    "maxTouchPoints",
    "flashEnabled",
    "javaEnabled",
    "hardwareConcurrency",
    "jsFonts",
    "timestamp",
    "performanceTiming",
    "internalip",
    "mediaDevices",
    "DIV",
    "P",
    "UL",
    "LI",
    "SCRIPT",
    "touchEvent"
];
    return new $_DJS(arr)['$_EBs'](function(e) {
        var t = r[e];
        o['push'](void 0 === t ? -1 : t);
    }),
    o['join']('magic data');
}
function get_t_value() {
    return $_HDZ([]);
}
//逆向好$_HDZ后，就可以直接调用get_e_value()查看返回的结果，是正常可用的！
//该函数只需要反混淆、去除控制流即可
function $_HDZ(e) {
    //前5行已经删除
    //全局进行反混淆操作
    var p = {
        "\u006d\u006f\u0076\u0065": 0,
        "\u0064\u006f\u0077\u006e": 1,
        "\u0075\u0070": 2,
        "\u0073\u0063\u0072\u006f\u006c\u006c": 3,
        "\u0066\u006f\u0063\u0075\u0073": 4,
        "\u0062\u006c\u0075\u0072": 5,
        "\u0075\u006e\u006c\u006f\u0061\u0064": 6,
        "\u0075\u006e\u006b\u006e\u006f\u0077\u006e": 7
    };
    function h(e, t) {
        //控制流：剩下case中的for循环和return即可，剩下全部删除
        for (var n = e['toString'](2), r = '', o = n['length'] + 1; o <= t; o += 1)
            r += '0';
        return n = r + n;
    }
    function f(e) {
        //控制流：直接处理，以此运行两个case中的内容
            var t = []
              , n = e['length']
              , r = 0;
            while (r < n) {
                var o = e[r]
                  , i = 0;
                while (1) {
                    if (16 <= i)
                        break;
                    var s = r + i + 1;
                    if (n <= s)
                        break;
                    if (e[s] !== o)
                        break;
                    i += 1;
                }
                r = r + 1 + i;
                var a = p[o];
                0 != i ? (t['push'](8 | a),
                t['push'](i - 1)) : t['push'](a);
            }
            for (var _ = h(32768 | n, 16), c = '', l = 0, u = t['length']; l < u; l += 1)
                c += h(t[l], 4);
            return _ + c;
        }

    function c(e, t) {
        //控制流：保存case中的for循环和return即可
        for (var n = [], r = 0, o = e['length']; r < o; r += 1)
            n['push'](t(e[r]));
        return n;
    }

    function d(e, t) {
        //控制流：只会以此运行每个case中的代码
        e = function _(e) {
            //前五行已经删除
            var t = 32767
              , n = (e = c(e, function(e) {
                //前五行已经删除
                return t < e ? t : e < -t ? -t : e;
            }))['length']
              , r = 0
              , o = [];
            while (r < n) {
                var i = 1
                  , s = e[r]
                  , a = Math['abs'](s);
                while (1) {
                    if (n <= r + i)
                        break;
                    if (e[r + i] !== s)
                        break;
                    if (127 <= a || 127 <= i)
                        break;
                    i += 1;
                }
                1 < i ? o['push']((s < 0 ? 49152 : 32768) | i << 7 | a) : o['push'](s),
                r += i;
            }
            return o;
        }(e);

        var n, r = [], o = [];

        c(e, function(e) {
            //前五行已经删除
            var t = Math['ceil'](function n(e, t) {
                //前五行已经删除
                return 0 === e ? 0 : Math['log'](e) / Math['log'](t);
            }(Math['abs'](e) + 1, 16));
            0 === t && (t = 1),
            r['push'](h(t - 1, 2)),
            o['push'](h(Math['abs'](e), 4 * t));
        });

        var i = r['join']('')
          , s = o['join']('');

        return n = t ? c(function a(e, t) {
            //前五行已经删除
            var n = [];
            return c(e, function(e) {
               //前五行已经删除
                t(e) && n['push'](e);
            }),
            n;
        }(e, function(e) {
            //前五行已经删除
            return 0 != e && e >> 15 != 1;
        }), function(e) {
            //前五行已经删除
            return e < 0 ? '1' : '0';
        })['join']('') : '',
        h(32768 | e['length'], 16) + i + s + n;

    }
    return function(e) {
       //前五行已经删除
        for (var t = [], n = [], r = [], o = [], i = 0, s = e['length']; i < s; i += 1) {
            var a = e[i]
              , _ = a['length'];
            t['push'](a[0]),
            n['push'](2 === _ ? a[1] : a[2]),
            3 === _ && (r['push'](a[1][0]),
            o['push'](a[1][1]));
        }
        var c = f(t) + d(n, !1) + d(r, !0) + d(o, !0)
          , l = c['length'];
        return l % 6 != 0 && (c += h(0, 6 - l % 6)),
        function u(e) {
            //前五行已经删除
            for (var t = '', n = e['length'] / 6, r = 0; r < n; r += 1)
                //nodejs中没有window这个全局变量，调用parseInt，直接parseInt（）就行，不需要window点的操作
                t += '()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~'['charAt'](parseInt(e['slice'](6 * r, 6 * (r + 1)), 2));
            return t;
        }(c);
    }(e);
}
function get_e_value() {
    var e = [
    [
        "up",
        223,
        714,
        1717077570056,
        "pointerup"
    ],
    [
        "down",
        223,
        714,
        1717077570761,
        "pointerdown"
    ],
    [
        "focus",
        1717077570763
    ],
    [
        "up",
        223,
        714,
        1717077570840,
        "pointerup"
    ]
];
    var $_BHIG = [
    [
        "up",
        [
            223,
            714
        ],
        0
    ],
    [
        "down",
        [
            0,
            0
        ],
        705
    ],
    [
        "focus",
        2
    ],
    [
        "up",
        [
            0,
            0
        ],
        77
    ]
];
    return $_HDZ($_BHIG);

}
function get_i_CECe(gt,challenge) {
    var $_CCFB = '-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1';
    var vip_order = undefined;
    var ct = undefined;
    now = new Date().getTime();
    var $_CEDX = {
    "v": "9.1.9-glhvqm",
    "te": false,
    "$_BCQ": true,
    //现存计算架构
    "ven": "Google Inc. (NVIDIA)",
    //此处就是显卡信息
    "ren": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4060 (0x00002882) Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "fp": [ //鼠标某次移动开始的坐标和时间
        "move",
        404,
        121,
        //此处时间可以换成当前系统时间
        //1715675996090,
        now,
        "pointermove"
    ],
    "lp": [ //鼠标最后停止时的坐标和时间
        "up",
        221,
        304,
        //结束时间，就是now加上一个时间间隔即可
        now+999,
        "pointerup"
    ],
    "em": {
        "ph": 0,
        "cp": 0,
        "ek": "11",
        "wd": 1,
        "nt": 0,
        "si": 0,
        "sc": 0
    },
    "tm": {
        "a": 1715675994241,
        "b": 1715675994406,
        "c": 1715675994406,
        "d": 0,
        "e": 0,
        "f": 1715675994242,
        "g": 1715675994242,
        "h": 1715675994242,
        "i": 1715675994242,
        "j": 1715675994242,
        "k": 0,
        "l": 1715675994325,
        "m": 1715675994404,
        "n": 1715675994404,
        "o": 1715675994407,
        "p": 1715675994495,
        "q": 1715675994495,
        "r": 1715675994496,
        "s": 1715675994496,
        "t": 1715675994497,
        "u": 1715675994497
    },
    "dnf": "dnf",
    "by": 0
}

    var i = this
        , e = get_e_value()
        , t = get_t_value()
        , n = get_n_value()
        , r = 'SPAN_0'
        , o = {
    "$_CAAM": 1717076756510,
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
        "static.geetest.com",
        "static.geevisit.com"
    ],
    "voice": "/static/js/voice.1.2.4.js",
    "click": "/static/js/click.3.1.0.js",
    "beeline": "/static/js/beeline.1.0.1.js",
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
    "aeskey": "94d8a39c4eb104eb",
    "theme": "wind",
    "theme_version": "1.5.8",
    "api_server": "api.geevisit.com",
    "logo": true,
    "feedback": "https://www.geetest.com/contact#report",
    "c": [
        12,
        58,
        98,
        36,
        43,
        95,
        62,
        15,
        12
    ],
    "s": "705f3f45",
    "i18n_labels": {
        "copyright": "由极验提供技术支持",
        "error": "网络不给力",
        "error_content": "请点击此处重试",
        "error_title": "网络超时",
        "fullpage": "智能检测中",
        "goto_cancel": "取消",
        "goto_confirm": "前往",
        "goto_homepage": "是否前往验证服务Geetest官网",
        "loading_content": "智能验证检测中",
        "next": "正在加载验证",
        "next_ready": "请完成验证",
        "read_reversed": false,
        "ready": "点击按钮进行验证",
        "refresh_page": "页面出现错误啦！要继续操作，请刷新此页面",
        "reset": "请点击重试",
        "success": "验证成功",
        "success_title": "通过验证"
    }
}
        , s = 2018;
    //该行代码其实就是i[$_CECj] = "";
    i['$_CECe'] = '';
    for (var a = [['lang', o['lang'] || 'zh-cn'], ['type', 'fullpage'], ['tt', function (e, t, n) {
        if (!t || !n)
            return e;
        var r, o = 0, i = e, s = t[0], a = t[2], _ = t[4];
        while (r = n['substr'](o, 2)) {
            o += 2;
            var c = parseInt(r, 16)
                , l = String['fromCharCode'](c)
                , u = (s * c * c + a * c + _) % e['length'];
            i = i['substr'](0, u) + l + i['substr'](u);
        }
        return i;
            }(e, o['c'], o['s']) || -1], ['light', r || -1], ['s', get_H_value(get_p_value(t))], ['h', get_H_value(get_p_value(n))], ['hh', get_H_value(n)], ['hi', get_H_value($_CCFB)], ['vip_order', vip_order || -1], ['ct', ct || -1], ['ep', $_CEDX || -1], ['passtime', s || -1], ['rp', get_H_value(o['gt'] + o['challenge'] + s)]], _ = 0; _ < a['length']; _++)
        i['$_CECe'] += '"' + a[_][0] + '":' + JSON['stringify'](a[_][1]) + ',';
    return i['$_CECe'];
}
function get_second_w(aseKey,gt,challenge) {
    //断点打在此处，发现t=['bbOy'],然后通过push将e添加到数组中，此时e就是一个空字符串
    // t = ['bbOy',""]
    var r = '';
    var o_string_code = "function o(e,t){var $_CFGDg=hZohI.$_CQ,$_CFGCD=['$_CFGGV'].concat($_CFGDg),$_CFGEq=$_CFGCD[1];$_CFGCD.shift();var $_CFGFQ=$_CFGCD[0];function n(e){var $_DDHGA=hZohI.$_Dd()[0][16];for(;$_DDHGA!==hZohI.$_Dd()[9][13];){switch($_DDHGA){case hZohI.$_Dd()[9][16]:var t=5381,n=e[$_CFGEq(81)],r=0;$_DDHGA=hZohI.$_Dd()[3][15];break;case hZohI.$_Dd()[3][15]:while(n--)t=(t<<5)+t+e[$_CFGDg(31)](r++);$_DDHGA=hZohI.$_Dd()[0][14];break;case hZohI.$_Dd()[9][14]:return t&=~(1<<31);break;}}}100<new Date()[$_CFGDg(200)]()-t[$_CFGDg(200)]()&&(e=$_CFGEq(1152)),r=$_CFGEq(766)+i[$_CFGEq(1109)]+$_CFGEq(1188)+n(o[$_CFGEq(47)]()+n(n[$_CFGDg(47)]())+n(e[$_CFGDg(47)]()))+$_CFGEq(1122);}";
    var n_string_code = 'function n(e){var $_DDHGA=hZohI.$_Dd()[0][16];for(;$_DDHGA!==hZohI.$_Dd()[9][13];){switch($_DDHGA){case hZohI.$_Dd()[9][16]:var t=5381,n=e[$_CFGEq(81)],r=0;$_DDHGA=hZohI.$_Dd()[3][15];break;case hZohI.$_Dd()[3][15]:while(n--)t=(t<<5)+t+e[$_CFGDg(31)](r++);$_DDHGA=hZohI.$_Dd()[0][14];break;case hZohI.$_Dd()[9][14]:return t&=~(1<<31);break;}}}';
    var e_string_code = 'bbOy';
    //下面是一个自运行函数，将t['shift'](), new Date()传递给了e和t这两个形参
    !function o(e, t) {
        function n(e) {
            var t = 5381
              , n = e['length']
              , r = 0;
            while (n--)
                t = (t << 5) + t + e['charCodeAt'](r++);
            return t &= ~(1 << 31);
        }
        100 < new Date()['getTime']() - t['getTime']() && (e = 'qwe'),
        //关键变量r的定义
        r = '{' + get_i_CECe(gt,challenge) + '"captcha_token":"' + n(o_string_code + n(n_string_code) + n(e_string_code)) +'","sugd":"lyaxkuq4"}';
    //此处t就是['bbOy','']通过shift将第一个元素取出，则t[shift] == bbOy
    // }(t['shift'](), new Date());
    }('bbOy', new Date());
    //返回值中，p['$_HED']是一个函数。c['encrypt']是一个函数
    //i['$_CCHE']()是一个函数调用返回一个秘钥
    //r是一组json格式的字符串
    return $_HED(encrypt1(r, aseKey));
}

// ============ CLI 黑箱入口：node second_w.js '{"aesKey":"..","gt":"..","challenge":".."}' ============
if (require.main === module) {
    const _p = JSON.parse(process.argv[2] || '{}');
    console.log(JSON.stringify({ w: get_second_w(_p.aesKey, _p.gt, _p.challenge) }));
}

