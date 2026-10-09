$(document).ready(function () {
    $("input[class*=sousou]") //所有样式名中含有grayTips的input   
        .each(function () {
            var oldVal = $(this).val();   //默认的提示性文本   
            $(this)
           .css({ "color": "#a6a6a6" })  //灰色   
           .focus(function () {
               if ($(this).val() != oldVal) {
                   $(this).css({ "color": "#000000" });
               } else { $(this).val("").css({ "color": "#000000" }); }
           })
           .blur(function () {
               if ($(this).val() == "") { $(this).val(oldVal).css({ "color": "#a6a6a6" }); }
           })
           .keydown(function () {
               $(this).css({ "color": "#000000" });
           })
        })

    $("#denglu").click(function () {
        pub.loginMember("");
    });

    $(".js_N_navLogout").click(function () {
        pub.logoutMember();
        return false;
    });
});
function ClearCookiexx() {
    pub.logoutMember();
    return false;
}

function zhuce() {
    window.open('/zhuce.html')
}
var pub = {
    loginMember: function (torigin) {
        var name = $("#txtUserName");
        var pwd = $("#txtUserPwd");
        var flag_jzmm = 0;
        var flag_jzyhm = 1;

        if ($.trim(name.val()) == "" || $.trim(name.val()) == null || name.val() == "请输入用户名") {
            alert("请输入用户名");
            name.focus();
            return false;
        }

        if ($.trim(pwd.val()) == "" || $.trim(pwd.val()) == null || pwd.val() == "请输入密码") {
            alert("请输入密码");
            pwd.focus();
            return false;
        }

        var o = [];
        var dt = new Date();
        var srctime = dt.getTime();
        o.push("https://sso.bidcenter.com.cn/member_login_crs");
        o.push("?callback=");
        o.push(srctime);
        o.push("&jsoncallback=?");
        $(".laoding").css("display", "block");
        $(".weidenglu").css("display", "none");
        $.getJSON(o.join(""), { "name": name.val(), "pwd": pwd.val(), "auto": flag_jzmm, "run": flag_jzyhm, "origin": torigin }, function (r) {
            if (r.status == "true") {
                setTimeout("laoding()", 1000);
            } else {
                alert(decodeURIComponent(r.brief));
                $(".weidenglu").css("display", "block");
                $(".laoding").css("display", "none");
                pwd.val("");
                pwd.focus();
            }
        });
    },
    logoutMember: function (toUrl) {
        var y = "https://sso.bidcenter.com.cn/logout";
        if (toUrl && toUrl != "")
            location.href = y + "?redirectURL=" + encodeURI(toUrl.replace(/&/g, '|'));
        else
            location.href = y + "?redirectURL=" + encodeURI(location.href.replace(/&/g, '|'));
        removeStorage();
    },
    login: function (APIKey, RUname, RUpwd, Back) {
        var y = "//sso.bidcenter.com.cn/";
        location.href = y + "validate?apk=" + APIKey + "&u=" + encodeURI(location.href.replace(/&/g, '|')) + "&RUname=" + RUname + "&RUpwd=" + RUpwd + "&b=" + (Back ? Back : 0);
        return false;
    }
};
function laoding() {
    window.location.href = window.location.href;
}

function removeStorage() {
    localStorage.removeItem("userdata");
}

