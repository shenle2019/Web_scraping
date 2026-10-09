//layui变量
var layer, laypage, laydate, laytpl, form;
var laystart, layend;
var layerisload = false;
//是否为首次加载
var isfirst = true;
var isbinddata = false;
//页面基础数据
var baseData = null;
var isLoadBase = false;
//搜索返回数据
var resultData = null;
//搜索返回推荐数据
var resultTjData = null;
//推荐项目类别 默认：0：非推荐信息 1：拆分关键词推荐 2：地区推荐
var tjType = 0;
//无数据拆分词
var keywordsSplitArry = [];
//建议搜索拆分词组
var jianyiKwdArry = [];
var currTjKwd = "";
var currInputKwd = "";//搜索框关键词
var nextToken = "";
var resultKwdData = null;
//全部地区Json
var diqusJson = [];
//旧版搜索参数
var searchParams = [];
//是否显示顶部悬浮搜索
var topSearchShow = true;
//弹框是否生效
var isEffectTank = false;
var tjKeyword = '';
//推荐供应商DOM对象数组及相关参数
var tjgysItems = [];
let tjgysActiveIndex = -1;
let tjgysExpandTimer = null;
const TJGYS_EXPAND_DELAY = 200;
const TJGYS_CLOSE_DURATION = 400;

