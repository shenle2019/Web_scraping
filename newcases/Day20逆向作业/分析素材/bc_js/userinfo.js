var cookieFn = {
    trim: function (str) {
        if (str.length > 0) {
            var isGoon = true;
            while (isGoon && str.indexOf(' ') == 0) {
                str = str.substr(1);
                isGoon = str.length > 0
            }
            isGoon = true;
            while (isGoon && str.lastIndexOf(' ') == (str.length - 1)) {
                str = str.substr(0, str.length - 1);
                isGoon = str.length > 0
            }
        }
        return str;
    },
    /*获取具体某一个cookie*/
    getCookieObject: function () {
        var currCookie = document.cookie;
        var listObj = [];
        var arry = [];
        if (currCookie) {
            arry = currCookie.split(';');
            for (var i = 0; i < arry.length; i++) {
                var arry2 = arry[i].split('&');
                if (arry2 && arry2.length > 0) {
                    var obj = {};
                    var arry_first = arry2[0].split('=');
                    if (arry_first.length == 3) {
                        obj[cookieFn.trim(arry_first[1])] = arry_first[2];
                        if (arry2.length > 1) {
                            for (var j = 1; j < arry2.length; j++) {
                                var arr3 = arry2[j].split('=');
                                if (arr3.length == 2) {
                                    obj[cookieFn.trim(arr3[0])] = arr3[1];
                                }
                            }
                        }
                        if (obj) {
                            var objSanji = {};
                            objSanji[cookieFn.trim(arry_first[0])] = obj;
                            listObj.push(objSanji);
                        }
                    } else if (arry_first.length == 2) {
                        for (var j = 0; j < arry2.length; j++) {
                            var arr3 = arry2[j].split('=');
                            if (arr3.length == 2) {
                                obj[cookieFn.trim(arr3[0])] = arr3[1];
                            }
                        }
                        if (obj) {
                            listObj.push(obj);
                        }
                    }

                }
            }
            return listObj;
        }
    },
    /*获取具体某一个cookie*/
    getCookieValue: function (key1, key2) {
        var cookieList = cookieFn.getCookieObject();
        for (var i = 0; i < cookieList.length; i++) {
            if (cookieList && typeof (cookieList[i]) == "object" && cookieList[i][key1]) {
                if (key2)
                    return cookieList[i][key1][key2];
                else
                    return cookieList[i][key1];
            }
        }
        return "";
    },
    /*获取url参数*/
    getUrlParams: function (name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
        var r = decodeURI(window.location.search).substr(1).match(reg);  //匹配目标参数
        if (r != null)
            return unescape(r[2]);

        return ""; //返回参数值
    }
}

var aspcn = cookieFn.getCookieValue("aspcn");
var userinfo = new Object();;
var islogin = false;
var username = "";
var permission = 1;
var permissionStr = "";
var diqu = "";
var jibie = "";//会员级别（包含地区）
if (aspcn != undefined && aspcn != '') {

    userinfo.name = cookieFn.getCookieValue("aspcn", "name");
    userinfo.vip = cookieFn.getCookieValue("aspcn", "vip");
    userinfo.id = cookieFn.getCookieValue("aspcn", "id");
    userinfo.diqu = cookieFn.getCookieValue("aspcn", "diqu");

    if (userinfo && userinfo.id && userinfo.id != '') {
        islogin = true;
        username = userinfo.name;
        permission = parseInt(userinfo.vip);
        diqu = userinfo.diqu;
        switch (permission) {
            case 2:
                permissionStr = "标准会员";
                break;
            case 3:
                permissionStr = "高级会员";
                break;
            case 4:
                permissionStr = "VIP会员";
                break;
            case 6:
                permissionStr = "金牌会员";
                break;
            case 7:
                permissionStr = "银牌会员";
                break;
            case 9:
                permissionStr = "投标通会员";
                break;
            case 30:
                permissionStr = "标准子账号";
                break;
            case 31:
                permissionStr = "高级子账号";
                break;
            case 32:
                permissionStr = "VIP子账号";
                break;
            case 35:
                permissionStr = "项目通会员";
                break;
            default:
                permissionStr = "免费会员";
                break;
        }
        jibie = $.inArray(permission, [2, 3, 30, 31]) > -1 ? diqu + permissionStr : permissionStr;
    }
}
function getcookie(c) {
    var a = document.cookie.indexOf(c), b = document.cookie.indexOf(";", a);
    return (a == -1 ? "" : decodeURIComponent(document.cookie.substring(a + c.length + 1, b > a ? b : document.cookie.length))).replace(";", "")
}
