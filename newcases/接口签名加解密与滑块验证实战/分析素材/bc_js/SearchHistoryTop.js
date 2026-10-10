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

function getlink() {
    switch (currTag) {
        case 0:
            return "https://search.bidcenter.com.cn/search?keywords=";
        case 1:
            return "https://www.bidcenter.com.cn/xiangmu?keywords=";
        case 2:
            return "https://user.bidcenter.com.cn/v2023/#/saasApply/qiqing-search?keywords=";
        case 3:
            return "https://shuju.bidcenter.com.cn/shuju/search-key.html?key=";
        case 4:
            return "https://credit.bidcenter.com.cn/credit/search.aspx?type=1&key=";
        case 5:
            return "https://user.bidcenter.com.cn/v2023/#/hetongshangji/index?kwd=";
    }
    return "https://search.bidcenter.com.cn/search?keywords=";
}

//热搜数据展示--关键词框1
$(".searchInput").focus(function () {
    if (currTag == 4 || currTag == 5) return;
    searchInputFocus("searchPop");
}).blur(function () {
    hideSearchLog();
});

//热搜数据展示--关键词框2
$(".searchInput1").focus(function () {
    if (currTag == 4 || currTag == 5) return;
    searchInputFocus("searchPop1");
}).blur(function () {
    hideSearchLog1();
});

function searchInputFocus(inputparent) {
    var searchkeyoword = "";

    if (inputparent == "searchPop")
        searchkeyoword = $(".searchInput").val();
    else
        searchkeyoword = $(".searchInput1").val();

    if (newsearch == 1 && searchkeyoword.length == 0) {
        $("#searchPop,#searchPop1").hide();
        return;
    }

    resouShow(inputparent, searchkeyoword);
    //关键词填充
    bidAutocomplete(inputparent, searchkeyoword);
}

$("#searchPop,#searchPop1").on("mouseenter", "li", function () {
    $(".searchPopWrap li").removeClass('active');
    $(this).addClass('active');
});

var isAllowHide = true;
//当在弹出上时
$("#searchPop,#searchPop1").mouseenter(function () {
    isAllowHide = false;
});
//当离开弹出上时
$("#searchPop,#searchPop1").mouseleave(function () {
    isAllowHide = true;
});

//自动匹配搜索关键词内容--关键词框1
$(".searchInput").keyup(function (event) {
    if (currTag == 4 || currTag == 5) return;
    searchInputFocus("searchPop");
});

//自动匹配搜索关键词内容--关键词框2
$(".searchInput1").keyup(function (event) {
    if (currTag == 4 || currTag == 5) return;
    searchInputFocus("searchPop1");
});

//隐藏记录列表--关键词框1
function hideSearchLog() {
    setTimeout(function () {
        if (isAllowHide)
            $("#searchPop").hide();
        else {
            if (!$(".searchInput").is(":focus"))
                $(".searchInput").focus();
        }
    }, 200);
}

//隐藏记录列表--关键词框2
function hideSearchLog1() {
    setTimeout(function () {
        if (isAllowHide)
            $("#searchPop1").hide();
        else {
            if (!$(".searchInput1").is(":focus"))
                $(".searchInput1").focus();
        }
    }, 200);
}

//填充词
function bidAutocomplete(inputparent, searchkeyoword) {
    if (searchkeyoword.length > 1) {
        var k = event.keyCode;
        var ctrl = event.ctrlKey;
        //k键值不是功能键或是ctrl+c、ctrl+x时才触发自动补全功能
        if (!ctrl || (ctrl && k == 67) || (ctrl && k == 88)) {
            var url = "https://interface.bidcenter.com.cn/zhaobiao/SearchAutoCompleteKwdsHandler.ashx?from=6137&location=6138&guid=" + new Date().getTime();
            var param = { keyword: searchkeyoword };
            if (currTag == 2) {
                url = "https://interface.bidcenter.com.cn/shuju/fenxi/company/SearchCompanyAutoCompleteHandler.ashx?from=6137&location=6138&guid=" + new Date().getTime();
                param = {
                    company: searchkeyoword,
                    pagesize: 10,
                    lytype: 3
                };
            }
            $("#" + inputparent + " .searchPopWrap .search-left").html("");
            $.post(url, param, function (result) {
                if (!result.ret) {
                    if (searchkeyoword.substring(0, 3) == '请输入')
                        historyShow(inputparent);
                    else
                        $("#" + inputparent + " .searchPopWrap .search-left").html("<ul><li title='" + searchkeyoword + "' onclick='runlink(getlink(),\"" + searchkeyoword + "\")'>" + searchkeyoword + "</li></ul>");
                }
                else {
                    var data_ = result.other2.data;
                    if (currTag == 2)
                        data_ = result.other2.remenlist;

                    if (data_ != null && data_.length > 0) {
                        var str_html = [];
                        str_html.push("<ul>");
                        for (var i = 0; i < data_.length; i++) {
                            var originalT = data_[i].title;
                            var showT = originalT;
                            for (var c in searchkeyoword) {
                                showT = showT.replace(new RegExp(searchkeyoword[c], "gm"), "<b>" + searchkeyoword[c] + "</b>");
                            }
                            str_html.push("<li title='" + originalT + "' onclick='runlink(getlink(),\"" + originalT + "\")'>" + showT + "</li>")
                        }
                        str_html.push("</ul>");
                        $("#" + inputparent + " .searchPopWrap .search-left").html(str_html.join(''));
                    }
                }
            }, "json")
        }
        $("#" + inputparent).show();
    }
    else
        historyShow(inputparent)
}