//登录信息
var pub = {
    logoutMember: function () {
        var y = "//sso.bidcenter.com.cn/logout";
        location.href = y + "?redirectURL=" + encodeURIComponent(location.href.replace(/&/g, '|'));
    },
    login: function (APIKey, RUname, RUpwd) {
        var y = "//sso.bidcenter.com.cn/";
        location.href = y + "validate?apk=" + APIKey + "&u=" + encodeURI(location.href.replace(/&/g, '|')) + "&RUname=" + RUname + "&RUpwd=" + RUpwd;
        return false;
    }
};
//页面基础变量
var variate = {
    key: { "words": [863652730, 2036741733, 1164342596, 1782662963], "sigBytes": 16 },
    aceIV: { "words": [1719227713, 1314533489, 1397643880, 1749959510], "sigBytes": 16 },
    xgGjcArray: [],
    xgGjcIndex: 0,
    isPageLoad: jq_searchData.page > 1 ? true : false//是否为页码跳转
}
//避免重复加载
var preRep = {
    loadCkxm: false
}
//提交验重变量
var cheRep = {
    dingyue: false
}
//定时器
var timer = {
    searchIndex: 0,
    search: null
}
//弹框对象
var tankObj = {
    yjfkIndex: null,
    dingyue: null,
    tellmeIndex: null
}
//页面方法
var method = {
    //提示信息
    commonAlert: function (content, options, yes) {
        options = options ? options : -1;
        try {
            layer.alert(content, options, yes);
        } catch (e) {
            alert(content);
            if (yes) {
                yes();
            }
        }
    },
    //提示信息
    commonTips: function (content, follow, options) {
        try {
            options = options ? options : new Object();
            if (!options.time) {
                options.time = 3;
            }
            if (!options.style) {
                options.style = ['background-color:#4595E6; color:#fff', '#4595E6'];
            }
            layer.tips(content, follow, options);
        } catch (e) {
            alert(content);
        }
    },
    //权限弹框提示
    showAllowTank: function (select, msg, width, height) {
        if (msg && msg != "")
            $(".gongneng_text").text(msg)
        if (!width || width == "")
            width = "750px";
        if (!height || height == "")
            height = "287px";
        layer.closeAll();
        layer.open({
            type: 1,
            title: false,
            closeBtn: 1,
            shadeClose: false, //点击遮罩关闭
            shade: 0.5,
            area: [width, height],
            content: $(select),
            end: function () {
                $(select).hide();
            }
        });
    },
    //清空已选条件位置展示效果
    jq_clearParSta: function () {
        $("#jq_search_params ul.yixuantiaojian-list,#jq_search_params2 ul.yixuantiaojian-list").html("");
        $(".yixuantiaojian").hide();
    },
    //清空筛选位置展示效果
    jq_clearSelectSta: function () {
        //地区
        jq_didu_fn.c_qingkong();
        jq_didu_fn.s_xuanzhong();
        //类别
        jq_type_fn.c_qingkong();
        jq_type_fn.s_xuanzhong();
        //发布时间
        jq_time_fn.c_qingkong();
        //自定义时间
        jq_customTime_fn.c_qingkong();
        //历史信息
        jq_history_fn.c_qingkong();
        //筛选范围
        jq_tag_fn.c_qingkong();
        //筛选模式
        var modTid = resultData.isFufei ? 1 : 0;
        jq_mod_fn.c_qingkong(modTid);
        //项目金额
        jq_zbje_fn.c_qingkong();
        //自定义金额
        jq_customZbje_fn.c_qingkong();
        //采购方式
        jq_cgfs_fn.c_qingkong();
        //资金来源
        jq_zjly_fn.c_qingkong();
        //评标办法
        jq_pbbf_fn.c_qingkong();
        //资质证书
        jq_zzzs_fn.c_qingkong();
        //排除词
        jq_excode_fn.c_qingkong();
        //相关词
        jq_kwordh_fn.c_qingkong();
    },
    //初始化默认参数
    jq_initParams: function () {
        //地区
        jq_searchDataNew.diqu = "";
        jq_searchDataNew.diquArea = "";
        jq_searchDataNew.areacode = "";
        //类别
        jq_searchDataNew.type = "";
        //发布时间
        jq_searchDataNew.time = 0;
        //自定义时间
        jq_searchDataNew.startTime = "";
        jq_searchDataNew.endTime = "";
        //筛选范围
        jq_searchDataNew.tag = 0;
        //筛选模式
        jq_searchDataNew.mod = 0;
        //项目金额
        jq_searchDataNew.zbjefw = 0;
        //自定义金额
        jq_searchDataNew.zbje_min = 0;
        jq_searchDataNew.zbje_max = 0;
        //采购方式
        jq_searchDataNew.ext_cgfs = "";
        //资金来源
        jq_searchDataNew.ext_zjly = "";
        //评标办法
        jq_searchDataNew.ext_pbbf = "";
        //资质证书
        jq_searchDataNew.zzzs = "";
        //排除词
        jq_searchDataNew.excode = "";
        //相关词
        jq_searchDataNew.kwordtagh = "";
        //排除词搜素范围
        jq_searchDataNew.paichutag = 0;
        //相关词搜索范围
        jq_searchDataNew.xiangguantag = 0;
    },
    //清空已选条件事件
    jq_clearParams: function () {
        method.jq_clearParSta();
        method.jq_clearSelectSta();
        method.jq_initParams();
        method.jq_search();
    },
    //页面搜索条件绑定
    jq_QDataBind: function (q) {
        //关键词绑定
        if (tjType == 0) {
            currInputKwd = decodeURIComponent(q.keywords);
            $("#jq_search_keyword").val(currInputKwd);
            var kwds = [];
            kwds.push(currInputKwd);
            if (q.secondKwds != undefined && q.secondKwds != '')
                kwds.push(decodeURIComponent(q.secondKwds));
            $(".keywords_show").text(kwds.join('∩')).attr("title", kwds.join('->'));
        }
        //清空已选条件
        method.jq_clearParSta();
        //地区
        method.jq_QDiqusBind(q);
        //小地区绑定
        method.jq_QDiquAreaBind(q);
        //类别
        method.jq_QTypesBind(q);
        //绑定发布时间
        method.jq_QTimeBind(q);
        //绑定发布时间范围
        method.jq_QTimeRangeBind(q);
        //历史绑定
        method.jq_HistoryBind(q);
        //搜索范围
        method.jq_QTagBind(q);
        //搜索模式
        method.jq_QModBind(q);
        //排除词范围
        method.jq_QPaiChuTagBind(q);
        //相关词范围
        method.jq_QXiangGuanTagBind(q);
        //绑定项目金额
        method.jq_ZbjeBind(q);
        //绑定资质证书
        method.jq_ZzzsBind(q);
        //绑定采购方式
        method.jq_cgfsBind(q);
        //绑定资金来源
        method.jq_zjlyBind(q);
        //绑定评标办法
        method.jq_pbbfBind(q);
        //绑定资质证书
        method.jq_zzzsBind(q);
        //绑定排除词
        method.jq_excodeBind(q);
        //绑定相关词
        method.jq_kwordhBind(q);
    },
    //绑定地区
    jq_QDiqusBind: function (qData) {
        jq_didu_fn.c_qingkong();
        $("#jq_show_diquArea").attr({ pid: 0, pname: "" }).html("").hide();
        if (qData.diqu && qData.diqu != "") {
            var arr = [];//选中一级地区tid筛选条件数组
            var arrs = [];//选中一级地区id数组
            if (qData.diqu != "0")
                arrs = qData.diqu.split(',');

            var showDiqus = [];
            var searParams = [];
            if (arrs.length > 0) {
                showDiqus.push('<li tid="0"><a href="javascript:;" title="全国">全国</a></li>')
                for (var i = 0; i < arrs.length; i++) {
                    var currProvinceObj = province.filter(function (x) {
                        return x.id == arrs[i];
                    });
                    if (currProvinceObj && currProvinceObj.length > 0) {
                        var provinceId = currProvinceObj[0].id, provinceCode = currProvinceObj[0].code, provinceName = currProvinceObj[0].name;
                        var yxtjText = provinceName, cityName = "";
                        arr.push("[tid=" + provinceId + "]");
                        var provinceCodeArry = [],//选中省份code数组
                            cityCodeArry = [],//选中城市code数组
                            currCityObj = [];//选中城市对象数组
                        if (provinceCode && provinceCode != "")
                            provinceCodeArry = provinceCode.split(",");
                        if (qData.areacode && qData.areacode != "")
                            cityCodeArry = qData.areacode.split(",");
                        if (provinceCodeArry.length > 0) {
                            if (cityCodeArry && cityCodeArry.length > 0) {
                                for (var j = 0; j < provinceCodeArry.length; j++) {
                                    $(areas[provinceCodeArry[j]]).each(function (index, element) {
                                        if ($.inArray(element.k.toString(), cityCodeArry) > -1)
                                            currCityObj.push(element);
                                    });
                                }
                            }
                            if (currCityObj && currCityObj.length > 0) {
                                $(currCityObj).each(function (index, element) {
                                    cityName = element.v;
                                    if (cityName != "")
                                        yxtjText = provinceName + "-" + cityName;
                                    searParams.push('<li type="1" tid="' + provinceId + '" tcode="' + element.k + '"><a href="javascript:;" title="' + yxtjText + '"><span>' + yxtjText + '</span><img src="//img.bidcenter.com.cn/search/search/image/v3/shanchu.png" class="shanchu_city-icon"></a></li>');
                                });
                            } else {
                                searParams.push('<li type="1" tid="' + provinceId + '"><a href="javascript:;" title="' + yxtjText + '"><span>' + yxtjText + '</span><img src="//img.bidcenter.com.cn/search/search/image/v3/shanchu.png" class="shanchu-icon"></a></li>');
                            }
                        }
                        showDiqus.push('<li tid="' + provinceId + '" class="active"><a href="javascript:;" title="' + provinceName + '">' + provinceName + '</a></li>');
                    }
                }
            } else
                showDiqus.push('<li tid="0"><a href="javascript:;" title="全国" class="active" >全国</a></li>')

            $(province).each(function (i, e) {
                if ($.inArray(e.id.toString(), arrs) == -1) {
                    showDiqus.push('<li tid="' + e.id + '"><a href="javascript:;" title="' + e.name + '">' + e.name + '</a></li>');
                }
            });

            if (showDiqus.length > 0) {
                $("#jq_intro_diqu li").remove();
                $("#jq_intro_diqu").html(showDiqus.join(''))
            }

            jq_didu_fn.s_xuanzhong(arr);

            //区县绑定
            if (arrs.length == 1)
                method.jq_QDiquAreaHtmlBind(arrs[0]);

            //绑定已选条件
            $("#jq_search_params ul.yixuantiaojian-list,#jq_search_params2 ul.yixuantiaojian-list").append(searParams.join(''));
            $(".yixuantiaojian").show();
        } else
            jq_didu_fn.s_xuanzhong();
    },
    //单选-小地区绑定
    jq_QDiquAreaHtmlBind: function (pid) {
        //var areaCurr = diqus[pid];
        //var diquAreaHtml = [];
        //$(areaCurr.c).each(function () {
        //    diquAreaHtml.push('<a href="javascript:;" title="' + this + '" >' + this + '</a>')
        //});
        //$("#jq_show_diquArea").attr({ pid: pid, pname: areaCurr.b }).html(diquAreaHtml.join('\n')).show();
        var currProvinceObj = province.filter(function (x) {
            return x.id == pid;
        });
        if (currProvinceObj && currProvinceObj.length > 0) {
            var codeArry = currProvinceObj[0].code.split(","), areaCurr = [];
            $(codeArry).each(function (i, e) {
                if (areas[e] && areas[e] != undefined)
                    areaCurr.push(areas[e]);
            });
            //var areaCurr = areas[currProvinceObj[0].code];
            if (areaCurr && areaCurr.length > 0) {
                var diquAreaHtml = [];
                $(areaCurr).each(function (index, element) {
                    $(element).each(function (i, e) {
                        diquAreaHtml.push('<a href="javascript:;" title="' + e.v + '" value="' + e.k + '" >' + e.v + '</a>');
                    })
                });
                $("#jq_show_diquArea").attr({ pid: pid, pname: currProvinceObj[0].name }).html(diquAreaHtml.join('\n')).show();
            }
        }
    },
    //多选-小地区绑定
    jq_QDiquAreaBind: function (q) {
        if (q.areacode && q.areacode != "") {
            var xdqArr = q.areacode.split(',');
            jq_didu_fn.s_xdqXuanzhong(xdqArr);
        }
    },
    //加载多选二级地区
    loadMulErjiDiqu: function () {
        for (var i = 0; i < province.length; i++) {
            var id = province[i].id, code = province[i].code;
            var codeArry = code.split(",");
            if (codeArry.length > 0) {
                var erjiHtml = [];
                erjiHtml.push('<div class="quyu-hover" pid="' + id + '">');
                erjiHtml.push('<div class="quyu-label"><a href="javascript:;" class="erji checkbox quanbu" value="">全部</a></div>');
                $(codeArry).each(function (index, element) {
                    if (areas[element]) {
                        var erji = areas[element];
                        $(erji).each(function (index, e) {
                            erjiHtml.push('<div class="quyu-label city"><a href="javascript:;" class="erji checkbox" value="' + e.k + '">' + e.v + '</a></div>');
                        });
                    }
                });
                erjiHtml.push('</div>');
                $("#jq_show_diqu ul li a.yiji[tid=" + id + "]").after(erjiHtml.join(' '));
            }
        }
        //for (var i = 1; i <= 34; i++) {
        //    if (diqus[i]) {
        //        var erji = diqus[i].c;
        //        if (erji && erji.length > 0) {
        //            var erjiHtml = [];
        //            erjiHtml.push('<div class="quyu-hover" pid="' + i + '">');
        //            erjiHtml.push('<div class="quyu-label"><a href="javascript:;" class="erji checkbox quanbu" value="">全部</a></div>');
        //            for (var j = 0; j < erji.length; j++) {
        //                erjiHtml.push('<div class="quyu-label city"><a href="javascript:;" class="erji checkbox" value="' + erji[j] + '">' + erji[j] + '</a></div>');
        //            }
        //            erjiHtml.push('</div>');
        //            $("#jq_show_diqu ul li a.yiji[tid=" + i + "]").after(erjiHtml.join(' '));
        //        }
        //    }
        //}
    },
    //绑定类别
    jq_QTypesBind: function (qData) {
        $("#jq_intro_type li").removeClass("active");
        var arr = [];
        var arrs = [];
        if (qData.type != "")
            arrs = qData.type.split(',');
        var searParams = [];
        for (var i = 0; i < arrs.length; i++) {
            var tId = arrs[i];
            arr.push("[tid=" + tId + "]");
            if (tId != undefined && tId != "" && types[tId]) {
                var tStr = types[tId].b;
                searParams.push('<li type="2" tid="' + tId + '"><a href="javascript:;" title="' + tStr + '"><span>' + tStr + '</span><img src="//img.bidcenter.com.cn/search/search/image/v3/shanchu.png" class="shanchu-icon"></a></li>');
            }
        }
        if (arr.length > 0) {
            //单选绑定
            $("#jq_intro_type li").filter(arr.join(',')).addClass("active");
            //多选绑定
            $("#jq_show_type ul li a").removeClass("active");
            $("#jq_show_type ul li a").filter(arr.join(',')).addClass("active");
        }
        else {
            $("#jq_intro_type li[tid='-1']").addClass("active");
        }
        if (searParams && searParams.length > 0) {
            //绑定已选条件
            $("#jq_search_params ul.yixuantiaojian-list,#jq_search_params2 ul.yixuantiaojian-list").append(searParams.join(''));
            $(".yixuantiaojian").show();
        }
    },
    //绑定时间
    jq_QTimeBind: function (q) {
        $("#jq_dvTime ul.search_days li").removeClass("active");
        if (q.dtrange < 2000) {
            $("#jq_dvTime ul.search_days li[tid=" + q.time + "]").addClass("active");
            if (parseInt(q.time) > 0) {
                var tStr = "";
                if (times[q.time])
                    tStr = times[q.time];
                else if (parseInt(q.time) > 2000)
                    tStr = q.time;
                if (tStr != "")
                    method.jq_addSearchParams(3, q.time, tStr);
            }
        }
    },
    //绑定搜索模式
    jq_QModBind: function (q) {
        $("#jq_dvMod ul li").removeClass("active").filter("[tid=" + q.mod + "]").addClass("active");
        var tStr = ssmss[q.mod];
        //2026-01-29再次修改逻辑，全文加附件并且模糊搜索时，去掉搜索条件优化建议
        if (q.tag == 0 && q.mod == 0)
            $(".search-empty-middle").hide();
        else {
            $(".search-empty-middle .remod").attr("tid", 0).text(ssmss[0]);
            $(".search-empty-middle").show();
        }
        if (q.mod && parseInt(q.mod) > 0) {
            method.jq_addSearchParams(5, q.mod, tStr);
        }
    },
    //绑定排除词范围
    jq_QPaiChuTagBind: function (q) {
        $("#jq_dvPaiChuCiTag ul li").removeClass("active").filter("[tid=" + q.paichutag + "]").addClass("active");
        if (q.paichutag && parseInt(q.paichutag) > 0) {
            var tStr = '排除词' + ssfws[q.paichutag]
            method.jq_addSearchParams(13, q.paichutag, tStr);
        }
    },
    //绑定相关词范围
    jq_QXiangGuanTagBind: function (q) {
        $("#jq_dvXiangGuanCiTag ul li").removeClass("active").filter("[tid=" + q.xiangguantag + "]").addClass("active");
        if (q.xiangguantag && parseInt(q.xiangguantag) > 0) {
            var tStr = '相关词' + ssfws[q.xiangguantag]
            method.jq_addSearchParams(14, q.xiangguantag, tStr);
        }
    },
    //绑定搜索范围
    jq_QTagBind: function (q) {
        $("#jq_dvTag ul li").removeClass("active").filter("[tid=" + q.tag + "]").addClass("active");
        var tStr = ssfws[q.tag];
        //2026-01-29再次修改逻辑，全文加附件并且模糊搜索时，去掉搜索条件优化建议
        if (q.tag == 0 && q.mod == 0)
            $(".search-empty-middle").hide();
        else {
            $(".search-empty-middle .retag").attr("tid", 0).text(ssfws[0]);
            $(".search-empty-middle").show();
        }
        if (q.tag && parseInt(q.tag) > 0) {
            method.jq_addSearchParams(4, q.tag, tStr);
        }
    },
    //采购方式绑定
    jq_cgfsBind: function (q) {
        if (!isLoadBase) return;
        if (q.ext_cgfs && q.ext_cgfs != "") {
            var tStr = baseData.cgfsList.filter(function (element) {
                return element.key == q.ext_cgfs;
            })[0].value;
            $("#jq_ddl_cgfs").prev().find('span').text(tStr);
            method.jq_addSearchParams(7, q.ext_cgfs, tStr);
        }
    },
    //资金来源绑定
    jq_zjlyBind: function (q) {
        if (!isLoadBase) return;
        if (q.ext_zjly && q.ext_zjly != "") {
            var tStr = baseData.zjlyList.filter(function (element) {
                return element.key == q.ext_zjly;
            })[0].value;
            $("#jq_ddl_zjly").prev().find('span').text(tStr);
            method.jq_addSearchParams(8, q.ext_zjly, tStr);
        }
    },
    //评标办法绑定
    jq_pbbfBind: function (q) {
        if (!isLoadBase) return;
        if (q.ext_pbbf && q.ext_pbbf != "") {
            var tStr = baseData.pbbfList.filter(function (element) {
                return element.key == q.ext_pbbf;
            })[0].value;
            $("#jq_ddl_pbbf").prev().find('span').text(tStr);
            method.jq_addSearchParams(9, q.ext_pbbf, tStr);
        }
    },
    //绑定资质证书
    jq_zzzsBind: function (q) {
        if (q.zzzs && q.zzzs != "") {
            afterLayui(function () {
                $("select[name='jq_ddl_zzzs']").siblings("div.layui-form-select").find('.layui-input').val(q.zzzs);
            });
            method.jq_addSearchParams(10, q.zzzs, q.zzzs);
        }
    },
    //绑定排除词
    jq_excodeBind: function (q) {
        if (q.excode != "") {
            if (!islogin) {
                return;
            }
            else if (!resultData.isFufei) {
                return;
            }
            else {
                var pccs = q.excode.split(',');
                if (pccs.length > 1) {
                    var searParams = [];
                    searParams.push('<li type="11" class="ddl_params"><a href="javascript:;" title="多个排除词"><span>多个排除词</span><img src="//img.bidcenter.com.cn/search/search/image/v3/shanchu.png" class="shanchu-icon"></a>');
                    searParams.push('<ul style="display:none;">');

                    for (var i = 0; i < pccs.length; i++) {
                        searParams.push('<li type="11" tid="' + pccs[i] + '" class="erji"><a href="javascript:;" title="' + pccs[i] + '"><span>' + pccs[i] + '</span><img src="//img.bidcenter.com.cn/search/search/image/v3/shanchu.png" class="shanchu-icon erji"></a></li>');
                    }
                    searParams.push('</ul>');
                    searParams.push('</li>');
                    //绑定已选条件
                    $("#jq_search_params ul.yixuantiaojian-list,#jq_search_params2 ul.yixuantiaojian-list").append(searParams.join(' '));
                    $(".yixuantiaojian").show();
                }
                else if (pccs.length > 0)
                    method.jq_addSearchParams(11, pccs[0], pccs[0], "排除词：");

                $(".paichuci-list").html('');
                for (var i = 0; i < pccs.length; i++) {
                    //绑定排除词选择项
                    $(".paichuci-list").append('<span class="paichuci"><span>' + pccs[i] + '</span><i onclick="method.removepaichuci(this,0)">×</i></span>');
                }

                $(".nowpaichuci").html(pccs.length);
                $(".paichuci-list-clear").css("display", "inline");
                if (pccs.length >= 5) {
                    $(".addpaichuci").attr("onclick", "").addClass("addpaichuci2");
                }
                else {
                    $(".addpaichuci").attr("onclick", "method.open_addpcc()").removeClass("addpaichuci2");
                }
            }
        }
        else {
            $(".nowpaichuci").html('0');
            $(".paichuci-list-clear").css("display", "none");
        }
    },
    //绑定相关词
    jq_kwordhBind: function (q) {
        if (q.kwordtagh != "") {
            if (!islogin) {
                return;
            }
            else if (!resultData.isFufei) {
                return;
            }
            else {
                var xgcs = q.kwordtagh.split(',');
                if (xgcs.length > 1) {
                    var searParams = [];
                    searParams.push('<li type="12" class="ddl_params"><a href="javascript:;" title="多个相关词"><span>多个相关词</span><img src="//img.bidcenter.com.cn/search/search/image/v3/shanchu.png" class="shanchu-icon"></a>');
                    searParams.push('<ul style="display:none;">');
                    for (var i = 0; i < xgcs.length; i++) {
                        searParams.push('<li type="12" tid="' + xgcs[i] + '" class="erji"><a href="javascript:;" title="' + xgcs[i] + '"><span>' + xgcs[i] + '</span><img src="//img.bidcenter.com.cn/search/search/image/v3/shanchu.png" class="shanchu-icon erji"></a></li>');
                    }
                    searParams.push('</ul>');
                    searParams.push('</li>');
                    //绑定已选条件
                    $("#jq_search_params ul.yixuantiaojian-list,#jq_search_params2 ul.yixuantiaojian-list").append(searParams.join(' '));
                    $(".yixuantiaojian").show();
                }
                else if (xgcs.length > 0)
                    method.jq_addSearchParams(12, xgcs[0], xgcs[0], "相关词：");

                $(".xiangguanci-list").html('');
                for (var i = 0; i < xgcs.length; i++) {
                    //绑定排除词选择项
                    $(".xiangguanci-list").append('<span class="xiangguanci"><span>' + xgcs[i] + '</span><i onclick="method.removexiangguanci(this,0)">×</i></span>');
                }

                $(".nowxiangguanci").html(xgcs.length);
                $(".xiangguanci-list-clear").css("display", "inline");
                if (xgcs.length >= 5) {
                    $(".addxiangguanci").attr("onclick", "").addClass("addxiangguanci2");
                }
                else {
                    $(".addxiangguanci").attr("onclick", "method.open_addxgc()").removeClass("addxiangguanci2");
                }
            }
        }
        else {
            $(".nowxiangguanci").html('0');
            $(".xiangguanci-list-clear").css("display", "none");
        }
    },
    //添加单选筛选条件
    jq_addSearchParams: function (type, tid, tStr, state) {
        var searParams = '<li type="' + type + '" tid="' + tid + '"><a href="javascript:;" title="' + tStr + '"><span>' + (state ? state : "") + tStr + '</span><img src="//img.bidcenter.com.cn/search/search/image/v3/shanchu.png" class="shanchu-icon"><div class="clear"></div> </a></li>';
        //绑定已选条件
        $("#jq_search_params ul.yixuantiaojian-list,#jq_search_params2 ul.yixuantiaojian-list").append(searParams);
        $(".yixuantiaojian").show();
    },
    //绑定时间范围筛选
    jq_QTimeRangeBind: function (q) {
        //var urlstime = method.getUrlParam('stime');
        //var urlendtime = method.getUrlParam('endtime');
        if (q.time != 0) {
            $("#txtStartTime").val(method.changeTime(q.stime));
            $("#txtEndTime").val(method.changeTime(q.endtime));
        }
    },
    //绑定项目金额
    jq_ZbjeBind: function (qData) {
        $("#jq_zhaobjine ul li").removeClass("active");
        if (qData.zbjefw > 0) {
            $("#jq_zhaobjine ul li[tid='" + qData.zbjefw + "']").addClass("active");
            var tStr = zbjes[qData.zbjefw]
            method.jq_addSearchParams(6, qData.zbjefw, tStr);
        }
        else
            $("#jq_zhaobjine ul li[tid='0']").addClass("active");
        if (qData.zbje_min > 0)
            $("#zbje_min").val(qData.zbje_min);
        else
            $("#zbje_min").val("");
        if (qData.zbje_max > 0 && qData.zbje_max < 999999999999)
            $("#zbje_max").val(qData.zbje_max);
        else
            $("#zbje_max").val("");
    },
    //绑定历史年份
    jq_HistoryBind: function (q) {
        if ($("#jq_historyData li[value='" + q.dtrange + "']").length > 0)
            $("#jq_historyData option[value='" + q.dtrange + "']").attr('selected', 'selected');
        else
            $("#jq_historyData option[value='']").attr('selected', 'selected');
    },
    //绑定资质证书
    jq_ZzzsBind: function (q) {
        if (q.zzzs && q.zzzs != "")
            $("#jq_ddl_zzzs option:contains('" + q.zzzs + "')").attr("selected", true)
    },
    //多选-地区确定
    jq_diqus_sure: function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        if (!$("#jq_show_diqu ul li a.yiji.quanguo").hasClass("active")) {
            var arrys = [];//一级地区
            var arryXdqs = [];//二级地区
            var arryCodes = [];//二级地区code
            //获取一级地区
            $("#jq_show_diqu ul li a.yiji.active:not(.quanguo,.quyu),#jq_show_diqu ul li a.yiji.active2:not(.quanguo,.quyu)").each(function (item, element) {
                var dqId = $(element).attr("tid");
                if ($.inArray(dqId, arrys) < 0)
                    arrys.push(dqId);
            });

            //获取二级地区
            $("#jq_show_diqu ul li a.erji.active:not(.quanbu)").each(function (item, element) {
                var xdqItem = $.trim($(element).text());
                if ($.inArray(xdqItem, arryXdqs) < 0)
                    arryXdqs.push(xdqItem);
                var xdqCode = $.trim($(element).attr("value"));
                if ($.inArray(xdqCode, arryCodes) < 0)
                    arryCodes.push(xdqCode);
                var pid = $(element).parents(".quyu-hover").attr("pid");
                if ($.inArray(pid, arrys) < 0)
                    arrys.push(pid);
            });

            var dqIds = arrys.sort().join(',');
            var xdqStr = arryXdqs.sort().join(',');
            var xdqCodeStr = arryCodes.sort().join(',');

            if (jq_searchData.diqu != dqIds)
                jq_searchDataNew.diqu = dqIds;

            if (jq_searchDataNew.diquArea != xdqStr)
                jq_searchDataNew.diquArea = xdqStr;

            if (jq_searchDataNew.areacode != xdqCodeStr)
                jq_searchDataNew.areacode = xdqCodeStr;
        } else {
            jq_searchDataNew.diqu = "";
            jq_searchDataNew.diquArea = "";
            jq_searchDataNew.areacode = "";
        }
        //筛选前 修改默认条件
        method.searchNewFieldInit();
        method.jq_search();
        jq_didu_fn.s_default();
    },
    //多选-类别确定
    jq_types_sure: function () {
        var arrys = [];
        if ($("#jq_show_type ul li a").length != $("#jq_show_type ul li a.active").length) {
            $("#jq_show_type ul li a.active").each(function (item, element) {
                arrys.push($(element).attr("tid"));
            });
        }
        var typeStr = arrys.sort().join(',')
        if (jq_searchData.type != typeStr) {
            jq_searchDataNew.type = typeStr;

            //筛选前 修改默认条件
            method.searchNewFieldInit();
            method.jq_search();
        }
        jq_type_fn.s_default();
    },
    //删除选中地区
    jq_check_checkedDiqu: function () {
        if ($("#jq_search_params ul li[type='1']").length == 0) {
            //移除所有当前选中项
            $("#jq_intro_diqu li").removeClass("active");
            $("#jq_show_diqu ul li a").removeClass("active");
            //直接跳转
            jq_searchDataNew.diqu = "";
            //method.jq_search();
        }
    },
    //删除选中类别
    jq_check_checkedType: function () {
        if ($("#jq_search_params ul li[type='2']").length == 0) {
            //移除所有当前选中项
            $("#jq_intro_type li").removeClass("active");
            $("#jq_show_type ul li a").removeClass("active");
            jq_searchDataNew.type = "";
            //method.jq_search();
        }
    },
    //获取URL中的参数
    getUrlParam: function (name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
        var r = window.location.search.substr(1).match(reg);  //匹配目标参数
        if (r != null) return unescape(r[2]); return null; //返回参数值
    },
    changeTime: function (time) {
        var t = time.slice(6, 19)
        var NewDtime = new Date(parseInt(t));
        return method.formatDate(NewDtime);
    },
    //Date(1528953453022+0800)/ 时间格式转换
    formatDate: function (dt, type) {
        var year = dt.getFullYear();
        var month = dt.getMonth() + 1;
        var date = dt.getDate();
        var hour = dt.getHours();
        var minute = dt.getMinutes();
        var second = dt.getSeconds();
        switch (type) {
            case 1:
                return year + "-" + month + "-" + date + " " + hour + ":" + minute + ":" + second;
                break;
            default:
                return year + "-" + method.formatNum(month) + "-" + method.formatNum(date);
                break;
        }
    },
    //格式化数字
    formatNum: function (num) {
        return num >= 10 ? num : "0" + num;
    },
    //招标金额查询
    jq_search_zbje: function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "项目金额");
            return;
        } else if ($.trim($("#zbje_min").val()) == "" || $.trim($("#zbje_max").val()) == "") {
            method.commonAlert("请输入正确的招标金额范围");
            return;
        } else {
            var zbje_min = parseFloat($.trim($("#zbje_min").val()));
            var zbje_max = parseFloat($.trim($("#zbje_max").val()));
            if (zbje_min > zbje_max) {
                $("#zbje_min").val(zbje_max);
                $("#zbje_max").val(zbje_min);
            }
        }
        jq_searchDataNew.zbjefw = 0;
        jq_searchDataNew.zbje_min = $.trim($("#zbje_min").val());
        jq_searchDataNew.zbje_max = $.trim($("#zbje_max").val());
        method.jq_search();
    },
    //回车搜索
    jq_search_keydown: function (event, element) {
        if (event.keyCode == 13) {
            var domId = $(element).prop("id");
            switch (domId) {
                case "jq_search_keyword":
                    var kwd = $.trim($("#jq_search_keyword").val());
                    if ($.fn.searchObj) {
                        var filterArry = $.fn.searchObj.objArry.filter(function (x) {
                            return x.tag == $.fn.searchObj.currTag;
                        });
                        if (filterArry && filterArry.length > 0) {
                            if ($.fn.searchObj.currTag == 0) {
                                if (kwd != "" || resultData.isFufei)
                                    location.href = "/search?keywords=" + encodeURIComponent(kwd);
                                else
                                    $("#jq_search_keyword").focus();
                            }
                            else if (kwd != "")
                                window.open(filterArry[0].href + encodeURIComponent(kwd));
                            else
                                window.open(filterArry[0].href.split('?')[0]);
                        }
                    }
                    break;
                default:
                    method.jq_rapeat_search(domId);
                    break;
            }
        }
    },
    //重新搜索
    jq_rapeat_search: function (domId, second) {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "已选条件搜索");
            return;
        }
        currInputKwd = $.trim($("#" + domId).val());
        if (currInputKwd != "") {
            if (second)
                jq_searchDataNew.secondKwds = currInputKwd;
            else {
                jq_searchDataNew.keywords = currInputKwd;
                jq_searchDataNew.secondKwds = '';
            }
            method.jq_search();
        }
    },
    //筛选前 修改默认条件
    searchNewFieldInit: function () {
        if (jq_searchData.dtrange < 2000) {
            if (resultData.Permission < 2)//新筛选时免费会员将时间改回默认
                jq_searchDataNew.time = 0;
            jq_searchDataNew.dtrange = 4;//信息库默认成当前数据库
            jq_searchDataNew.page = 1;
        }
    },
    //搜索前执行
    jq_searchBefore: function (backtop) {
        //回到顶部
        if (backtop == undefined || backtop)
            method.backTop();
        //关闭其它二级地区
        $("#jq_show_diqu ul li a.diqu_text").removeClass("current");
        $("#jq_show_diqu ul li a.yiji.checkbox").show();
        $("#jq_show_diqu ul li .quyu-hover").hide();
    },
    //重新搜索
    jq_research: function () {
        var nTag = parseInt($(".search-empty-middle .retag").attr("tid"));
        var nMod = parseInt($(".search-empty-middle .remod").attr("tid"));
        if (nTag == 2) {
            if (!islogin) {
                tankLogin();
                return;
            } else if (!isWanshan && tankWanshan()) {
                return;
            } else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "搜索不包含附件");
                return;
            }
        } else if (nMod == 1) {
            if (!islogin) {
                tankLogin();
                return;
            } else if (!isWanshan && tankWanshan()) {
                return;
            } else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "精准搜索");
                return;
            }
        }
        jq_searchDataNew.tag = nTag;
        jq_searchDataNew.mod = nMod;
        method.jq_QTagBind(jq_searchDataNew);
        method.jq_QModBind(jq_searchDataNew);
        //筛选前 修改默认条件
        method.searchNewFieldInit();
        method.jq_search();
    },
    //初始化推荐信息
    jq_initTjInfo: function () {
        tjKeyword = "";
        jq_searchDataNew.currDiqu = "";
        jq_searchDataNew.currCity = "";
        jq_searchDataNew.currCityCode = "";
        $("#searchListArea,.tjxm-gjc").html("");
        $(".more_prject").attr('javascript:;');
        $(".tuijianxiangmu-title").hide();
    },
    //执行搜索
    //callback：回调函数
    //reTjType：是否重置tjType
    //initTjInfo：是否初始化推荐信息
    //backtop：是否回到顶部
    jq_search: function (callback, reTjType, initTjInfo, backtop) {
        if (reTjType == undefined || reTjType) tjType = 0;
        if (initTjInfo == undefined || initTjInfo) method.jq_initTjInfo();
        var params = {};
        if (isfirst) {
            params = interface_params_json.searchParamsJson;
            searchParams = searchold_params_json;
            //添加搜索记录
            addlocalStorageBySearch(decodeURIComponent(params.keywords));
        }
        else {
            var params = {
                from: 6137,
                guid: guid,
                location: 6138,
                token: token,
                next_token: nextToken
            };
            searchParams = [];
            //跳转前验证
            //--如果关键词为空情况下
            if (jq_searchDataNew.keywords == "" && jq_searchDataNew.type != "0" && !isFufei)
                location.href = "/";

            //关键词
            if (jq_searchDataNew.keywords != "") {
                params.keywords = encodeURIComponent(jq_searchDataNew.keywords);
                if (tjType == 0)
                    searchParams.push("keywords=" + params.keywords);

                //添加搜索记录
                addlocalStorageBySearch(jq_searchDataNew.keywords);
            }
            //二次查询关键词
            if (jq_searchDataNew.secondKwds != undefined && jq_searchDataNew.secondKwds != "") {
                params.secondKwds = encodeURIComponent(jq_searchDataNew.secondKwds);
                params.deftag = 1;
            }

            //地区
            if (jq_searchDataNew.diqu != "") {
                params.diqu = jq_searchDataNew.diqu;
                searchParams.push("diqu=" + params.diqu);
            }

            //地区区县
            if (jq_searchDataNew.diquArea != "") {
                params.darea = encodeURIComponent(jq_searchDataNew.diquArea.replace("市", ""));
                searchParams.push("darea=" + params.darea);
            }

            if (jq_searchDataNew.areacode != "") {
                params.areacode = jq_searchDataNew.areacode;
                searchParams.push("areacode=" + params.areacode);
            }

            //自定义时间判断，如果用户的时间选项为全部，时间框里面有值的时候，按照时间框里面来进行查询
            if ($.trim($("#txtStartTime").val()) != "" && $.trim($("#txtEndTime").val()) != "" && jq_searchDataNew.time == 0)
                jq_searchDataNew.time = 5;

            //历史信息
            if (jq_searchDataNew.dtrange > 2000) {
                params.dtrange = jq_searchDataNew.dtrange;
                searchParams.push("dtrange=" + params.dtrange);
            }
                //时间或时间段
            else {
                if (jq_searchDataNew.time > 0) {
                    params.time = jq_searchDataNew.time;
                    searchParams.push("time=" + params.time);
                    if (jq_searchDataNew.time == 5) {
                        jq_searchDataNew.startTime = $.trim($("#txtStartTime").val());
                        jq_searchDataNew.endTime = $.trim($("#txtEndTime").val());
                        //时间范围筛选-开始时间
                        params.stime = jq_searchDataNew.startTime;
                        searchParams.push("stime=" + params.stime);
                        //时间范围筛选-结束时间
                        params.endtime = jq_searchDataNew.endTime;
                        searchParams.push("endtime=" + params.endtime);
                    }
                }
            }

            //类型
            if (jq_searchDataNew.type != "" && jq_searchDataNew.type != "-1") {
                params.type = jq_searchDataNew.type;
                searchParams.push("type=" + params.type);
            }

            //搜索范围
            if (jq_searchDataNew.tag != 0) {
                params.tag = jq_searchDataNew.tag;
                searchParams.push("tag=" + params.tag);
            }

            //排除词范围
            if (jq_searchDataNew.paichutag != 0) {
                params.paichutag = jq_searchDataNew.paichutag;
                searchParams.push("paichutag=" + params.paichutag);
            }

            //相关词范围
            if (jq_searchDataNew.xiangguantag != 0) {
                params.xiangguantag = jq_searchDataNew.xiangguantag;
                searchParams.push("xiangguantag=" + params.xiangguantag);
            }

            //搜索模式
            params.mod = jq_searchDataNew.mod;
            searchParams.push("mod=" + params.mod);

            //信息大行业类型
            if (jq_searchDataNew.sort != "" && jq_searchDataNew.sort != 0) {
                params.sort = jq_searchDataNew.sort;
                searchParams.push("sort=" + params.sort);
            }

            if (islogin && resultData.isFufei) {
                if (jq_searchDataNew.zbjefw != 0) {
                    params.zbjefw = jq_searchDataNew.zbjefw;
                    searchParams.push("zbjefw=" + params.zbjefw);
                }
                if (jq_searchDataNew.zbje_min != 0) {
                    params.zbje_min = jq_searchDataNew.zbje_min;
                    searchParams.push("zbje_min=" + params.zbje_min);
                }
                if (jq_searchDataNew.zbje_max != 0) {
                    params.zbje_max = jq_searchDataNew.zbje_max;
                    searchParams.push("zbje_max=" + params.zbje_max);
                }
                if (jq_searchDataNew.ext_cgfs != 0) {
                    params.ext_cgfs = jq_searchDataNew.ext_cgfs;
                    searchParams.push("ext_cgfs=" + params.ext_cgfs);
                }
                if (jq_searchDataNew.ext_zjly != 0) {
                    params.ext_zjly = jq_searchDataNew.ext_zjly;
                    searchParams.push("ext_zjly=" + params.ext_zjly);
                }
                if (jq_searchDataNew.ext_pbbf != 0) {
                    params.ext_pbbf = jq_searchDataNew.ext_pbbf;
                    searchParams.push("ext_pbbf=" + params.ext_pbbf);
                }
                if (jq_searchDataNew.zzzs != "") {
                    params.zzzs = encodeURIComponent(jq_searchDataNew.zzzs);
                    searchParams.push("zzzs=" + params.zzzs);
                }
                //排除关键词
                if (jq_searchDataNew.excode != "") {
                    params.excode = encodeURIComponent(jq_searchDataNew.excode);
                    searchParams.push("excode=" + params.excode);
                }
                //相关词
                if (jq_searchDataNew.kwordtagh != "") {
                    params.kwordtagh = encodeURIComponent(jq_searchDataNew.kwordtagh);
                    searchParams.push("kwordtagh=" + params.kwordtagh);
                }
            }
            else {
                jq_searchDataNew.excode = '';
                jq_searchDataNew.kwordtagh = '';
            }

            //关键词限制
            if (jq_searchDataNew.limitkwd > 0) {
                params.limitkwd = 2;
                searchParams.push("limitkwd=" + params.limitkwd);
            }

            //地区标识
            if (jq_searchDataNew.dqbs == "1") {
                params.dqbs = 1;
                searchParams.push("dqbs=" + params.dqbs);
            }
            //页码
            if (!variate.isPageLoad)
                jq_searchDataNew.page = 1;
            if (jq_searchDataNew.page && jq_searchDataNew.page > 1) {
                params.page = jq_searchDataNew.page;
                searchParams.push("page=" + params.page);
            }

            if (tjType > 0) {
                params.pagesize = 10;//每页条数
                params.secondQuery = 1;//二次查询
            }

            //招标金额、中标金额、工程造价范围
            if (jq_searchDataNew.zbjefw > 0)
                params.zbjefw = jq_searchDataNew.zbjefw;

            if (jq_searchDataNew.zbje_min != undefined && jq_searchDataNew.zbje_max != undefined && jq_searchDataNew.zbje_min != "" && jq_searchDataNew.zbje_max != "") {
                params.zbje_min = parseInt(jq_searchDataNew.zbje_min) * 10000;
                params.zbje_max = parseInt(jq_searchDataNew.zbje_max) * 10000;
            }
            //采购方式
            if (jq_searchDataNew.ext_cgfs && jq_searchDataNew.ext_cgfs != "")
                params.ext_cgfs = jq_searchDataNew.ext_cgfs;
            //资金来源
            if (jq_searchDataNew.ext_zjly && jq_searchDataNew.ext_zjly != "")
                params.ext_zjly = jq_searchDataNew.ext_zjly;
            //评标办法
            if (jq_searchDataNew.ext_pbbf && jq_searchDataNew.ext_pbbf != "")
                params.ext_pbbf = jq_searchDataNew.ext_pbbf;
            //资质证书
            if (jq_searchDataNew.zzzs && jq_searchDataNew.zzzs != "")
                params.zzzs = encodeURIComponent(jq_searchDataNew.zzzs);
        }
        //获取推荐信息参数
        if (tjType > 0 && keywordsSplitArry.length > 0) {//根据拆分词获取有效关键词
            tjType = 2;
            params.splitKwd = keywordsSplitArry.join(',');
            method.validKeywords(params, function () {
                if (resultTjData && resultTjData.length > 0) {
                    //绑定有效关键词html标签
                    var tagArry = [];
                    for (var i = 0; i < resultTjData.length; i++) {
                        var act = resultTjData[i] == currTjKwd ? 'class="active"' : '';
                        tagArry.push('<li ' + act + '>' + resultTjData[i] + '</li>');
                    }
                    $(".tjxm-gjc").html(tagArry.join(''));
                    //判断当前搜索的拆分词是否为有效关键词，如果不是，则默认搜索第一个有效关键词
                    tjType = 1;
                    var hasCurrKwd = resultTjData.filter(function (x) {
                        return x == currTjKwd;
                    }).length > 0;
                    if (!hasCurrKwd) {
                        currTjKwd = resultTjData[0];
                        $(".tjxm-gjc li:contains(" + currTjKwd + ")").addClass('active');
                    }
                    $(".more_prject").attr("href", "/search?keywords=" + encodeURIComponent(currTjKwd));
                    tjKeyword = currTjKwd;
                }
            });
        } else if (tjType > 0) //无拆分词
            tjType = 2;

        //更新推荐信息搜索参数
        if (tjType == 2) {
            //params = { from: 6137, guid: guid, location: 6138, token: token };
            //var currDiqu = diqusJson.filter(function (x) {
            //    return x.b == currProvince;
            //});
            //if (currDiqu && currDiqu.length > 0)
            //    diquid = currDiqu[0].id;
            var currProvinceObj = province.filter(function (x) {
                return x.name == currProvince;
            });
            if (currProvinceObj && currProvinceObj.length > 0) {
                jq_searchDataNew.keywords = "";
                jq_searchDataNew.currDiqu = currProvinceObj[0].id;
                jq_searchDataNew.currCity = currCity;
                jq_searchDataNew.currCityCode = "";
                var codeArry = currProvinceObj[0].code.split(",");
                if (codeArry.length > 0) {
                    for (var i = 0; i < codeArry.length; i++) {
                        if (areas[codeArry[i]]) {
                            var currCityObj = areas[codeArry[i]].filter(function (x) {
                                return x.v.replace("市", "") == currCity;
                            });
                            if (currCityObj && currCityObj.length > 0) {
                                jq_searchDataNew.currCityCode = currCityObj[0].k;
                                break;
                            }

                        }
                    }
                }
            }
        }
        if (tjType > 0 && (tjKeyword != "" || (jq_searchDataNew.currDiqu && jq_searchDataNew.currDiqu != ""))) {
            params.keywords = encodeURIComponent(tjKeyword);
            params.diqu = jq_searchDataNew.diqu;
            params.darea = encodeURIComponent(jq_searchDataNew.diquArea.replace("市", ""));
            params.areacode = jq_searchDataNew.areacode;
            if (jq_searchDataNew.currDiqu && jq_searchDataNew.currDiqu != "")
                params.currDiqu = jq_searchDataNew.currDiqu;
            if (jq_searchDataNew.currCity && jq_searchDataNew.currCity != "")
                params.currCity = encodeURIComponent(jq_searchDataNew.currCity.replace("市", ""));
            if (jq_searchDataNew.currCityCode && jq_searchDataNew.currCityCode != "")
                params.currCityCode = jq_searchDataNew.currCityCode;
        }
        params.vtime = new Date().getTime();
        console.log("执行搜索前：" + new Date());
        var index;
        $.ajax({
            type: "POST",
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/search/GetSearchProHandler.ashx"),
            data: params,
            timeout: 20000,
            dataType: "text",
            beforeSend: function () {
                method.jq_searchBefore(backtop);
                isbinddata = false;
                //显示加载动画
                if (!isfirst || tjType > 0) {
                    if (layerisload)
                        index = layer.load(1, {
                            shade: [0.1, '#000']
                        });
                    else {
                        var layertimer0 = setInterval(function () {
                            console.log(new Date());
                            if (layerisload && !isbinddata) {
                                index = layer.load(1, {
                                    shade: [0.1, '#000']
                                });
                                clearInterval(layertimer0);
                            } else if (isbinddata)
                                clearInterval(layertimer0);
                        }, 30);
                    }
                }
                //更新地址栏url
                if (tjType == 0) {
                    //2026-01-22 jianyisousuo->search-empty
                    $(".search-empty").hide();
                    try {
                        var currUrl = (location.origin == undefined ? "" : location.origin) + location.pathname;
                        if (searchParams.length > 0)
                            currUrl += "?" + searchParams.join('&');
                        history.pushState(null, null, currUrl);
                    } catch (err) {
                    }
                }
                console.log("执行搜索时：" + new Date());
            },
            success: function (res) {
                method.bindSearchData(index, res, params, callback);
            },
            error: function (e) {
                layer.msg("网络错误，请重试");
            }
        });
        if (isfirst) {
            timer.search = setInterval(function () {
                $(".loadding_text").text("数据正在加载，请稍后" + (timer.searchIndex % 2 == 0 ? "..." : ""));
                timer.searchIndex += 1;
            }, 1000);
        }
    },
    //绑定搜索结果
    bindSearchData: function (index, res, params, callback) {
        console.log("执行搜索成功：" + new Date());
        clearInterval(timer.search);
        if (!isfirst) {
            isbinddata = true;
            if (index) layer.close(index);
        }
        if (res) {
            var data = method.AESDecrypt(res);
            if (data) {
                if (data.ret) {
                    if (data.other2) {
                        resultData = data.other2;

                        //页面元素显示状态
                        try {
                            var showzip = ziptag;
                            if (showzip) {
                                $(".exprot_zip").show();
                            } else {
                                //>>导出ZIP功能
                                if ($.inArray(resultData.Permission, [4, 6, 7, 9, 35]) > -1 || (userinfo && userinfo.id == '523275'))//VIP会员和bidcentertest有导出权限
                                    $(".exprot_zip").show();
                                else
                                    $(".exprot_zip").hide();
                            }
                        } catch (e) {
                            //>>导出ZIP功能
                            if ($.inArray(resultData.Permission, [4, 6, 7, 9, 35]) > -1 || (userinfo && userinfo.id == '523275'))//VIP会员和bidcentertest有导出权限
                                $(".exprot_zip").show();
                            else
                                $(".exprot_zip").hide();
                        }

                        if (!(tjType > 0)) {
                            //数据绑定
                            jq_searchData = eval('(' + resultData.pageSearchJson + ')');
                            jq_searchDataNew = eval('(' + resultData.pageSearchJson + ')');
                        }

                        nextToken = "";
                        //金额单位转换
                        if (jq_searchData) {
                            if (jq_searchData.zbje_min && jq_searchData.zbje_min > 0) {
                                jq_searchData.zbje_min = jq_searchData.zbje_min / 10000;
                                jq_searchDataNew.zbje_min = jq_searchDataNew.zbje_min / 10000;
                            }
                            if (jq_searchData.zbje_max && jq_searchData.zbje_max > 0 && jq_searchData.zbje_max < 999999999999) {
                                jq_searchData.zbje_max = jq_searchData.zbje_max / 10000;
                                jq_searchDataNew.zbje_max = jq_searchDataNew.zbje_max / 10000;
                            } else {
                                jq_searchData.zbje_max = 0;
                                jq_searchDataNew.zbje_max = 0;
                            }
                        }
                        //弹框展示
                        if (!islogin && isfirst) {
                            setTimeout(function () {
                                isEffectTank = true;
                                tankLogin();
                            }, 2000);
                        }
                        else if (!isWanshan && (isfirst || jq_searchData.page > 1)) {
                            isEffectTank = true;
                            tankWanshan();
                        }
                        else if (!resultData.isFufei && jq_searchData.page > 10) {
                            isEffectTank = true;
                            method.showAllowTank(".allow_mianfei", "更多信息");
                        }
                        isLoadBase = true;
                        //绑定页面搜索条件
                        method.jq_QDataBind(jq_searchData);
                        //加载搜索结果列表
                        if (resultData.listData) {
                            $(".loadding_area").hide();
                            if (tjType > 0) {//如果为推荐信息
                                $(".ssjg-top_tongji.has_data,.ssjg-wrap_dingyue,.ssjg-wrap_caozuo").hide();//隐藏“为您查询到***有关n条信息”“去订阅”“导出”
                                //2026-01-22 jianyisousuo->search-empty
                                $(".ssjg-top_tongji.no_data,.search-empty,.tuijianxiangmu-title").show();//显示“暂未查询到***有关的信息”“建议搜索”“推荐项目”
                                resultData.listData.ckhide = 1;//去掉复选框
                                if (tjType == 2) {
                                    $(".tuijianxiangmu-title-right").hide();//隐藏“推荐项目-更多项目”
                                    $(".keywords_jianyi").html('<span class="red">重新搜索关键词</span>');//“建议搜索”显示重新搜索关键词
                                } else {
                                    $(".tuijianxiangmu-title-right").show();//显示“推荐项目-更多项目”
                                    $(".keywords_jianyi").html('<span class="red">' + jianyiKwdArry.join('、') + '</span>相关关键词');//“建议搜索”显示拆分关键词
                                }
                            } else {
                                //$(".ssjg-top_tongji.has_data,.ssjg-wrap_dingyue,.ssjg-wrap_caozuo").show();//显示“为您查询到***有关n条信息”“去订阅”“导出”
                                $(".ssjg-top_tongji.has_data,.ssjg-wrap_caozuo").show();
                                //2026-01-22 jianyisousuo->search-empty
                                $(".ssjg-top_tongji.no_data,.search-empty,.tuijianxiangmu-title").hide();//隐藏“暂未查询到***有关的信息”“建议搜索”“推荐项目”
                                isfirst = false;
                            }
                            afterLayui(function () {
                                method.loadListData(resultData.listData);//加载列表数据html
                                if (tjType == 0)
                                    method.loadPage("listPage", resultData);//加载分页信息html
                            });
                            method.changePageStatus(true);//列表区域正常显示
                            if (tjType > 0) $("#listPage").hide();
                            jq_searchDataNew.keywords = currInputKwd;
                            console.log("绑定列表成功：" + new Date());
                        }
                        else if (tjType == 0) {// && (jq_searchData.tag > 0 || jq_searchData.mod > 0)
                            //2026-01-27恢复推荐信息，全文加附件并且模糊搜索时，去掉推荐信息逻辑，直接显示未查询到信息
                            //2026-01-29再次修改逻辑，只要无数据，就显示推荐信息
                            isfirst = false;
                            tjType = 2;
                            keywordsSplitArry = [];
                            //拼接拆分关键词
                            if (resultData.keywordsSplitArry && resultData.keywordsSplitArry.length > 0) {
                                jianyiKwdArry = [];
                                for (var i = 0; i < resultData.keywordsSplitArry.length; i++) {
                                    jianyiKwdArry.push('<a href="/search?keywords=' + encodeURIComponent(resultData.keywordsSplitArry[i]) + '" class="red">' + resultData.keywordsSplitArry[i] + '</a>');
                                }
                                $(".keywords_jianyi").html('<span class="red">' + jianyiKwdArry.join('、') + '</span>相关关键词');//“建议搜索”显示拆分关键词
                                keywordsSplitArry = resultData.keywordsSplitArry;
                            }
                            method.jq_search(undefined, false);//通过拆分关键词获取有效关键词，然后通过有效关键词获取推荐项目
                        } else {
                            //2026-01-22去掉推荐信息逻辑，直接显示未查询到信息
                            isfirst = false;
                            $(".loadding_area").hide();//隐藏“加载中”动图
                            $(".ssjg-top_tongji.has_data,.ssjg-wrap_dingyue,.ssjg-wrap_caozuo").hide();//隐藏“为您查询到***有关n条信息”“去订阅”“导出”
                            $(".ssjg-top_tongji.no_data").show();//显示“暂未查询到***有关的信息”“建议搜索”
                            method.changePageStatus(false, true);

                            //$(".loadding_area").hide();//隐藏“加载中”动图
                            //if (tjType == 1) {
                            //    $(".ssjg-top_tongji.has_data,.ssjg-wrap_dingyue,.ssjg-wrap_caozuo").hide();//隐藏“为您查询到***有关n条信息”“去订阅”“导出”
                            //    $(".ssjg-top_tongji.no_data").show();//显示“暂未查询到***有关的信息”“建议搜索”
                            //} else {
                            //    //$(".ssjg-wrap_dingyue,.ssjg-wrap_caozuo").show();
                            //    $(".tuijianxiangmu-title").hide();//隐藏“推荐项目”
                            //    $(".keywords_jianyi").html('<span class="red">重新搜索关键词</span>');//“建议搜索”显示重新搜索关键词
                            //}
                            //method.changePageStatus(false, true);//列表区域显示空数据
                        }
                        if (jq_searchData.keywords != "") {
                            var totalcount = resultData.realInfoCount;
                            if (resultData.optimize && $.inArray('totalcount', resultData.optimize) > -1)
                                totalcount = `约${resultData.realInfoCount}`;
                            $(".result_count").text(totalcount);
                            if (jq_searchData.keywords == "")
                                $(".has_keywords").hide();//隐藏“为您查询到***有关n条信息”中的“***”
                        }
                        else
                            $(".ssjg-top_tongji").hide();//隐藏“为您查询到***有关n条信息”“暂未查询到***有关的信息”

                        //付费会员显示权限
                        if (resultData.isFufei) {
                            if (!preRep.loadCkxm) {
                                $("#jq_intro_type li[tid=3]").after('<li tid="90"><a href="javascript:;">参考项目</a></li>');
                                $("#jq_show_type ul li .info_nzj").after('<div class="quyu-label"><a href="javascript:;" tid="90" class="checkbox">参考项目</a></div>');
                                preRep.loadCkxm = true;
                            }
                            $(".fufei_show").show();
                            $(".mianfei_show").hide();
                            $(".ssjg_header_fhjb").show();
                            $(".search_dingyue").hide();
                        } else {
                            $(".fufei_show").hide();
                            $(".mianfei_show").show();
                            $(".ssjg_header_fhjb").hide();
                        }
                        //加载订阅url
                        var bid_lxr_name = "";//联系人名称
                        var bid_lxr_mobile = "400-810-9688";//联系人电话
                        var bid_lxr_zhiwu = "销售经理";//联系人职务
                        var bid_fwrx = "400-810-9688";//服务热线
                        if (islogin) {
                            if (resultData.isFufei) {
                                bid_fwrx = "010-57219779";
                                bid_lxr_zhiwu = "客服人员";
                            } else {
                                bid_lxr_zhiwu = "销售人员";
                                if (!resultData.listData || resultData.listData.length <= 0 || jq_searchData.keywords == "")
                                    $(".search_dingyue").hide();
                                else
                                    $(".to_dingyue").addClass("add_dingyue");
                            }
                            if (resultData.bidLxrName && resultData.bidLxrName != "")
                                bid_lxr_name = resultData.bidLxrName;
                            else
                                bid_lxr_name = bid_lxr_zhiwu;
                            if (resultData.bidLxrMobile && resultData.bidLxrMobile != "")
                                bid_lxr_mobile = resultData.bidLxrMobile;
                            if (resultData.bidLxrWeImg && resultData.bidLxrWeImg != "")
                                $(".gzh-ewm-img").attr("src", resultData.bidLxrWeImg);

                            $(".dingyue-btn").attr("href", "//www.bidcenter.com.cn/BuserCenter/EmailSet/User_MailSet.aspx?keywords=" + jq_searchData.keywords + "&tag=" + jq_searchData.tag + "&type=" + jq_searchData.type + "&diqu=" + jq_searchData.diqu).attr("target", "_blank");
                        }
                        else {
                            bid_lxr_name = bid_lxr_zhiwu;
                            $(".dingyue-btn,.to_dingyue").addClass("jq_lijichakan");
                        }
                        $(".tell_lxr").text(bid_lxr_name + "（" + bid_lxr_mobile + "）");
                        $(".tell_zhiwu").text(bid_lxr_zhiwu);
                        $(".tell_lxfs").text(bid_fwrx);
                        $(".tell_tel").text(bid_lxr_mobile + "（" + bid_lxr_name + "）");

                        //初始化筛选标识
                        variate.isPageLoad = false;//分页筛选标识
                        if (callback)
                            callback();
                    }
                    if (data.retbs == 1) {
                        $(".error_text").text("您查询的信息中可能含有敏感内容，因政策监管原因，部分信息会做屏蔽处理，如需查询更多详情，请联系客服专员。");
                        $(".dingyue_info").hide();
                        $(".error_info").show();
                    }
                } else if (data.retbs == 11163)
                    location.href = "/alivalidate?rUrl=" + encodeURIComponent(location.href.replace(/&/g, '|'));
                else {
                    if (data.other2 && data.other2.pageSearchJson) {
                        resultData = data.other2;
                        if (tjType == 0) {
                            isfirst = false;
                            //数据绑定
                            jq_searchData = eval('(' + resultData.pageSearchJson + ')');
                            jq_searchDataNew = eval('(' + resultData.pageSearchJson + ')');
                        }
                        //金额单位转换
                        if (jq_searchData) {
                            if (jq_searchData.zbje_min && jq_searchData.zbje_min > 0) {
                                jq_searchData.zbje_min = jq_searchData.zbje_min / 10000;
                                jq_searchDataNew.zbje_min = jq_searchDataNew.zbje_min / 10000;
                            }
                            if (jq_searchData.zbje_max && jq_searchData.zbje_max > 0 && jq_searchData.zbje_max < 999999999999) {
                                jq_searchData.zbje_max = jq_searchData.zbje_max / 10000;
                                jq_searchDataNew.zbje_max = jq_searchDataNew.zbje_max / 10000;
                            } else {
                                jq_searchData.zbje_max = 0;
                                jq_searchDataNew.zbje_max = 0;
                            }
                        }
                    }
                    //绑定页面搜索条件
                    method.jq_QDataBind(jq_searchData);
                    $(".loadding_area").hide();
                    switch (data.retbs) {
                        case 201:
                            $(".wrong_data .null-text,.wrong_data .null-jianyi").hide();
                            $(".wrong_data .null-text2").html(`<span class="red">${data.msg}</span>`).show();
                            break;
                        default:
                            $(".wrong_data .null-text2").hide();
                            $(".wrong_data .null-text,.wrong_data .null-jianyi").show();
                            break;
                    }
                    method.changePageStatus(false);
                    //弹框展示
                    if (!islogin && isfirst) {
                        setTimeout(function () {
                            isEffectTank = true;
                            isLoadBase = true;
                            tankLogin();
                        }, 2000);
                    }
                    else if (!islogin && jq_searchData.page > 10) {
                        pub.login('7D24909FC08A6E08203D5A005AC7D5DC');
                    } else if (!isWanshan && (isfirst || jq_searchData.page > 1)) {
                        isEffectTank = true;
                        isLoadBase = true;
                        tankWanshan();
                    }
                    else if (!resultData.isFufei && jq_searchData.page > 10) {
                        isEffectTank = true;
                        isLoadBase = true;
                        method.showAllowTank(".allow_mianfei", "更多信息");
                    } else {
                        afterLayui(function () {
                            layer.msg(data.msg);
                        });
                    }
                }
            }
        }
    },
    //加载存在有效数据的关键词（首次加载搜索数据无数据时，将关键词拆分后调用）
    validKeywords: function (params, callback) {
        $.ajax({
            type: "POST",
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/search/GetValidKeywordsHandler.ashx"),
            data: params,
            async: false,
            dataType: "text",
            success: function (res) {
                if (res) {
                    var data = method.AESDecrypt(res);
                    if (data) {
                        if (data.ret && data.other2) {
                            resultTjData = data.other2;
                            if (callback)
                                callback();
                        }
                    }
                }
            },
            error: function (e) {
                layer.msg("网络错误，请重试");
            }
        });
    },
    //加载搜索条件区域下拉框数据
    baseDataInit: function (callback) {
        var params = interface_params_json.baseParamsJson;
        $.ajax({
            type: "POST",
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/search/InitSearchParamsHandler.ashx"),
            data: params,
            dataType: "text",
            success: function (res) {
                method.bindBaseData(res, callback);
            },
            error: function (e) {
                layer.msg("网络错误，请重试");
            }
        });
    },
    bindBaseData: function (res, callback) {
        if (res) {
            var data = method.AESDecrypt(res);
            if (data && data.ret) {
                baseData = data.other2;
                //绑定会员级别
                $(".huiyuanstr").text(baseData.jibie);
                //下拉数据绑定
                //采购方式
                if (baseData.cgfsList && baseData.cgfsList.length > 0) {
                    var cgfsHtml = [];
                    cgfsHtml.push('<li tid=""><a href="javascript:;">全部</a></li>');
                    for (var i = 0; i < baseData.cgfsList.length; i++) {
                        cgfsHtml.push('<li tid="' + baseData.cgfsList[i].key + '"><a href="javascript:;">' + baseData.cgfsList[i].value + '</a></li>');
                    }
                    $("#jq_ddl_cgfs").html(cgfsHtml.join(''));
                }
                //资金来源
                if (baseData.zjlyList && baseData.zjlyList.length > 0) {
                    var zjlyHtml = [];
                    zjlyHtml.push('<li tid=""><a href="javascript:;">全部</a></li>');
                    for (var i = 0; i < baseData.zjlyList.length; i++) {
                        zjlyHtml.push('<li tid="' + baseData.zjlyList[i].key + '"><a href="javascript:;">' + baseData.zjlyList[i].value + '</a></li>');
                    }
                    $("#jq_ddl_zjly").html(zjlyHtml.join(''));
                }
                //评标办法
                if (baseData.pbbfList && baseData.pbbfList.length > 0) {
                    var pbbfHtml = [];
                    pbbfHtml.push('<li tid=""><a href="javascript:;">全部</a></li>');
                    for (var i = 0; i < baseData.pbbfList.length; i++) {
                        pbbfHtml.push('<li tid="' + baseData.pbbfList[i].key + '"><a href="javascript:;">' + baseData.pbbfList[i].value + '</a></li>');
                    }
                    $("#jq_ddl_pbbf").html(pbbfHtml.join(''));
                }
                if (callback)
                    callback();
            } else
                layer.msg(data.msg);
        }
    },
    //加载右侧相关数据（推荐供应商、历史搜索、热门搜索词）
    loadRightData: function (keywords) {
        var params = interface_params_json.keywordsParamsJson;
        $.ajax({
            type: "POST",
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/search/GetRelatedDataHandler.ashx"),
            data: params,
            //xhrFields: { withCredentials: true },
            dataType: "text",
            success: function (res) {
                method.bindRightData(res, keywords);
            },
            error: function (e) {
                layer.msg("网络错误，请重试");
            }
        });
    },
    bindRightData: function (res, keywords) {
        if (res) {
            var data = method.AESDecrypt(res);
            if (data && data.other2) {
                var json = data.other2;
                if (json.tjgysList && json.tjgysList.length > 0) {
                    var kwdads = [];
                    if (keywords != "") {
                        $.each(json.tjgysList, function (i, obj) {
                            if (obj) {
                                var filterKwd = [];
                                var kwds = obj.keyword.split(',');
                                if (kwds.length > 0) {
                                    filterKwd = kwds.filter(function (x) {
                                        return keywords.indexOf(x) > -1;
                                    });
                                    if (filterKwd.length > 0) {
                                        json.tjgysList.splice($.inArray(obj, json.tjgysList), 1);
                                        obj.keyword = method.markRed(obj.keyword, json.kwdArry);
                                        kwdads.push(obj);
                                    }
                                }
                            }
                        });
                    }
                    if (kwdads <= 0) {
                        //var gysShowCount = 5 - kwdads.length;
                        $.each(json.tjgysList, function (i, obj) {
                            if (kwdads.length < 5)
                                kwdads.push(obj);
                        });
                    }
                    //加载推荐供应商
                    method.loadTjgysData(kwdads);
                }
                else
                    $(".tjgys_area").hide();
                if (json.historyList && json.historyList.length > 0)
                    //加载历史搜索
                    method.loadHistoryData(json.historyList);
                else
                    $(".lsss_area").hide();
                if (json.remenList && json.remenList.length > 0) {
                    //加载热门搜索
                    method.loadRemenData(json.remenList);
                    var jianyiHtml = [];
                    $.each(json.remenList, function (i, obj) {
                        if (jianyiHtml.length < 10)
                            jianyiHtml.push('<a href="/search?keywords=' + encodeURIComponent(obj.keywords) + '" class="jianyi-word">' + obj.keywords + '</a>');
                    });
                    $(".jianyi_text").html(jianyiHtml.join('、'));
                }
                else
                    $(".rmssc_area").hide();
            }
        }
    },
    //加载关键词广告/推荐供应商、业主（已下线）
    loadKwdAdOrTjCompany: function (keywords) {
        var params = interface_params_json.keywordsParamsJson;
        $.ajax({
            type: "POST",
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/search/GetKwdAdDataHandler.ashx"),
            data: params,
            //xhrFields: { withCredentials: true },
            dataType: "text",
            success: function (res) {
                method.bindKwdAdOrTjCompanyData(res);
            },
            error: function (e) {
                layer.msg("网络错误，请重试");
            }
        });
    },
    bindKwdAdOrTjCompanyData: function (res) {
        if (res) {
            var data = method.AESDecrypt(res);
            if (data && data.other2) {
                resultKwdData = data.other2;
                method.bindKwdAd();
            }
        }
    },
    //获取相关关键词（已下线）
    getRelatedKwd: function (keywords) {
        var params = interface_params_json.keywordsParamsJson;
        $.ajax({
            type: "POST",
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/search/GetKeywordsRelatedHandler.ashx"),
            data: params,
            dataType: "text",
            success: function (res) {
                method.bindRelatedKwdData(res);
            },
            error: function (e) {
                layer.msg("网络错误，请重试");
            }
        });
    },
    bindRelatedKwdData: function (res) {
        if (res) {
            var data = method.AESDecrypt(res);
            if (data && data.ret && data.other2) {
                var json = data.other2;
                if (json.isXgc)
                    $(".gjc-explain").text("相关搜索：");
                else
                    $(".gjc-explain").text("热门搜索：");
                if (json.xgGjc && json.xgGjc.length > 0) {
                    var currGroup = [];
                    for (var i = 0; i < json.xgGjc.length; i++) {
                        if (json.xgGjc[i] != "")
                            currGroup.push(json.xgGjc[i]);
                        if (currGroup.length == 7 || i == json.xgGjc.length - 1) {
                            variate.xgGjcArray.push(currGroup);
                            currGroup = [];
                        }
                        if (variate.xgGjcArray.length > 1)
                            $(".gjc-change").show();
                        else
                            $(".gjc-change").hide();
                    }
                    //if (json.isDingyue || tjType > 0)
                    //    $(".ssjg-wrap_dingyue").hide();
                    //else
                    //    $(".ssjg-wrap_dingyue").show();
                    method.bindXgGjc();
                }
            }
        }
    },
    //接口返回解密
    AESDecrypt: function (str) {
        var nContent = CryptoJS.AES.decrypt(str, variate.key, {
            iv: variate.aceIV,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.ZeroPadding
        })
        if (nContent && nContent != null) {
            try {
                var constr = CryptoJS.enc.Utf8.stringify(nContent)
                if (constr != "") {
                    var data = JSON.parse(constr);
                    return data;
                }
                else
                    return null;
            }
            catch (err) {
                return null;
            }

        } else
            return null;
    },
    //搜索结果列表是否加载数据成功-状态改变，nodata：是否为无数据
    changePageStatus: function (success, nodata) {
        if (success) {
            $(".just_data").show();
            $(".wrong_data").hide();
            if (tjType == 0) $(".search-empty").hide();
        } else if (nodata) {
            $(".just_data").hide();
            //2026-01-22 jianyisousuo->search-empty
            $(".search-empty").show();
        } else {//异常数据
            $(".just_data").hide();
            $(".wrong_data").show();
        }
    },
    //加载关键词广告
    loadKwdAd: function (data) {
        var getTpl = keywordAd.innerHTML;
        if (view) {
            laytpl(getTpl).render(data, function (html) {
                $("#keywordAdArea").html(html);
            });
        }
    },
    //加载推荐业主、供应商广告
    loadTjCompany: function (data) {
        var getTpl = tjCompany.innerHTML;
        if (view) {
            laytpl(getTpl).render(data, function (html) {
                $("#tjCompanyArea").html(html);
            });
        }
    },
    //加载搜索结果列表
    loadListData: function (data) {
        var getTpl = searchResult.innerHTML;
        laytpl(getTpl).render(data, function (html) {
            $("#searchListArea").html(html);
            isbinddata = true;
            if (!isEffectTank)
                layer.closeAll();
            //添加:visited效果
            addVisited();

            //获取扶持企业信息
            GetFuChiCompanyArr();
        });
    },
    //加载搜索地区
    loadDiquData: function (data) {
        var getTpl = searchDiqu.innerHTML;
        laytpl(getTpl).render(data, function (html) {
            $("#searchDiquArea").html(html);
        });
    },
    //加载推荐供应商
    loadTjgysData: function (data) {
        var getTpl = tjgys.innerHTML;
        laytpl(getTpl).render(data, function (html) {
            $("#tjgysArea").html(html);
            const listEl = document.getElementById('tjgysArea');
            tjgysItems = Array.from(listEl.querySelectorAll('.tjgys-item'));

            tjgysItems.forEach((item, index) => {
                let isHover = false;
                item.addEventListener('mouseenter', () => {
                    isHover = true;
                    clearTimeout(tjgysExpandTimer);
                    tjgysExpandTimer = setTimeout(() => {
                        if (isHover) method.tjgysExpandItem(index);
                    }, TJGYS_EXPAND_DELAY);
                });
                item.addEventListener('mouseleave', () => {
                    isHover = false;
                    clearTimeout(tjgysExpandTimer);
                    tjgysExpandTimer = null;
                });
            });
        });
    },
    // 推荐供应商-展开效果
    tjgysExpandItem: function (index) {
        clearTimeout(tjgysExpandTimer);
        tjgysExpandTimer = null;
        if (tjgysActiveIndex === index) return;
        if (tjgysActiveIndex >= 0) {
            const oldItem = tjgysItems[tjgysActiveIndex];
            const panel = oldItem.querySelector('.gongyingshang_cell_detail');
            panel.classList.add('fast-close');
            panel.classList.add('closing-panel');
            setTimeout(() => {
                panel.classList.remove('fast-close');
                panel.classList.remove('closing-panel');
            }, TJGYS_CLOSE_DURATION);
            oldItem.classList.remove('active');
        }
        tjgysActiveIndex = index;
        tjgysItems[index].classList.add('active');
    },
    // 推荐供应商-关闭效果
    tjgysCollapseAll: function () {
        clearTimeout(tjgysExpandTimer);
        tjgysExpandTimer = null;
        tjgysItems.forEach(el => {
            const panel = el.querySelector('.gongyingshang_cell_detail');
            panel.classList.add('fast-close');
            panel.classList.add('closing-panel');
            el.classList.remove('active');
            setTimeout(() => {
                panel.classList.remove('fast-close');
                panel.classList.remove('closing-panel');
            }, TJGYS_CLOSE_DURATION);
        });
        tjgysActiveIndex = -1;
    },
    //加载历史搜索
    loadHistoryData: function (data) {
        var getTpl = historyKwd.innerHTML;
        laytpl(getTpl).render(data, function (html) {
            $("#historyKwdArea").html(html);
        });
    },
    //加载热门搜索词
    loadRemenData: function (data) {
        var getTpl = remenKwd.innerHTML;
        laytpl(getTpl).render(data, function (html) {
            $("#remenKwdArea").html(html);
        });
    },
    //绑定关键词广告/推荐供应商、业主
    bindKwdAd: function () {
        if (resultKwdData.tuijianCompany && resultKwdData.tuijianCompany.length > 0) {
            resultKwdData.tuijianCompany.isLogin = islogin;
            method.loadTjCompany(resultKwdData.tuijianCompany);
        }
    },
    //加载分页
    loadPage: function (id, data, params) {
        var layout = [];
        if (params && params.length > 0)
            layout = params;
        else
            layout = ['prev', 'page', 'next'];
        laypage.render({
            elem: id,
            limit: 40,
            groups: 10,
            curr: jq_searchData.page,
            count: data.showInfoCount,
            layout: layout,
            first: '首页',
            last: false,
            skip: '跳转到',
            jump: function (obj, first) {
                if (!first) {
                    jq_searchDataNew.page = obj.curr;
                    variate.isPageLoad = true;
                    method.jq_search(undefined, false, false);
                }
            }
        });
        $(".layui-laypage-first").insertBefore($(".layui-laypage-prev"));
        if (!islogin) {
            $("#listPage a").each(function (item, element) {
                var dp = $(element).attr("data-page");
                if (dp) {
                    if (parseInt(dp) > 10)
                        $(element).addClass("jq_tologin").removeAttr("data-page");
                    else if (parseInt(dp) > 1) {
                        $(element).addClass("jq_lijichakan").removeAttr("data-page");
                    }
                }
            });
        } else if (!isWanshan) {
            $("#listPage a").each(function (item, element) {
                var dp = $(element).attr("data-page");
                if (dp && parseInt(dp) > 10)
                    $(element).addClass("jq_wanshan").removeAttr("data-page");
            });
        }
        if ($(".layui-laypage-next").hasClass("layui-disabled"))
            $(".layui-laypage-next").removeClass("layui-disabled").addClass("layui-last");
    },
    //告诉我-弹框
    open_tellme: function () {
        tankObj.tellmeIndex = layer.open({
            type: 1,
            area: ['auto', 'auto'],
            title: false,
            border: [0],
            closeBtn: 0,
            content: $(".wentifankui"),
            end: function () {
                $(".wentifankui").hide();
            }
        });
    },
    //提交反馈意见
    sub_feedback: function () {
        var c = $.trim($("#feedbackContent").val());
        var mobile = $.trim($("#feedbackMobile").val());
        var yuanyin = $.trim($("input[name='bmy_yuanyin']:checked").val());
        if (c == "") {
            $("#feedbackContent").focus();
            method.commonAlert("请填写反馈内容！");
        } else if (mobile == "") {
            $("#feedbackMobile").focus();
            method.commonAlert("请填写手机号！");
        } else if (!method.checkFkMobile("#feedbackMobile")) {
            $("#feedbackMobile").focus();
            method.commonAlert("请填写正确手机号！");
        } else {
            if (yuanyin != "")
                c = yuanyin + ":" + c;
            var qData = { msg: encodeURIComponent(c), mobile: mobile, keywords: encodeURIComponent($.trim(jq_searchData.keywords)), url: encodeURIComponent(document.location.href) };
            $.ajax({
                type: "GET", //用POST方式传输
                contentType: "application/json", //数据格式:JSON
                data: qData,
                url: "/Handler/SearchFeedback.aspx", //目标地址
                dataType: "json",
                success: function (json) {
                    layer.close(tankObj.tellmeIndex);
                    layer.msg("您已提交成功，届时会有接待客服与您联系，请保持电话畅通");
                }, error: function (e) {
                    layer.close(tankObj.tellmeIndex);
                }
            });
        }
    },
    //关闭问题反馈
    close_tellme: function () {
        layer.close(tankObj.tellmeIndex);
    },
    //显示意见反馈
    showYjfk: function () {
        tankObj.yjfkIndex = layer.open({
            type: 1,
            area: ['auto', 'auto'],
            title: false,
            border: [0],
            closeBtn: 0,
            content: $(".yijianfankuiPop"),
            end: function () {
                $(".yijianfankuiPop").hide();
            }
        });
    },
    //提交意见反馈
    jq_subQuestion: function () {
        var c = $.trim($("#qContents").val());
        var mobile = $.trim($("#qMobile").val());
        if (c == "") {
            $("#qContents").focus();
            method.commonAlert("请填写反馈内容！");
        } else if (mobile == "") {
            $("#qMobile").focus();
            method.commonAlert("请填写手机号！");
        } else if (!method.checkFkMobile("#qMobile")) {
            $("#qMobile").focus();
            method.commonAlert("请填写正确手机号！");
        } else {
            var qData = { msg: encodeURIComponent(c), mobile: mobile, keywords: encodeURIComponent($.trim(jq_searchData.keywords)), url: encodeURIComponent(document.location.href) };
            $.ajax({
                type: "GET", //用POST方式传输
                contentType: "application/json", //数据格式:JSON
                data: qData,
                url: "/Handler/SearchFeedback.aspx", //目标地址
                dataType: "json",
                success: function (json) {
                    layer.close(tankObj.yjfkIndex);
                    method.commonAlert(json.msg);
                }, error: function (e) {
                    layer.close(tankObj.yjfkIndex);
                }
            });
        }
    },
    //添加排除词-弹框
    open_addpcc: function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "排除词");
            return;
        }

        tankObj.addpccIndex = layer.open({
            type: 1,
            area: ['auto', 'auto'],
            title: false,
            border: [0],
            closeBtn: 0,
            content: $(".addpccPop"),
            success: function (layero, index) {
                var pcount = $(".paichuci-show .paichuci").length;
                $(".nowsubpcc").html(pcount);
                if (pcount > 4) {
                    $(".addpccPop .setci-input-btn").attr("onclick", "");
                }
                else {
                    $(".addpccPop .setci-input-btn").removeClass("setci-input-btn2").attr("onclick", "method.jq_subpaichuci()");
                }

                $(".addpccPop .setci-list").html("");
                $.each($(".paichuci-show .paichuci"), function () {
                    $(".addpccPop .setci-list").append('<li><span>' + $(this).find("span").html() + '</span><i onclick="method.removepaichuci(this,1)">×</i></li>');
                });

                $(".addpccPop .setci-input-text").val("");
            },
            end: function () {
                $(".addpccPop").hide();
            }
        });
    },
    //提交填写的排除词
    jq_subpaichuci: function () {
        var subpc = $(".addpccPop .setci-input-text").val();
        if (subpc != '') {
            var pcount = $(".addpccPop .setci-list li").length;
            if (pcount >= 4) {
                $(".addpccPop .setci-input-btn").attr("onclick", "");
                $(".addpccPop .setci-input-btn").addClass("setci-input-btn2");
            }

            $(".addpccPop .setci-list").append('<li><span>' + subpc + '</span><i onclick="method.removepaichuci(this,1)">×</i></li>');

            $(".nowsubpcc").html(pcount + 1);
            $(".addpccPop .setci-input-text").val("");
        }
    },
    //移除待提交项
    removepaichuci: function (e, t) {
        var pcount = 0;
        if (t == 0) {
            if (!islogin) {
                tankLogin();
                return;
            }
            else if (!isWanshan && tankWanshan()) {
                return;
            }
            else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "排除词");
                return;
            }

            $(e).parent().remove();
            pcount = $(".paichuci-list .paichuci").length;
            $(".nowpaichuci").html(pcount);
            $(".paichuci-list-clear").css("display", "inline");
            $(".addpaichuci").attr("onclick", "method.open_addpcc()").removeClass("addpaichuci2");

            jq_searchDataNew.excode = '';
            if (pcount > 0) {
                $.each($(".paichuci-list .paichuci"), function () {
                    jq_searchDataNew.excode += $(this).find("span").html() + ",";
                });

                jq_searchDataNew.excode = jq_searchDataNew.excode.substr(0, jq_searchDataNew.excode.length - 1);
            }
            method.jq_search();
        }
        else {
            $(e).parent().remove();
            pcount = $(".addpccPop .setci-list li").length;
        }
        $(".nowsubpcc").html(pcount);
        $(".addpccPop .setci-input-btn").removeClass("setci-input-btn2").attr("onclick", "method.jq_subpaichuci()");
    },
    //重置提交排除词
    jq_clearsubpaichuci: function (t) {
        if (t == 0) {
            if (!islogin) {
                tankLogin();
                return;
            }
            else if (!isWanshan && tankWanshan()) {
                return;
            }
            else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "排除词");
                return;
            }

            jq_searchDataNew.excode = '';
            $(".nowpaichuci").html('0');
            $(".paichuci-list-clear").css("display", "none");
            $(".paichuci-show .paichuci-list").html("");
            $(".addpaichuci").attr("onclick", "method.open_addpcc()").removeClass("addpaichuci2");

            $.each($(".paichuci-list .paichuci"), function () {
                jq_searchDataNew.excode += $(this).find("span").html() + ",";
            });
            if (jq_searchDataNew.excode != '')
                jq_searchDataNew.excode = jq_searchDataNew.excode.substr(0, jq_searchDataNew.excode.length - 1);

            method.jq_search();
        }
        $(".addpccPop .setci-list").html("");
        $(".nowsubpcc").html("0");
        $(".addpccPop .setci-input-btn").removeClass("setci-input-btn2").attr("onclick", "method.jq_subpaichuci()");
    },
    //保存排除词
    jq_addpaichuci: function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "排除词");
            return;
        }

        $(".paichuci-show .paichuci-list").html("");
        var sublist = $(".addpccPop .setci-list li");
        var pcount = sublist.length;
        $.each(sublist, function () {
            $(".paichuci-show .paichuci-list").append('<span class="paichuci"><span>' + $(this).find("span").html() + '</span><i onclick="method.removepaichuci(this,0)">×</i></span>');
        });
        $(".nowpaichuci").html(pcount);
        $(".paichuci-list-clear").css("display", "inline");
        if (pcount >= 5) {
            $(".addpaichuci").attr("onclick", "").addClass("addpaichuci2");
        }
        else {
            $(".addpaichuci").attr("onclick", "method.open_addpcc()").removeClass("addpaichuci2");
        }
        layer.close(tankObj.addpccIndex);

        jq_searchDataNew.excode = '';
        $.each($(".paichuci-list .paichuci"), function () {
            jq_searchDataNew.excode += $(this).find("span").html() + ",";
        });
        if (jq_searchDataNew.excode != '')
            jq_searchDataNew.excode = jq_searchDataNew.excode.substr(0, jq_searchDataNew.excode.length - 1);

        method.jq_search();
    },
    //添加相关词-弹框
    open_addxgc: function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "相关词");
            return;
        }
        tankObj.addxgcIndex = layer.open({
            type: 1,
            area: ['auto', 'auto'],
            title: false,
            border: [0],
            closeBtn: 0,
            content: $(".addxgcPop"),
            success: function (layero, index) {
                var pcount = $(".xiangguanci-show .xiangguanci").length;
                $(".nowsubxgc").html(pcount);
                if (pcount > 4) {
                    $(".addxgcPop .setci-input-btn").attr("onclick", "");
                }
                else {
                    $(".addxgcPop .setci-input-btn").removeClass("setci-input-btn2").attr("onclick", "method.jq_subxiangguanci()");
                }

                $(".addxgcPop .setci-list").html("");
                $.each($(".xiangguanci-show .xiangguanci"), function () {
                    $(".addxgcPop .setci-list").append('<li><span>' + $(this).find("span").html() + '</span><i onclick="method.removexiangguanci(this,1)">×</i></li>');
                });

                $(".addxgcPop .setci-input-text").val("");
            },
            end: function () {
                $(".addxgcPop").hide();
            }
        });
    },
    //提交填写的相关词
    jq_subxiangguanci: function () {
        var subpc = $(".addxgcPop .setci-input-text").val();
        if (subpc != '') {
            var pcount = $(".addxgcPop .setci-list li").length;
            if (pcount >= 4) {
                $(".addxgcPop .setci-input-btn").attr("onclick", "");
                $(".addxgcPop .setci-input-btn").addClass("setci-input-btn2");
            }


            $(".addxgcPop .setci-list").append('<li><span>' + subpc + '</span><i onclick="method.removexiangguanci(this,1)">×</i></li>');

            $(".nowsubxgc").html(pcount + 1);
            $(".addxgcPop .setci-input-text").val("");
        }
    }
    ,
    //移除待提交项
    removexiangguanci: function (e, t) {
        var pcount = 0;
        if (t == 0) {
            if (!islogin) {
                tankLogin();
                return;
            }
            else if (!isWanshan && tankWanshan()) {
                return;
            }
            else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "相关词");
                return;
            }

            $(e).parent().remove();
            pcount = $(".xiangguanci-list .xiangguanci").length;
            $(".nowxiangguanci").html(pcount);
            $(".xiangguanci-list-clear").css("display", "inline");
            $(".addxiangguanci").attr("onclick", "method.open_addxgc()").removeClass("addxiangguanci2");

            jq_searchDataNew.kwordtagh = '';
            if (pcount > 0) {
                $.each($(".xiangguanci-list .xiangguanci"), function () {
                    jq_searchDataNew.kwordtagh += $(this).find("span").html() + ",";
                });

                jq_searchDataNew.kwordtagh = jq_searchDataNew.kwordtagh.substr(0, jq_searchDataNew.kwordtagh.length - 1);
            }
            method.jq_search();
        }
        else {
            $(e).parent().remove();
            pcount = $(".addxgcPop .setci-list li").length;
        }
        $(".nowsubxgc").html(pcount);
        $(".addxgcPop .setci-input-btn").removeClass("setci-input-btn2").attr("onclick", "method.jq_subxiangguanci()");
    },
    //重置提交相关词
    jq_clearsubxiangguanci: function (t) {
        if (t == 0) {
            if (!islogin) {
                tankLogin();
                return;
            }
            else if (!isWanshan && tankWanshan()) {
                return;
            }
            else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "相关词");
                return;
            }

            jq_searchDataNew.kwordtagh = '';
            $(".nowxiangguanci").html('0');
            $(".xiangguanci-list-clear").css("display", "none");
            $(".xiangguanci-show .xiangguanci-list").html("");
            $(".addxiangguanci").attr("onclick", "method.open_addxgc()").removeClass("addxiangguanci2");

            $.each($(".xiangguanci-list .xiangguanci"), function () {
                jq_searchDataNew.kwordtagh += $(this).find("span").html() + ",";
            });
            if (jq_searchDataNew.kwordtagh != '')
                jq_searchDataNew.kwordtagh = jq_searchDataNew.kwordtagh.substr(0, jq_searchDataNew.kwordtagh.length - 1);

            method.jq_search();
        }
        $(".addxgcPop .setci-list").html("");
        $(".nowsubxgc").html("0");
        $(".addxgcPop .setci-input-btn").removeClass("setci-input-btn2").attr("onclick", "method.jq_subxiangguanci()");
    },
    //保存相关词
    jq_addxiangguanci: function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "相关词");
            return;
        }

        $(".xiangguanci-show .xiangguanci-list").html("");
        var sublist = $(".addxgcPop .setci-list li");
        var pcount = sublist.length;
        $.each(sublist, function () {
            $(".xiangguanci-show .xiangguanci-list").append('<span class="xiangguanci"><span>' + $(this).find("span").html() + '</span><i onclick="method.removexiangguanci(this,0)">×</i></span>');
        });
        $(".xiangguanci-list-clear").css("display", "inline");
        $(".nowxiangguanci").html(pcount);
        if (pcount >= 5) {
            $(".addxiangguanci").attr("onclick", "").addClass("addxiangguanci2");
        }
        else {
            $(".addxiangguanci").attr("onclick", "method.open_addxgc()").removeClass("addxiangguanci2");
        }
        layer.close(tankObj.addxgcIndex);

        jq_searchDataNew.kwordtagh = '';
        $.each($(".xiangguanci-list .xiangguanci"), function () {
            jq_searchDataNew.kwordtagh += $(this).find("span").html() + ",";
        });
        if (jq_searchDataNew.kwordtagh != '')
            jq_searchDataNew.kwordtagh = jq_searchDataNew.kwordtagh.substr(0, jq_searchDataNew.kwordtagh.length - 1);

        method.jq_search();
    },
    //验证手机号
    checkFkMobile: function (selecter) {
        var obj = $(selecter);
        var s = $.trim(obj.val());
        var stel = /(^0{0,1}1[3-8][0-9]{9}$)/;
        if (s == "" || s == "请填写真实联系方式")
            method.commonTips("请输入您的手机号", selecter);
        else if (!stel.exec(s))
            method.commonTips("请输入真实手机号码", selecter);
        else
            return true;
        return false;
    },
    //绑定相关关键词
    bindXgGjc: function () {
        if (variate.xgGjcArray[variate.xgGjcIndex] && variate.xgGjcArray[variate.xgGjcIndex].length > 0) {
            var xggjcHtml = [];
            for (var i = 0; i < variate.xgGjcArray[variate.xgGjcIndex].length; i++) {
                xggjcHtml.push('<a href="JavaScript:;" onclick="method.openUrl(\'' + encodeURIComponent(variate.xgGjcArray[variate.xgGjcIndex][i]) + '\');" title="' + variate.xgGjcArray[variate.xgGjcIndex][i] + '">' + variate.xgGjcArray[variate.xgGjcIndex][i] + '</a>');
            }
            $(".gjc-text").html(xggjcHtml.join(''));
            if (variate.xgGjcIndex + 1 == variate.xgGjcArray.length)
                variate.xgGjcIndex = 0;
        }
    },
    openUrl: function (keywords) {
        if ($.fn.SearchTag == 0)
            location.href = "/search?keywords=" + keywords;
        else
            window.open("//shuju.bidcenter.com.cn/shuju/search-zb.html?key=" + keywords);
    },
    //换一批相关关键词
    changeKwd: function () {
        variate.xgGjcIndex += 1;
        method.bindXgGjc();
    },
    //加载全部地区Json
    loadDiquJson: function () {
        $.each(diqus, function (i, e) {
            diqusJson.push({
                id: i,
                b: e.b,
                c: e.c
            });
        });
    },
    //导出信息
    jq_BidExport: function (type) {
        if (!islogin)
            tankLogin();
        else if (!isWanshan)
            tankWanshan();
        else {
            var daochuType;
            var showzip = false;
            try { showzip = ziptag; } catch (e) { }
            if (($.inArray(resultData.Permission, [4, 6, 7, 9, 35]) > -1 || showzip) || (type == 4 && userinfo && userinfo.id == '523275'))
                daochuType = 3;
            else if ($.inArray(resultData.Permission, [2, 3]) > -1)
                daochuType = 2;
            else if (resultData.Permission == 1)
                daochuType = 1;

            switch (daochuType) {
                case 1:
                    if (resultData.userXiangmu && resultData.userXiangmu != null && resultData.userXiangmu.indexOf(',1017,') == -1)
                        window.open("//shuju.bidcenter.com.cn/");
                    else
                        method.showAllowTank(".allow_mianfei", "项目导出");
                    break;
                case 2:
                    var ids = [];
                    $("#searchListArea input[type=checkbox][name=ids]:checked").each(function () {
                        ids.push($(this).val());
                    });
                    if (ids.length == 0) {
                        method.commonAlert("请选择要导出的信息");
                        return;
                    }
                    var exportname = encodeURIComponent('关于“' + $.trim(jq_searchData.keywords) + '”信息-中国采招网信息搜索_' + jq_searchData.page);
                    if (jq_searchData.keywords == "") {
                        exportname = encodeURIComponent('”中国采招网信息搜索_' + jq_searchData.page);
                    }
                    switch (type) {
                        case 1:
                            window.open("//export.bidcenter.com.cn/JsonHandler/WordExportNoContent.aspx?ids=" + ids.join(',') + "&exportname=" + exportname);
                            break;
                        case 2:
                            window.open("//export.bidcenter.com.cn/JsonHandler/ZhaobiaoExcelExportNoContent.aspx?ids=" + ids.join(',') + "&exportname=" + exportname);
                            break;
                        case 3:
                            window.open("//export.bidcenter.com.cn/JsonHandler/ZhaobiaoPDFExportNoContent.aspx?ids=" + ids.join(',') + "&exportname=" + exportname);
                            break;
                        default:
                            break;
                    }
                    break;
                case 3:
                    var ids = [];
                    $("#searchListArea input[type=checkbox][name=ids]:checked").each(function () {
                        ids.push($(this).val());
                    });
                    if (ids.length == 0) {
                        method.commonAlert("请选择要导出的信息");
                        return;
                    }
                    var exportname = encodeURIComponent('关于“' + $.trim(jq_searchData.keywords) + '”信息-中国采招网信息搜索_' + jq_searchData.page);
                    if (jq_searchData.keywords == "") {
                        exportname = encodeURIComponent('”中国采招网信息搜索_' + jq_searchData.page);
                    }
                    switch (type) {
                        case 1:
                            window.open("//export.bidcenter.com.cn/JsonHandler/WordExport.aspx?ids=" + ids.join(',') + "&exportname=" + exportname);
                            break;
                        case 2:
                            window.open("//export.bidcenter.com.cn/JsonHandler/ZhaobiaoExcelExport.aspx?ids=" + ids.join(',') + "&exportname=" + exportname);
                            break;
                        case 3:
                            window.open("//export.bidcenter.com.cn/JsonHandler/ZhaobiaoPDFExport.aspx?ids=" + ids.join(',') + "&exportname=" + exportname);
                            break;
                        case 4:
                            window.open("//export.bidcenter.com.cn/JsonHandler/ZipExport.aspx?ids=" + ids.join(',') + "&exportname=" + exportname);
                            break;
                        default:
                            break;
                    }
                    break;
                default:
                    window.open("//shuju.bidcenter.com.cn/");
                    break;
            }
        }
    },
    //在线开通会员
    zaixiankaitong: function () {
        var url = window.location.href.replace(/\?/g, "$").replace(/&/g, "^").replace(/=/g, "@");
        window.open("//www.bidcenter.com.cn/zaixiankaitong/index.aspx?reurl=" + url, "_blank");
    },
    //人工开通会员
    showrengongkaitong: function () {
        layer.closeAll();
        layer.open({
            type: 2,
            title: false,
            closeBtn: 1,
            shadeClose: false, //点击遮罩关闭
            shade: 0.5,
            area: ['800px', '590px'],
            skin: 'myskin',
            content: '//www.bidcenter.com.cn/zaixiankaitong/rengongkaitong.aspx'
        });
    },
    //展开更多
    openMore: function () {
        $(".zhankaigengduo").hide();
        $(".shouqigengduo").show();
        $("#more_condition").slideDown();
    },
    //收起更多
    closeMore: function () {
        $(".shouqigengduo").hide();
        $(".zhankaigengduo").show();
        $("#more_condition").slideUp();
    },
    //回到顶部
    backTop: function () {
        if ($('html').scrollTop() > 0) {
            $('html').animate({ scrollTop: 0 }, 1000);
            return false;
        }
        $('body').animate({ scrollTop: 0 }, 1000);
        return false;
    },
    initTime: function () {
        var thisDate = new Date();
        laystart.config.min = {
            year: 2000,
            month: 0,//关键
            date: 1
        }
        laystart.config.max = {
            year: thisDate.getFullYear(),
            month: thisDate.getMonth(),//关键
            date: thisDate.getDate()
        }
        layend.config.min = {
            year: 2000,
            month: 0,
            date: 1
        }
        layend.config.max = {
            year: thisDate.getFullYear(),
            month: thisDate.getMonth(),//关键
            date: thisDate.getDate()
        }
    },
    //获取默认显示文字
    getShowText: function (str) {
        if (str == '' || str == '--') return '<i class="defaut">详见内容</i>';
        return str;
    },
    getShowTextV2: function (str) {
        if (str == '' || str == '--') return '<i class="defaut">详见内容</i>';
        return str.substring(0, 7);
    },
    //获取标签HTML
    getTagHtml: function (str) {
        var showHtml = [];
        if (str != "" && str != "--") {
            var tagArr = str.split(',');
            if (tagArr.length > 0) {

                for (var i = 0; i < tagArr.length; i++) {
                    switch (tagArr[i]) {
                        case "1":
                            showHtml.push('<span class="ssjg-label biaoshu-label">标书</span>');
                            break;
                        case "2":
                            showHtml.push('<span class="ssjg-label fujian-label">附件</span>');
                            break;
                        case "3":
                            showHtml.push('<span class="ssjg-label hetong-label">合同</span>');
                            break;
                        case "4":
                            showHtml.push('<span class="ssjg-label fujian-label">变更</span>');
                            break;
                        case "5":
                            showHtml.push('<span class="ssjg-label fujian-label">跟进</span>');
                            break;
                        case "6":
                            showHtml.push('<span class="ssjg-label fujian-label">核实</span>');
                            break;
                        case "7":
                            showHtml.push('<span class="ssjg-label fujian-label">委托</span>');
                            break;
                        case "8":
                            showHtml.push('<span class="ssjg-label fujian-label">推荐</span>');
                            break;
                        case "9":
                            showHtml.push('<span class="ssjg-label fujian-label">VIP独家</span>');
                            break;
                        default:
                            showHtml.push('<span class="ssjg-label caigoujihua-label">' + tagArr[i] + '</span>');
                            break;
                    }
                }
            }
        }
        return showHtml.join(' ');
    },
    //关键词是否在附件中
    getKwdFujian: function (str) {
        var kwds = [];
        var skw = jq_searchData.keywords;
        if (tjType > 0)
            skw = tjKeyword.length > 5 ? tjKeyword.substr(0, 5) + "..." : tjKeyword;
        else {
            var arr = [];
            $.each(jq_searchData.keywordsArry, function (i, e) {
                var len = arr.join('').length;
                if (len >= 5 || i > 1) return;
                if (e.length > (5 - len)) {
                    arr.push(e.substr(0, 5 - len) + "...");
                } else if ((i == 0 && e.length == 5) || (jq_searchData.keywordsArry.length > 2 && i == 1))
                    arr.push(e + "等");
                else
                    arr.push(e);
            });
            skw = arr.join(',');
        }
        kwds.push(skw);
        if (jq_searchData.secondKwds != undefined && jq_searchData.secondKwds != '')
            kwds.push(jq_searchData.secondKwds);
        if (str != "" && str != '--')
            return '(<font style="color:red;" title="' + (tjType > 0 ? tjKeyword : jq_searchData.keywords) + '">' + kwds.join('∩') + '</font>在' + str + '中)';
        return "";
    },
    //关键词标记红色
    markRed: function (str, kwdArry) {
        var kwds = jq_searchData.keywordsAllArry;
        if (kwds == undefined || kwds.length <= 0)
            kwds = kwdArry;
        if (tjType > 0 && currTjKwd != "")
            kwds = [currTjKwd];
        if (kwds && kwds != undefined && kwds.length > 0) {
            for (var i = 0; i < kwds.length; i++) {
                if (!/^[0-9]+\.?[0-9]*$/.test(kwds[i]))
                    str = str.replace(kwds[i], '$newstitle_' + i + '_mark');
            }
            for (var i = 0; i < kwds.length; i++) {
                if (!/^[0-9]+\.?[0-9]*$/.test(kwds[i]))
                    str = str.replace('$newstitle_' + i + '_mark', '<font color="red">' + kwds[i] + '</font>');
            }
        }
        if (str == '' || str == '--') str = '<font color="#777777">详见内容</font>';
        return str;
    },
    //加载用户二维码
    loadUserErweima: function () {
        var params = {
            from: 6137,
            guid: guid,
            location: 6138,
            token: token,
            lyid: 6137
        };
        $.ajax({
            type: "POST",
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/search/ErWeiMaUrlImgHandler.ashx"),
            data: params,
            dataType: "text",
            success: function (res) {
                method.bindUerErweima(res);
            },
            error: function (e) {
                layer.msg("网络错误，请重试");
            }
        });
    },
    //加载二维码
    bindUerErweima: function (res) {
        if (res) {
            var data = method.AESDecrypt(res);
            if (data && data.ret && data.other) {
                var url = data.other;
                $(".gzh-ewm-img").attr("src", url);
            }
        }
    },
    //返回旧版
    backOldVer: function () {
        var params = "";
        if (searchParams.length > 0)
            params = "?" + searchParams.join('&');
        location.href = "/searchold" + params;
    },
    //layui初始化
    layuiInit: function () {
        layui.use(['layer', 'laypage', 'laydate', 'laytpl', 'form'], function () {
            layer = layui.layer;
            laypage = layui.laypage;
            laydate = layui.laydate;
            laytpl = layui.laytpl;
            form = layui.form;
            layer.ready(function () {
                layerisload = true;
                //资质证书筛选
                form.on('select(jq_ddl_zzzs)', function (element) {
                    jq_searchDataNew.zzzs = element.value;
                    method.jq_search();
                });
                form.render();
                //时间范围筛选
                if (isfirst)
                    method.jq_QTimeRangeBind(jq_searchData);
                var thisDate = new Date();
                //开始时间
                laystart = laydate.render({
                    elem: '#txtStartTime',
                    trigger: 'click',
                    max: method.changeTime(jq_searchData.endtime),
                    done: function (value, date) {
                        layend.config.min = {
                            year: date.year,
                            month: date.month - 1,//关键
                            date: date.date
                        }
                        jq_searchDataNew.startTime = value;
                        if ($.trim($("#txtEndTime").val()) != "") {
                            jq_searchDataNew.time = 5;
                            jq_searchDataNew.dtrange = 1;
                            $("#jq_historyData").prev().find("span").text("历史信息");
                            //method.jq_QTimeRangeBind(jq_searchDataNew);
                            method.jq_search();
                        }
                    }
                });
                //结束时间
                layend = laydate.render({
                    elem: '#txtEndTime',
                    trigger: 'click',
                    min: method.changeTime(jq_searchData.stime),
                    done: function (value, date) {
                        laystart.config.max = {
                            year: date.year,
                            month: date.month - 1,//关键
                            date: date.date
                        }
                        jq_searchDataNew.endTime = value;
                        if ($.trim($("#txtStartTime").val()) != "") {
                            jq_searchDataNew.startTime = $.trim($("#txtStartTime").val());
                            jq_searchDataNew.time = 5;
                            jq_searchDataNew.dtrange = 1;
                            $("#jq_historyData").prev().find("span").text("历史信息");
                            //method.jq_QTimeRangeBind(jq_searchDataNew);
                            method.jq_search();
                        }
                    }
                });
                //if (isfirst)
                //    method.initTime();
                //加载layui select option title
                $("select[name='jq_ddl_zzzs'] option").each(function (index, element) {
                    var value = $(element).val();
                    var select = "dd[lay-value='" + value + "']";
                    $("select[name='jq_ddl_zzzs']").siblings("div.layui-form-select").find('dl').find(select).attr("title", value)
                });
                //加载搜索地区
                method.loadDiquData(diqusJson);
                //加载二级地区
                method.loadMulErjiDiqu();
                //$(".loadding_area").show();
                //加载相关搜索
                //method.getRelatedKwd(jq_searchDataNew.keywords);
                //获取查招标、查项目、查企业、查数据推荐关键词
                //method.getTjKwds(function () {
                //    method.hyp();
                //});
                $.fn.searchObj = {
                    currTag: 0,
                    objArry: [{
                        tag: 0,
                        currShowIndex: 0,
                        href: "/search?keywords=",
                        kwdsArry: []
                    }, {
                        tag: 1,
                        currShowIndex: 0,
                        href: "//www.bidcenter.com.cn/xiangmu?keywords=",
                        kwdsArry: []
                    }, {
                        tag: 2,
                        currShowIndex: 0,
                        href: "//user.bidcenter.com.cn/v2023/#/saasApply/qiqing-search?keywords=",
                        kwdsArry: []
                    }, {
                        tag: 3,
                        currShowIndex: 0,
                        href: "//shuju.bidcenter.com.cn/shuju/search-key.html?key=",
                        kwdsArry: []
                    }, {
                        tag: 4,
                        currShowIndex: 0,
                        href: "//credit.bidcenter.com.cn/credit/search.aspx?type=1&key=",
                        kwdsArry: []
                    }, {
                        tag: 5,
                        currShowIndex: 0,
                        href: "//user.bidcenter.com.cn/v2023/#/hetongshangji/index?kwd=",
                        kwdsArry: []
                    }]
                };
                //加载右侧推荐供应商
                method.loadRightData(jq_searchDataNew.keywords);
            })

        });
    },
    //设置cookie
    setCookie: function (cname, cvalue, domain, minutes) {
        var d = new Date();
        d.setTime(d.getTime() + (minutes * 60 * 1000));
        var expires = "expires=" + d.toGMTString();
        document.cookie = cname + "=" + encodeURIComponent(cvalue) + ";domain=" + domain + ";" + expires;
    },
    todetail: function (tourl) {
        window.open(tourl);
    },
    closeTop: function () {
        $(".ssjg-header2").hide();
        $(".ssjg-header_openbtn").show();
        topSearchShow = false;
    },
    openTop: function () {
        $(".ssjg-header2").show();
        $(".ssjg-header_openbtn").hide();
        topSearchShow = true;
    },
    //加载查招标、查项目、查企业、查数据推荐关键词
    getTjKwds: function (callback) {
        var params = { from: 6137, location: 6138, guid: guid, token: token };
        $.ajax({
            type: "POST",
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/index/TuijianKeywordsHandler.ashx"),
            data: params,
            dataType: "json",
            success: function (data) {
                if (data) {
                    console.log(data);
                    $.fn.searchObj = data.other2;
                    if (callback)
                        callback();
                }
            },
            error: function (e) { console.log(e); }
        });
    },
    hyp: function (change) {
        if ($.fn.searchObj) {
            var filterArry = $.fn.searchObj.objArry.filter(function (x) {
                return x.tag == $.fn.searchObj.currTag;
            });
            if (filterArry && filterArry.length > 0) {
                var obj = filterArry[0];
                if (obj.currShowIndex < obj.kwdsArry.length - 1 && change)
                    obj.currShowIndex += 1;
                else
                    obj.currShowIndex = 0;
                if (obj.kwdsArry.length > 1)
                    $(".gjc-change").show();
                else
                    $(".gjc-change").hide();
                var kwds = obj.kwdsArry[obj.currShowIndex];
                if (kwds && kwds.length > 0) {
                    var tjgjcHtml = [];
                    for (var i = 0; i < kwds.length; i++) {
                        var kwd = "", href = "";
                        if (kwds[i].kwd && kwds[i].href) {
                            kwd = kwds[i].kwd;
                            href = kwds[i].href;
                        } else {
                            kwd = kwds[i];
                            href = obj.href + encodeURIComponent(kwd);
                        }
                        if ($.trim(kwd) != "")
                            tjgjcHtml.push('<a href="' + href + '" ' + ($.fn.searchObj.currTag == 0 ? '' : 'target="_blank"') + ' title="' + kwd + '">' + kwd + '</a>');
                    }
                    $('.gjc-text[tag="' + $.fn.searchObj.currTag + '"]').html(tjgjcHtml.join(''));
                }
            }
        }
    }
}
//layui初始化后执行事件
function afterLayui(callback) {
    if (layerisload)
        callback();
    else {
        var timer = setInterval(function () {
            if (layerisload) {
                callback();
                clearInterval(timer);
            }
        }, 30);
    }
}
function tankLogin() {
    if (isEffectTank)
        jq_quick_r_register();
    return false;
}
function tankWanshan() {
    if (isEffectTank) {
        jq_quick_r_perfect2();
        return true;
    }
    return false;
}
//获取中小扶持公司
function GetFuChiCompanyArr() {
    var params = { from: 6137, location: 6138, guid: guid, token: token };
    $.ajax({
        type: "POST",
        url: interfaceConfig.serverURL + "/search/GetFuChiCompanyArrayListHandler.ashx",
        data: params,
        success: function (res) {
            var data = method.AESDecrypt(res);
            if (data.ret) {
                var arrlen = data.other2.list.length;
                var groupcount = Math.floor(arrlen / 2);

                var html = '<div class="fuchiList"><ul class="fuchiinfoList">';

                for (var i = 0; i < groupcount; i++) {
                    var j = (i + 1) * 2 - 1;
                    html += '<li class="fuchiindexLine"><div class="fuchiindex" style="margin-left: 20px;"><div style="float: left;"><img src="' + (data.other2.list[j - 1].logopath == "" ? "https://img.bidcenter.com.cn/search/search/image/v3/fcjh.png" : data.other2.list[j - 1].logopath) + '"></div><div style="float: left;margin-left: 20px;"><div><span class="fuchitag">扶</span><span style="font-size: 14px;">';
                    html += '<a target="' + (data.other2.list[j - 1].url == "" ? "_self" : "_blank") + '" href="' + (data.other2.list[j - 1].url == "" ? "https://search.bidcenter.com.cn/search?keywords=" + data.other2.list[j - 1].user_company : data.other2.list[j - 1].url) + '">' + data.other2.list[j - 1].user_company + '</a>';
                    html += '</span></div><div class="fuchiyewu">';
                    html += '' + data.other2.list[j - 1].yewu + '';
                    html += '</div></div></div>';
                    html += '<div class="fuchiindex"><div style="float: left;"><img src="' + (data.other2.list[j].logopath == "" ? "https://img.bidcenter.com.cn/search/search/image/v3/fcjh.png" : data.other2.list[j].logopath) + '"></div><div style="float: left;margin-left: 20px;"><div><span class="fuchitag">扶</span><span style="font-size: 14px;">';
                    html += '<a target="' + (data.other2.list[j].url == "" ? "_self" : "_blank") + '" href="' + (data.other2.list[j].url == "" ? "https://search.bidcenter.com.cn/search?keywords=" + data.other2.list[j].user_company : data.other2.list[j].url) + '">' + data.other2.list[j].user_company + '</a>';
                    html += '</span></div><div class="fuchiyewu">';
                    html += '' + data.other2.list[j].yewu + '';
                    html += '</div></div></div></li>';
                }

                //判断是否存在奇数个
                if (data.other2.list.length % 2 > 0) {
                    html += '<li class="fuchiindexLine"><div class="fuchiindex" style="margin-left: 20px;"><div style="float: left;"><img src="' + (data.other2.list[arrlen - 1].logopath == "" ? "https://img.bidcenter.com.cn/search/search/image/v3/fcjh.png" : data.other2.list[arrlen - 1].logopath) + '"></div><div style="float: left;margin-left: 20px;"><div><span class="fuchitag">扶</span><span style="font-size: 14px;">';
                    html += '<a target="' + (data.other2.list[arrlen - 1].url == "" ? "_self" : "_blank") + '" href="' + (data.other2.list[arrlen - 1].url == "" ? "https://search.bidcenter.com.cn/search?keywords=" + data.other2.list[arrlen - 1].user_company : data.other2.list[arrlen - 1].url) + '">' + data.other2.list[arrlen - 1].user_company + '</a>';
                    html += '</span></div><div class="fuchiyewu">';
                    html += '' + data.other2.list[arrlen - 1].yewu + '';
                    html += '</div></div></li>'
                }

                html += '</ul></div>';

                $(".fuchicell").append(html);
                if (arrlen > 0)
                    $(".fuchicell").show();
                else
                    $(".fuchicell").hide();

                if (arrlen > 2) {
                    $(".fuchiList").Scroll({
                        line: 1,
                        speed: 1000,
                        timer: 5000
                    });
                }
            }
            else {
                $(".fuchicell").hide();
            }
        },
        error: function (e) {
            $(".fuchicell").hide();
        }
    });
}
var storageFn = function (name) {
    return {
        set: function (val) {
            let old = localStorage.getItem(name);
            if (old) {
                // 如果old中有val，则中止
                if (old.indexOf(val) !== -1) {
                    return;
                }
                // 只存储最新添加的1000个id
                const arr = old.split(",");
                if (arr.length >= 1000) {
                    old = arr.slice(-1, 1000).join(",");
                }
                localStorage.setItem(name, old + "," + val);
            } else {
                localStorage.setItem(name, val + "");
            }
        },
        get: function () {
            return localStorage.getItem(name);
        },
    };
};

