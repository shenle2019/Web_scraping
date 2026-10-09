//关于地区的方法
var jq_didu_fn = {
    s_default: function () {//默认
        $("#jq_diqu_duoxuan,#searchDiquArea,#jq_diqu_gengduo").show();
        $("#jq_show_diqu").slideUp();
    },
    s_gengduo: function () {
        $("#jq_intro_diqu").css("height", "auto");
        $("#jq_diqu_gengduo").hide();
        $("#jq_diqu_shouqi").show();
    },
    s_shouqi: function () {
        $("#jq_intro_diqu").css("height", "26px");
        $("#jq_diqu_gengduo").show();
        $("#jq_diqu_shouqi").hide();
    },
    s_duoxuan: function () { //多选
        $("#jq_show_diqu").slideDown();
        $("#jq_diqu_duoxuan,#searchDiquArea,#jq_show_diquArea,.jq_diqu_handler").hide();
    },
    s_xuanzhong: function (tids) {//选中地区 tids为筛选条件 如：“[tid='1'],[tid='2']”
        if (tids && tids.length > 0) {
            $("#jq_intro_diqu li").filter(tids.join(',')).addClass("active");
            $("#jq_show_diqu ul li a.yiji").filter(tids.join(',')).addClass('active');
        } else {
            $("#jq_intro_diqu li[tid='0']").addClass("active");
            $("#jq_show_diqu ul li a.yiji.quanguo").addClass('active');
        }
    },
    s_xdqXuanzhong: function (xdqArr) {//小地区选中 xdqArr：小地区数组
        if (xdqArr.length > 0) {
            for (var i = 0 ; i < xdqArr.length; i++) {
                //$("#jq_show_diquArea a:contains('" + xdqArr[i] + "')").addClass("active");
                //$("#jq_show_diqu ul li .quyu-hover a:contains('" + xdqArr[i] + "')").each(function (index, element) {
                //    $(element).addClass("active");
                //    var currArea = $(element).parents(".quyu-hover");
                //    currArea.prev().removeClass("active").addClass("active2");
                //});
                $("#jq_show_diquArea a[value='" + xdqArr[i] + "']").addClass("active");
                $("#jq_show_diqu ul li .quyu-hover a[value='" + xdqArr[i] + "']").each(function (index, element) {
                    $(element).addClass("active");
                    var currArea = $(element).parents(".quyu-hover");
                    currArea.prev().removeClass("active").addClass("active2");
                });
            }
        }
    },
    c_quanxuan: function () { //全选
        $("#jq_show_diqu ul li a.yiji").addClass("active");
    },
    c_qingkong: function () {//清空
        $("#jq_intro_diqu li").removeClass("active");
        $("#jq_show_diqu ul li a").removeClass("active").removeClass("active2");
    }
};
//关于类型的方法
var jq_type_fn = {
    s_default: function () {//默认
        $('#jq_type_duoxuan,#jq_intro_type,#jq_type_gengduo').show();
        $('#jq_show_type').slideUp();
    },
    s_gengduo: function () {
        $("#jq_intro_type").css("height", "auto");
        $("#jq_type_gengduo").hide();
        $("#jq_type_shouqi").show();
    },
    s_shouqi: function () {
        $("#jq_intro_type").css("height", "26px");
        $("#jq_type_gengduo").show();
        $("#jq_type_shouqi").hide();
    },
    s_duoxuan: function () { //多选
        $('#jq_show_type').slideDown();
        $('#jq_type_duoxuan,#jq_intro_type,.jq_type_handler').hide();
    },
    s_xuanzhong: function (tids) {//选中类别 tids为筛选条件 如：“[tid='1'],[tid='2']”
        if (tids && tids.length > 0) {
            $("#jq_intro_type li").filter(tids.join(',')).addClass("active");
            $("#jq_show_type ul li a").filter(tids.join(',')).addClass('active');
        } else {
            $("#jq_intro_type li[tid='-1']").addClass("active");
            $("#jq_show_type ul li a.quantype").addClass('active');
        }
    },
    c_quanxuan: function () { //全选
        $("#jq_show_type ul li a").addClass("active");
    },
    c_qingkong: function () {//清空
        $("#jq_intro_type li").removeClass("active");
        $("#jq_show_type ul li a").removeClass("active");
    }
}
//关于发布时间的方法
var jq_time_fn = {
    c_qingkong: function () {//清空
        $("#jq_dvTime ul.search_days li a").removeClass("active");
        $("#jq_dvTime ul.search_days li[tid='0'] a").addClass("active");
    }
}
//关于自定义时间的方法
var jq_customTime_fn = {
    c_qingkong: function () {//清空
        $("#txtStartTime").val("");
        $("#txtEndTime").val("");
    }
}
//关于历史信息的方法
var jq_history_fn = {
    c_qingkong: function () {//清空
        $("#jq_historyData").prev().find("span").text("历史信息");
    }
}
//关于筛选范围的方法
var jq_tag_fn = {
    c_qingkong: function () {//清空
        $("#jq_dvTag ul li").removeClass("active");
        $("#jq_dvTag ul li[tid='0']").addClass("active");
    }
}
//关于筛选模式的方法
var jq_mod_fn = {
    c_qingkong: function (tid) {//清空
        $("#jq_dvMod ul li").removeClass("active");
        $("#jq_dvMod ul li[tid='" + tid + "']").addClass("active");
    }
}
//关于项目金额的方法
var jq_zbje_fn = {
    c_qingkong: function (tid) {//清空
        $("#jq_zhaobjine ul li").removeClass("active");
        $("#jq_zhaobjine ul li[tid='0']").addClass("active");
    }
}
//关于自定义金额的方法
var jq_customZbje_fn = {
    c_qingkong: function (tid) {//清空
        $("#zbje_min").val("");
        $("#zbje_max").val("");
    }
}
//关于采购方式的方法
var jq_cgfs_fn = {
    c_qingkong: function (tid) {//清空
        $("#jq_ddl_cgfs").prev().find("span").text("全部");
    }
}
//关于资金来源的方法
var jq_zjly_fn = {
    c_qingkong: function (tid) {//清空
        $("#jq_ddl_zjly").prev().find("span").text("全部");
    }
}
//关于评标办法的方法
var jq_pbbf_fn = {
    c_qingkong: function (tid) {//清空
        $("#jq_ddl_pbbf").prev().find("span").text("全部");
    }
}
//关于资质证书的方法
var jq_zzzs_fn = {
    c_qingkong: function (tid) {//清空
        $("#jq_ddl_zzzs").prev().find("span").text("全部");
    }
}
//关于排除词的方法
var jq_excode_fn = {
    c_qingkong: function (tid) {//清空
        $("input[name='excode']").val("");
    }
}
//关于相关词的方法
var jq_kwordh_fn = {
    c_qingkong: function (tid) {//清空
        $("input[name='kwordh']").val("");
    }
}