//显示历史记录
function historyShow(inputparent) {
    $("#" + inputparent + " .searchPopWrap .search-left").html("");
    //从本地缓存中获取关键词
    var history = [];
    if (currTag == 2)
        history = localStorage["comhistroylist"] ? eval(localStorage["comhistroylist"]) : [];
    else
        history = localStorage["histroylist"] ? eval(localStorage["histroylist"]) : [];

    var history_html = [];
    if (history && history != null && history.length > 0) {
        if (removelishisousuo != 1)
            history_html.push("<h3><span style='float:left;'>历史搜索</span><span style='float:right;margin-right:10px;' onclick='clearlocalStorage(\"histroylist\")'>清空</span></h3>");

        history_html.push("<div style='clear:both;'></div><ul>");
        for (var i = 0; i < history.length; i++) {
            history_html.push("<li title='" + history[i] + "' onclick='runlink(getlink(),\"" + history[i] + "\")'>" + history[i] + "</li>");
        }
        history_html.push("</ul>");
    }
    else
        history_html.push("<div class='empty'><img src='https://img.bidcenter.com.cn/www/images/null.png' />无搜索历史，赶紧搜索吧~</div>");
    $("#" + inputparent + " .searchPopWrap .search-left").html(history_html.join(''));
}

//显示热搜或者推荐关键词
function resouShow(inputparent, searchkeyoword) {
    var token = cookieFn.getCookieValue("aspcn", "Token");
    $.ajax({
        type: "POST", //用POST方式传输
        data: { from: 6150, location: 1111, token: token, tag: currTag, keyword: searchkeyoword },
        url: "https://interface.bidcenter.com.cn/search/GetSearchTopHandler.ashx?guid=" + new Date().getTime(), //目标地址 
        dataType: "json",
        success: function (data) {
            if (data) {
                //转json
                if (data != undefined && data.ret) {
                    var str_html = [];
                    if (data.retbs == 1)
                        str_html.push("<h3>热门搜索</h3>");
                    else
                        str_html.push("<h3>猜你想搜</h3>");
                    if (data.other2 && data.other2.remenlist && data.other2.remenlist.length > 0) {
                        var r_list = data.other2.remenlist;
                        str_html.push("<ul>");
                        for (var i = 0; i < r_list.length; i++) {
                            if (i < 3) {
                                switch (i) {
                                    case 0:
                                        str_html.push("<li title='" + r_list[i] + "' onclick='runlink(getlink(),\"" + r_list[i] + "\")'><span class='one xuhao'>1</span>" + r_list[i] + "</li>");
                                        break;
                                    case 1:
                                        str_html.push("<li title='" + r_list[i] + "' onclick='runlink(getlink(),\"" + r_list[i] + "\")'><span class='two xuhao'>2</span>" + r_list[i] + "</li>");
                                        break;
                                    case 2:
                                        str_html.push("<li title='" + r_list[i] + "' onclick='runlink(getlink(),\"" + r_list[i] + "\")'><span class='three xuhao'>3</span>" + r_list[i] + "</li>");
                                        break;
                                }
                            }
                            else
                                str_html.push("<li title='" + r_list[i] + "' onclick='runlink(getlink(),\"" + r_list[i] + "\")'><span class='xuhao'>" + (i + 1) + "</span>" + r_list[i] + "</li>");
                        }
                        str_html.push("</ul>");
                    }
                    else
                        str_html.push("<div class='empty'><img src='https://img.bidcenter.com.cn/www/images/null.png' />无热门搜索，赶紧搜索吧~</div>");
                    $("#" + inputparent + " .search-right").html(str_html.join(''));
                    $("#" + inputparent).show();
                }
                else {
                    $("#" + inputparent).hide();
                }
            }
            else
                $("#" + inputparent).hide();
        },
        error: function (e) {
            $("#" + inputparent).hide();
        }
    })
}

//跳转，并且记录localStorage
function runlink(link, value) {
    addlocalStorage(value);
    window.open(link + value, "_blank");
}

//清空指定的本地缓存
function clearlocalStorage() {
    var key = "histroylist";
    if (currTag == 2)
        key = "comhistroylist";

    localStorage.removeItem(key);
    layer.msg("清除成功");
}

//存储localStorage
function addlocalStorage(value) {
    var key = "histroylist";
    if (currTag == 2)
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