var clickedObj = {
    bx: storageFn("clickedbx"),
    pro: storageFn("clickedpro"),
};

var bid_storage = {
    /*
    追加数据
    key：用于限制位置类别
    value:存入的值
    limit_size:最大的条数，默认为不限制
    type:session 或 local storeage 传1时为localStorage
    */
    append: function (key, value, limit_size, type) {
        var key_name = "bid_storage_" + key;
        var exists_value = "";
        if (type == 1) {
            exists_value = localStorage.getItem(key_name)
        } else {
            exists_value = sessionStorage.getItem(key_name)
        }
        if (!exists_value)
            exists_value = "";
        var isExists = exists_value.length > 0 ? ("," + exists_value + ",").indexOf("," + value + ",") > -1 : false;
        if (!isExists) {
            var exists_value_arry = [];
            if (exists_value != "")
                exists_value_arry = exists_value.split(',');
            var isGoOn = true;
            if (limit_size && limit_size > 0) {
                while (isGoOn) {
                    isGoOn = exists_value_arry.length >= limit_size;
                    if (isGoOn) {
                        exists_value_arry.shift();
                    }

                }
            }
            exists_value_arry.push(value);
            if (type == 1) {
                localStorage.setItem(key_name, exists_value_arry.join(','))
            } else {
                sessionStorage.setItem(key_name, exists_value_arry.join(','))
            }
        }
    },
    /*获取数据*/
    get: function (key, type) {
        var key_name = "bid_storage_" + key;
        var exists_value = "";
        if (type == 1) {
            exists_value = localStorage.getItem(key_name)
        } else {
            exists_value = sessionStorage.getItem(key_name)
        }
        if (!exists_value) exists_value = "";
        return exists_value;
    }
}
function addStorage(news_id, news_type) {
    switch (news_type) {
        case "1":
        case "2":
        case "4":
        case "5":
        case "6":
        case "7":
        case "8":
        case "9":
            clickedObj.bx.set(news_id); break;
        case "31":
        case "32":
        case "33":
            clickedObj.bx.set(news_id); break;
        case "3":
        case "10":
        case "11":
        case "12":
        case "15":
        case "90":
        case "97":
        case "98":
        case "99":
            clickedObj.pro.set(news_id); break;
    }
    //if (news_id && news_id != '')
    //    bid_storage.append(7930, news_id, 1000, 1);
}
function addVisited() {
    //var value = bid_storage.get(7930, 1);
    //var valueBx = clickedObj.bx.get(),
    //   valuePro = clickedObj.pro.get();
    //var arrBx = [], arrPro = [], arr = [];
    //if (valueBx && valueBx != '')
    //    arrBx = valueBx.split(',');
    //if (valuePro && valuePro != '')
    //    arrPro = valuePro.split(',');
    try {
        var history = show_history.get();
        var arr = history.bx.concat(history.pro);
        $(".ssjg-list_bt a.ssjg-title").each(function (i, e) {
            var obj = $(e);
            if ($.inArray(parseInt(obj.attr('tid')), arr) > -1)
                obj.addClass("visited");
        });
    }
    catch (e) {
        console.log(e);
    };
    //if (arr && arr.length > 0) {
    //    $.each(arr, function (i, e) {
    //        $(".ssjg-list_bt a.ssjg-title[tid='" + e + "']").addClass("visited");
    //    });
    //}
}
//获取跨域URL
function getCrossDomainPostUrl(currURL) {
    //如果是跨域才走这个里处理
    if ((currURL.indexOf("http") == 0 || currURL.indexOf("//") == 0) && currURL.indexOf(location.host) == -1) {
        var isIELower = false;
        try {
            isIELower = navigator.appName == "Microsoft Internet Explorer" && parseInt(navigator.appVersion.split(";")[1].replace(/[ ]/g, "").replace("MSIE", "")) <= 9;
        } catch (e) {
        }
        if (isIELower) {
            console.log("您的浏览器版本过低，请使用IE9及以上版本");
            return "/JsonHandler/interfaceError/CrossDomainPostUrl.ashx?oldurl=" + encodeURIComponent(currURL);
        }
    }
    return currURL;
}

//存储localStorage
function addlocalStorageBySearch(value) {
    var tag = $(".search_cut.active").attr("tag");
    var key = "histroylist";
    if (tag == 2)
        key = "comhistroylist";

    var history = localStorage[key] ? eval(localStorage[key]) : [];
    var index = history.indexOf(value);
    if (index > -1)
        history.splice(index, 1);
    history.unshift(value);
    //超过10个，只取前十
    if (history.length > 10)
        history = history.slice(0, 10);
    localStorage[key] = JSON.stringify(history);
}

//加载searchelist
method.loadDiquJson();
method.jq_search();
method.layuiInit();
//基础数据初始化
method.baseDataInit();
$(function () {
    //是否登陆
    if (islogin) {
        $(".user_name").text(username).attr("title", username).attr("href", "//www.bidcenter.com.cn/BuserCenter/Index.aspx").attr("target", "_blank");
        $(".nologin").hide();
        $(".islogin").show();
    } else {
        $(".islogin").hide();
        $(".nologin").show();
    }
    //滚动条滚动事件
    $(window).scroll(function () {
        var cankaoTop = $(".shaixuan-gengduo").offset().top;
        var selector;
        if ($(document).scrollTop() >= cankaoTop) {
            if (topSearchShow) {
                $(".ssjg-header2,.ssjg-header_closebtn").show();
                $(".ssjg-header_openbtn").hide();
            } else {
                $(".ssjg-header2").hide();
                $(".ssjg-header_openbtn").show();
            }
            $.fn.SearchInput = "jq_search_keyword2";
            selector = $("#" + $.fn.SearchInput);
            $.fn.SearchTag = 0;

            if (selector.is(":focus"))
                $("#searchPop1").show();
        } else {
            topSearchShow = true;
            $.fn.SearchInput = "jq_search_keyword";
            selector = $("#" + $.fn.SearchInput);
            var offset = selector.offset();
            var h = selector.outerHeight();
            $(".ssjg-header2,.ssjg-header_openbtn").hide();
            var tag = $(".search_cut.active").attr("tag");
            $.fn.SearchTag = parseInt(tag);

            if (selector.is(":focus"))
                $("#searchPop").show();
        }
    });

    //二维码移入移除
    $("#ewmThumb,#ewmThumb2,.ewm_hover").mouseenter(function () {
        $(".ewm_hover").show();
    }).mouseleave(function () {
        $(".ewm_hover").hide();
    });
    //提示信息
    $(".notes-icon").mouseover(function () {
        $(this).next().show();
    }).mouseout(function () {
        $(this).next().hide();
    })

    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') method.tjgysCollapseAll();
    });

    $(".ddl_area .lishixinxi a").live('click', function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "采购方式、资金来源、评标办法、资质证书");
            return;
        }
        $(".ddl_area .lishixinxi ul").slideUp();
        if ($(this).next().is(':hidden'))
            $(this).next().slideDown();
    });
    $(".ddl_area .layui-input").live('focus', function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "资质证书");
            return;
        }
        $(".ddl_area .lishixinxi ul").slideUp();
    });
    $(".ddl_area .lishixinxi ul li a").live('click', function () {
        var obj = $(this);
        obj.parents('ul').prev().find('span').text(obj.text());
        obj.parents('ul').slideUp();
    });
    //点击新关键词搜索
    $("#jq_btn_search").click(function () {
        var kwd = $.trim($("#jq_search_keyword").val());
        if ($.fn.searchObj) {
            var filterArry = $.fn.searchObj.objArry.filter(function (x) {
                return x.tag == $.fn.searchObj.currTag;
            });
            if (filterArry && filterArry.length > 0) {
                if ($.fn.searchObj.currTag == 0) {
                    if (kwd != "" || resultData.isFufei)
                        location.href = "/search?keywords=" + encodeURIComponent(kwd);
                    else
                        $("#jq_search_keyword").focus();
                }
                else if (kwd != "")
                    window.open(filterArry[0].href + encodeURIComponent(kwd));
                else
                    window.open(filterArry[0].href.split('?')[0]);
            }
        }
    });
    //单选-地区点击
    $("#jq_intro_diqu li").live('click', function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        $("#jq_intro_diqu li").removeClass("active");
        $("#jq_show_diqu ul li a").removeClass("active");
        var obj = $(this);
        var tid = $(this).attr("tid");
        obj.addClass('active');
        if (tid == '0')
            jq_searchDataNew.diqu = "";
        else
            jq_searchDataNew.diqu = tid;
        jq_searchDataNew.diquArea = "";
        jq_searchDataNew.areacode = "";
        //筛选前 修改默认条件
        method.searchNewFieldInit();
        method.jq_search();
    });
    //单选-选择类别
    $("#jq_intro_type li").live('click', function () {
        var obj = $(this);
        var tid = obj.attr("tid");
        if (tid == "0" && !islogin)
            tankLogin();
        else {
            $("#jq_intro_type li").removeClass("active");
            $("#jq_show_type ul li a").removeClass("active");
            obj.addClass("active");
            jq_searchDataNew.type = tid;
            //筛选前 修改默认条件
            method.searchNewFieldInit();
            method.jq_search();
        }
    });
    //单选-小地区点击
    $("#jq_show_diquArea a").live("click", function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        jq_searchDataNew.diquArea = $.trim($(this).text());
        jq_searchDataNew.areacode = $.trim($(this).attr("value"));
        jq_searchDataNew.diqu = $("#jq_show_diquArea").attr("pid");
        method.jq_QDiquAreaBind(jq_searchDataNew);
        //筛选前 修改默认条件
        method.searchNewFieldInit();
        method.jq_search();
    });
    //多选-地区点击
    $("#jq_show_diqu ul li a").live('click', function () {
        var obj = $(this);
        var piece = obj.parents('.quyu-label');
        var li = obj.parents('li');
        if (obj.hasClass('checkbox')) {
            if (!obj.hasClass('quanguo'))
                $("#jq_show_diqu ul li a.yiji.quanguo").removeClass("active");
            //全国
            if (obj.hasClass('quanguo')) {
                if (obj.hasClass('active'))
                    jq_didu_fn.c_qingkong();
                else {
                    jq_didu_fn.c_qingkong();
                    obj.addClass("active");
                }
            } else if (obj.hasClass('quyu')) {
                if (obj.hasClass('active'))
                    li.find('a.yiji').removeClass('active');
                else
                    li.find('a.yiji').addClass('active');
            } else if (obj.hasClass("quanbu")) {
                var currArea = obj.parents(".quyu-hover");
                var pid = currArea.attr('pid');
                var yiji = $("#jq_show_diqu ul li a.yiji[tid=" + pid + "]");
                yiji.removeClass("active2")
                if (obj.hasClass('active')) {
                    obj.removeClass("active");
                    if (yiji.hasClass('active'))
                        yiji.removeClass("active");
                }
                else {
                    currArea.find("a").removeClass('active');
                    obj.addClass("active");
                    if (!yiji.hasClass('active'))
                        yiji.addClass('active');
                }
            } else if (obj.hasClass('erji')) {
                //获取当前省市地区dom
                var currArea = obj.parents(".quyu-hover");
                //获取当前城市所属区域dom
                var currLi = obj.parents("li");
                //获取一级地区id
                var pid = currArea.attr('pid');
                //获取一级地区dom
                var yiji = $("#jq_show_diqu ul li a.yiji[tid=" + pid + "]");
                var totalCount = currArea.find('a:not(.quanbu)').length;
                var yijiTotalCount = currLi.find('a.yiji:not(.quyu)').length;
                if (obj.hasClass('active')) {
                    obj.removeClass('active');
                }
                else {
                    obj.addClass('active');
                    if (!yiji.hasClass('active'))
                        yiji.addClass('active');
                }
                var selCount = currArea.find('a.active:not(.quanbu)').length;
                if (selCount == totalCount) {
                    currArea.find('a.quanbu').addClass('active');
                    currArea.find('a:not(.quanbu)').removeClass("active");
                    if (yiji.hasClass('active2'))
                        yiji.removeClass("active2");
                    if (!yiji.hasClass('active'))
                        yiji.addClass('active');
                }
                else {
                    currArea.find('a.quanbu').removeClass('active');
                    if (yiji.hasClass('active'))
                        yiji.removeClass("active");
                    yiji.addClass('active2')
                }
                var yijiSelCount = currLi.find('a.yiji.active:not(.quyu)').length;
                if (yijiSelCount == yijiTotalCount)
                    currLi.find('a.yiji.quyu').addClass("active");
                else
                    currLi.find('a.yiji.quyu').removeClass("active");
            } else {
                var erjiArea = obj.prev();
                var totalCount = li.find('a.yiji:not(.quyu)').length;
                if (obj.hasClass('active')) {
                    obj.removeClass('active');
                    erjiArea.find('a').removeClass('active');
                }
                else
                    obj.addClass('active');
                var selCount = li.find('a.yiji.active:not(.quyu)').length;
                if (selCount == totalCount)
                    li.find('a.yiji.quyu').addClass("active");
                else
                    li.find('a.yiji.quyu').removeClass("active");
            }
        } else {
            if (obj.hasClass("current")) {
                obj.removeClass("current");
                piece.find("a.yiji.checkbox").show();
                obj.prev().hide();
            } else {
                //关闭其它二级地区
                $("#jq_show_diqu ul li a.diqu_text").removeClass("current");
                $("#jq_show_diqu ul li a.yiji.checkbox").show();
                $("#jq_show_diqu ul li .quyu-hover").hide();

                obj.addClass("current");
                piece.find("a.yiji.checkbox").hide();
                obj.prev().show();
            }
        }
    });
    //多选-鼠标滑过显示二级地区
    $("#jq_show_diqu ul li .province").live('mouseover', function () {
        var obj = $(this).find("a.diqu_text");
        //关闭其它二级地区
        $("#jq_show_diqu ul li a.diqu_text").removeClass("current");
        $("#jq_show_diqu ul li a.yiji.checkbox").show();
        $("#jq_show_diqu ul li .quyu-hover").hide();

        obj.addClass("current");
        obj.parents('.quyu-label').find("a.yiji.checkbox").hide();
        obj.prev().show();
    }).live('mouseout', function () {
        var obj = $(this).find("a.diqu_text");
        obj.removeClass("current");
        obj.parents('.quyu-label').find("a.yiji.checkbox").show();
        obj.prev().hide();
    });
    //多选-类别点击
    $("#jq_show_type ul li a").live("click", function () {
        var obj = $(this);
        var li = obj.parents('li');
        //全国
        if (obj.hasClass('quantype')) {
            if (obj.hasClass('active'))
                jq_type_fn.c_qingkong();
            else
                jq_type_fn.c_quanxuan();
        } else if (obj.hasClass('quyu')) {
            if (obj.hasClass('active'))
                li.find('a').removeClass('active');
            else
                li.find('a').addClass('active');
        } else {
            if (obj.hasClass('active'))
                obj.removeClass('active');
            else
                obj.addClass('active');
        }
    });
    //删除选中条件
    $("#jq_search_params ul li a .shanchu_city-icon,#jq_search_params2 ul li a .shanchu_city-icon").live('click', function () {
        var obj = $(this);
        var li = obj.parents('li');
        li.remove();
        var tid = li.attr('tid'), tcode = li.attr('tcode');
        $("#jq_intro_diqu li[tid=" + tid + "]").removeClass("active");
        $("#jq_show_diqu ul li a[tid=" + tid + "]").removeClass("active").removeClass("active2");
        $("#jq_show_diqu ul li .quyu-hover a.erji[value=" + tcode + "]").removeClass("active");
        method.jq_check_checkedDiqu();
        method.jq_diqus_sure();
    });
    $("#jq_search_params ul li a .shanchu-icon,#jq_search_params2 ul li a .shanchu-icon").live('click', function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        var obj = $(this);
        var li;
        if (obj.hasClass("erji"))
            li = obj.parents('li.erji');
        else
            li = obj.parents('li');
        li.remove();
        var tid = li.attr('tid');
        if (li.attr("type") == "1") {
            $("#jq_intro_diqu li[tid=" + tid + "]").removeClass("active");
            $("#jq_show_diqu ul li a[tid=" + tid + "]").removeClass("active").removeClass("active2");
            $("#jq_show_diqu ul li .quyu-hover[pid=" + tid + "] a.erji").removeClass("active");
            method.jq_check_checkedDiqu();
            method.jq_diqus_sure();
        } else if (li.attr("type") == "2") {
            $("#jq_intro_type li[tid=" + tid + "]").removeClass("active");
            $("#jq_show_type ul li a[tid=" + tid + "]").removeClass("active");
            method.jq_check_checkedType();
            method.jq_types_sure();
        } else if (li.attr("type") == "3") {
            $("#jq_dvTime ul.search_days li a").removeClass("active");
            $("#jq_dvTime ul.search_days li[tid='0'] a").addClass("active");
            $("#jq_historyData").prev().find("span").text("历史信息");
            jq_searchDataNew.time = 0;
            method.jq_search();
        } else if (li.attr("type") == "4") {//筛选范围
            jq_searchDataNew.tag = 0;
            method.jq_search();
        } else if (li.attr("type") == "5") {//筛选模式
            jq_searchDataNew.mod = 0;
            method.jq_search();
        } else if (li.attr("type") == "6") {//项目金额
            jq_searchDataNew.zbjefw = 0;
            method.jq_search();
        } else if (li.attr("type") == "7") {//采购方式
            jq_cgfs_fn.c_qingkong();
            jq_searchDataNew.ext_cgfs = "";
            method.jq_search();
        } else if (li.attr("type") == "8") {//资金来源
            jq_zjly_fn.c_qingkong();
            jq_searchDataNew.ext_zjly = "";
            method.jq_search();
        } else if (li.attr("type") == "9") {//评标办法
            jq_pbbf_fn.c_qingkong();
            jq_searchDataNew.ext_pbbf = "";
            method.jq_search();
        } else if (li.attr("type") == "10") {//资质证书
            jq_zzzs_fn.c_qingkong();
            jq_searchDataNew.zzzs = "";
            method.jq_search();
        } else if (li.attr("type") == "11") {//排除词
            if (tid && tid != "") {
                $(".paichuci-list .paichuci span").each(function (index, element) {
                    if ($(element).html() == tid)
                        $(element).parent().remove();
                });
                var pccs = jq_searchData.excode.split(',');
                jq_searchDataNew.excode = pccs.filter(function (x) {
                    return x != tid;
                }).join(',');
            } else {
                method.jq_clearsubpaichuci(0);
                jq_searchDataNew.excode = "";
            }
            method.jq_search();
        } else if (li.attr("type") == "12") {//相关词
            if (tid && tid != "") {
                $(".xiangguanci-list .xiangguanci span").each(function (index, element) {
                    if ($(element).html() == tid)
                        $(element).parent().remove();
                });

                var xgcs = jq_searchData.kwordtagh.split(',');
                jq_searchDataNew.kwordtagh = xgcs.filter(function (x) {
                    return x != tid;
                }).join(',');
            } else {
                method.jq_clearsubxiangguanci(0);
                jq_searchDataNew.kwordtagh = "";
            }
            method.jq_search();
        } else if (li.attr("type") == "13") {//排除词范围
            jq_searchDataNew.paichutag = 0;
            method.jq_search();
        } else if (li.attr("type") == "14") {//相关词范围
            jq_searchDataNew.xiangguantag = 0;
            method.jq_search();
        }
        if ($("#jq_search_params ul li").length == 0)
            method.jq_clearParSta();
    });
    //时间选择
    $("#jq_dvTime ul.search_days li").live('click', function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        //清空时间范围
        $("#txtStartTime").val("");
        $("#txtEndTime").val("");
        var obj = $(this);
        var currTime = parseInt(obj.attr("tid"));
        if (currTime != 180) {
            if (!islogin) {
                tankLogin();
                return;
            }
            else if (currTime == "11") {
                if (!islogin) {
                    tankLogin();
                    return;
                }
                else if (!isWanshan && tankWanshan()) {
                    return;
                }
                else if (!resultData.isFufei) {
                    method.showAllowTank(".allow_mianfei", "搜索最近一年");
                    return;
                }
            }
            jq_searchDataNew.dtrange = 5;//如果选择近一年，则默认最近库即可
        } else
            jq_searchDataNew.dtrange = 4;//如果选择近一年，则默认最近库即可
        $("#jq_historyData").prev().find("span").text("历史信息");
        jq_searchDataNew.time = currTime;
        //method.jq_QTimeBind(jq_searchDataNew);
        method.jq_search();

    });
    //选择筛选模式
    $("#jq_dvMod ul li").live('click', function () {
        if (!islogin)
            tankLogin();
        else if (!isWanshan)
            tankWanshan();
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "精准搜索");
        } else {
            jq_searchDataNew.mod = parseInt($(this).attr("tid"));
            method.jq_QModBind(jq_searchDataNew);

            //筛选前 修改默认条件
            method.searchNewFieldInit();
            method.jq_search();
        }
    });

    //选择排除词模式
    $("#jq_dvPaiChuCiTag ul li").live('click', function () {
        var nTag = $(this).attr("tid");
        if (nTag == "2") {
            if (!islogin) {
                tankLogin();
                return;
            } else if (!isWanshan && tankWanshan()) {
                return;
            } else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "搜索不包含附件");
                return;
            }
        }
        jq_searchDataNew.paichutag = parseInt(nTag);
        method.jq_QPaiChuTagBind(jq_searchDataNew);
        //筛选前 修改默认条件
        method.searchNewFieldInit();
        method.jq_search();
    });

    //选择相关词模式
    $("#jq_dvXiangGuanCiTag ul li").live('click', function () {
        var nTag = $(this).attr("tid");
        if (nTag == "2") {
            if (!islogin) {
                tankLogin();
                return;
            } else if (!isWanshan && tankWanshan()) {
                return;
            } else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "搜索不包含附件");
                return;
            }
        }
        jq_searchDataNew.xiangguantag = parseInt(nTag);
        method.jq_QXiangGuanTagBind(jq_searchDataNew);
        //筛选前 修改默认条件
        method.searchNewFieldInit();
        method.jq_search();
    });

    //搜索范围
    $("#jq_dvTag ul li").live('click', function () {
        var nTag = $(this).attr("tid");
        if (nTag == "2") {
            if (!islogin) {
                tankLogin();
                return;
            } else if (!isWanshan && tankWanshan()) {
                return;
            } else if (!resultData.isFufei) {
                method.showAllowTank(".allow_mianfei", "搜索不包含附件");
                return;
            }
        }
        jq_searchDataNew.tag = parseInt(nTag);
        method.jq_QTagBind(jq_searchDataNew);
        //筛选前 修改默认条件
        method.searchNewFieldInit();
        method.jq_search();
    });
    //历史数据筛选
    $("#jq_historyData li").live('click', function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        //清空时间范围
        $("#txtStartTime").val("");
        $("#txtEndTime").val("");
        var tid = $(this).attr("tid");
        if (tid != "") {
            var currHistorData = parseInt(tid);
            jq_searchDataNew.dtrange = currHistorData;
        } else
            jq_searchDataNew.dtrange = 4;
        method.jq_search();
    });
    //项目金额
    $("#jq_zhaobjine ul li").live('click', function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        else if (!resultData.isFufei) {
            method.showAllowTank(".allow_mianfei", "项目金额");
            return;
        }
        var tid = $(this).attr("tid");
        jq_searchDataNew.zbjefw = tid;
        jq_searchDataNew.zbje_min = 0
        jq_searchDataNew.zbje_max = 0
        method.jq_search();
    });
    //采购方式、资金来源、评标办法
    $("#jq_ddl_cgfs li,#jq_ddl_zjly li,#jq_ddl_pbbf li").live('click', function () {
        if (!isLoadBase) return;
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        var tid = $(this).attr("tid");
        var ttype = $(this).parent().attr("ttype");
        switch (ttype) {
            case "1":
                if (!resultData.isFufei) {
                    method.showAllowTank(".allow_mianfei", "采购方式");
                    return;
                }
                jq_searchDataNew.ext_cgfs = tid;
                if (tid && tid != "") {
                    var tStr = baseData.cgfsList.filter(function (element) {
                        return element.key == tid;
                    })[0].value;
                    method.jq_addSearchParams(7, tid, tStr);
                }
                break;
            case "2":
                if (!resultData.isFufei) {
                    method.showAllowTank(".allow_mianfei", "资金来源");
                    return;
                }
                jq_searchDataNew.ext_zjly = tid;
                if (tid && tid != "") {
                    var tStr = baseData.zjlyList.filter(function (element) {
                        return element.key == tid;
                    })[0].value;
                    method.jq_addSearchParams(8, tid, tStr);
                }
                break;
            case "3":
                if (!resultData.isFufei) {
                    method.showAllowTank(".allow_mianfei", "评标办法");
                    return;
                }
                jq_searchDataNew.ext_pbbf = tid;
                if (tid && tid != "") {
                    var tStr = baseData.pbbfList.filter(function (element) {
                        return element.key == tid;
                    })[0].value;
                    method.jq_addSearchParams(9, tid, tStr);
                }
                break;
        }
        method.jq_search();
    });
    //资质证书筛选
    $("#jq_ddl_zzzs li").live('click', function () {
        if (!islogin) {
            tankLogin();
            return;
        }
        else if (!isWanshan && tankWanshan()) {
            return;
        }
        var value = $.trim($(this).attr("tid"));
        jq_searchDataNew.zzzs = value;
        method.jq_search();
    });
    //列表数据点击添加关键词cookie
    $(".add_kwd_cookie").live('click', function () {
        method.setCookie("keywordsAllYuanArry", "", -1);
        if (jq_searchData.keywordsAllYuanArry && jq_searchData.keywordsAllYuanArry.length > 0)
            method.setCookie("keywordsAllYuanArry", jq_searchData.keywordsAllYuanArry, ".bidcenter.com.cn", 20);
    });
    //下一页点击
    $(".layui-laypage-next").live('click', function () {
        if ($(this).hasClass("layui-last")) {
            if (resultData.next_token && resultData.next_token != "") {
                nextToken = resultData.next_token;
                jq_searchDataNew.page = jq_searchData.page + 1;
                variate.isPageLoad = true;
                method.jq_search();
            }
        }
    });
    //文本输入按钮效果
    $("input[name='zbje']").live('keyup', function () {
        if ($.trim($("#zbje_min").val()) != "" && $.trim($("#zbje_max").val()) != "")
            $("#btn_jine").addClass("active");
        else
            $("#btn_jine").removeClass("active");
    });
    $("input[name='kwordh']").live('keyup', function () {
        if ($.trim($("#kwordh1").val()) != "" || $.trim($("#kwordh2").val()) != "" || $.trim($("#kwordh3").val()) != "")
            $("#btn_kwordh").addClass("active");
        else
            $("#btn_kwordh").removeClass("active");
    });
    //全选
    $(".check_all").live('change', function () {
        var obj = $(this);
        if (obj.is(':checked'))
            $("#searchListArea input[type='checkbox'][name=ids]").prop('checked', true);
        else
            $("#searchListArea input[type='checkbox'][name=ids]").prop('checked', false);
    })
    $(".add_dingyue").live('click', function () {
        window.open("//user.bidcenter.com.cn/v2023/#/customCenter/customInfo?type=1&operation=add&fenxikeywordlist=" + jq_searchData.keywords, "_blank");
    })
    //推荐项目点击切换
    $(".tjxm-gjc li").live('click', function () {
        var obj = $(this);
        $(".tjxm-gjc li").removeClass("active");
        obj.addClass("active");
        currTjKwd = obj.text();
        method.jq_search(undefined, false, false, false);
    });
    $(".ddl_params").live('mouseover', function () {
        $(this).find("ul").show();
    }).live('mouseout', function () {
        $(this).find("ul").hide();
    })
    //问号提示效果
    $(".note-rhss,.zhushi-box").live('mouseover', function () {
        $(this).next().show();
    }).live('mouseout', function () {
        $(this).next().hide();
    })
    //信息导出效果
    $(".daochu-btn,.daochu-hover").live('mouseover', function () {
        $(".daochu-hover").show();
    }).live('mouseout', function () {
        $(".daochu-hover").hide();
    });
    //搜索标签切换
    $(".search_cut").live('click', function () {
        var obj = $(this);
        if ($.fn.searchObj) {
            $.fn.searchObj.currTag = parseInt(obj.attr("tag"));
            $.fn.SearchTag = $.fn.searchObj.currTag;
            $(".search_cut").removeClass("active");
            obj.addClass("active");
            $(".gjc-text").hide();
            $(".ssjg-xgss").show();
            $(".gjc-text[tag='" + $.fn.searchObj.currTag + "']").show();
            if ($.fn.searchObj.currTag == 0)
                $("#jq_search_keyword").val(jq_searchData.keywords);
            else
                $("#jq_search_keyword").val("");
            var placeholder = "请输入您的产品关键词，多个词请用逗号隔开";
            switch ($.fn.searchObj.currTag) {
                case 1:
                    placeholder = "请输入工程项目名称关键词，多个词请用逗号隔开";
                    break;
                case 2:
                    placeholder = "请输入要搜索的企业名称，如“北京海诚通胜网络科技有限公司”或“海诚通胜”";
                    break;
                case 3:
                    placeholder = "请输入行业或产品关键词，如“防水工程”";
                    break;
                case 4:
                    placeholder = "请输入企业名称或统一社会信用代码";
                    break;
                case 5:
                    placeholder = "请输入适用的关键词，查询合同到期商机";
                    $(".ssjg-xgss").hide();
                    break;
            }
            currTag = $.fn.searchObj.currTag;
            $("#jq_search_keyword").attr("placeholder", placeholder);
            method.hyp();
        }
    });
    //右侧浮动控制
    var ishover = false;
    $(".right_shouqi").live("click", function () {
        $(".tag_all,.right_shouqi").hide();
        $(".right_zhankai").show();
        $(".extra-wrap").css("margin-top", "38px");
    });
    $(".right_zhankai").live("click", function () {
        ishover = false;
        $(".tag_all,.right_shouqi").show();
        $(".right_shouqi").show();
        $(".right_zhankai").hide();
        $(".extra-wrap").css("margin-top", "-265px");
    }).mouseenter(function () {
        if (ishover) {
            $(".tag_all").show();
            $(".extra-wrap").css("margin-top", "-265px");
        }
    }).mouseleave(function () {
        if ($(".right_zhankai").is(':visible')) {
            ishover = true;
            $(".tag_all").hide();
            $(".extra-wrap").css("margin-top", "38px");
        }
    });
    // 下载App
    $('.xiazaiApp a').mouseenter(function () {
        $(this).next().show();
    }).mouseleave(function () {
        $(this).next().hide();
    });
    // 关注微信
    $('.lianxifangshi li').each(function () {
        var $li = $(this);
        var $trigger = $li.find('a');
        var $popup = $trigger.next();

        // 鼠标进入父容器时显示弹窗
        $li.mouseenter(function () {
            if ($li.is('#bidcenter_qidian')) {
                renderZaiXianKF();

            }
            $popup.show();

        });

        // 鼠标离开父容器时隐藏弹窗
        $li.mouseleave(function () {
            $popup.hide();
        });
    });
    $(".zaixiankefu").click(function () {
        window.open("http://wpa.b.qq.com/cgi/wpa.php?ln=1&key=XzkzODE4NDE0MV80Nzg5MTBfNDAwODEwOTY4OF8yXw");
    })
    //保存桌面快捷方式
    $("#btnShengCheng").click(function () {
        var currUrl = location.origin + location.pathname;
        if (searchParams.length > 0)
            currUrl += "?" + searchParams.join('&');
        window.open("http://down.bidcenter.com.cn/shengcheng.php?url=" + encodeURIComponent(currUrl) + "&name=" + encodeURIComponent(jq_searchData.keywords.replace('+', '&')));
    });
    //回到顶部
    $(".backTop-icon").click(function () {
        method.backTop();
    });
    //跳转登录
    $(".jq_tologin").live('click', function () {
        pub.login('7D24909FC08A6E08203D5A005AC7D5DC');
    });
    //完善信息
    $(".jq_wanshan").live('click', function () {
        tankWanshan();
    })
    //客服咨询
    function renderZaiXianKF() {
        var kfData = getZhibanKefu()
        if (kfData && kfData.QRCode) {
            $(".xiangmuzixun_kf img").attr("src", kfData.QRCode + "?x-oss-process=style/sl_100x100" || "");
        }
    }
    function getZhibanKefu() {
        // 1. 配置项：缓存key + 过期时间（单位：毫秒，示例：24小时=86400000ms，可自定义）
        const kefuCacheKey = "zhibanKefuContactInfo";
        const EXPIRE_TIME = 1 * 60 * 60 * 1000; // 缓存有效期：24小时，可改为1小时=3600000ms等
        let kefuInfo = null;

        // 2. 从LocalStorage读取缓存（缓存为「数据+过期时间」的组合对象）
        const cacheStr = localStorage.getItem(kefuCacheKey);
        if (cacheStr) {
            try {
                // 解析缓存的组合对象：{ data: 客服信息, expire: 过期时间戳 }
                const cacheObj = JSON.parse(cacheStr);
                // 校验缓存：是否有数据 + 是否未过期（当前时间 < 过期时间）
                if (cacheObj.data && cacheObj.expire && Date.now() < cacheObj.expire) {
                    // 缓存有效：直接取真实客服数据
                    kefuInfo = cacheObj.data;
                    // 校验核心字段，防止缓存数据残缺
                    if (!kefuInfo.Biduname || !kefuInfo.Bidumobile) {
                        kefuInfo = null;
                        localStorage.removeItem(kefuCacheKey);
                    }
                } else {
                    // 缓存过期/无有效数据：删除过期缓存
                    localStorage.removeItem(kefuCacheKey);
                    console.log("客服缓存已过期，将重新请求接口");
                }
            } catch (e) {
                // 缓存损坏：删除缓存，重新请求
                console.log("客服缓存解析失败，将重新请求接口：", e);
                localStorage.removeItem(kefuCacheKey);
            }
        }

        // 3. 有有效缓存：直接返回，无需调接口
        if (kefuInfo) {
            return kefuInfo;
        }

        // 4. 无有效缓存/缓存过期：调用接口获取数据（同步请求保证返回值）
        $.ajax({
            type: "POST",
            async: false,
            data: { from: 6137, location: 6138, guid: guid, token: token, noen: 1 },
            url: getCrossDomainPostUrl(interfaceConfig.serverURL + "/User/custom/PC/GetCustomerContactZhibanHandler.ashx"),
            dataType: "json",
            success: function (data) {
                // 多层校验接口返回数据有效性
                if (data && data.ret && data.other2 && data.other2.lianxifangsi) {
                    kefuInfo = data.other2.lianxifangsi;
                    // 校验核心字段，仅缓存有效数据
                    if (kefuInfo.Biduname && kefuInfo.Bidumobile) {
                        // 存储「数据+过期时间」的组合对象到LocalStorage
                        const cacheValue = {
                            data: kefuInfo, // 真实的客服信息数据
                            expire: Date.now() + EXPIRE_TIME // 过期时间戳：当前时间+有效期
                        };
                        localStorage.setItem(kefuCacheKey, JSON.stringify(cacheValue));
                    }
                }
            },
            error: function (e) {
                console.log("请求专属客服接口失败：", e);
            }
        });

        // 5. 返回最终客服信息对象（有效则返回，无则null）
        return kefuInfo;
    }
})