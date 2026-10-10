(function ($) {
    var bigAutocomplete = new function () {
        this.currentInputText = null;//目前获得光标的输入框（解决一个页面多个输入框绑定自动补全功能）
        this.functionalKeyArray = [9, 20, 13, 16, 17, 18, 91, 92, 93, 45, 36, 33, 34, 35, 37, 39, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 144, 19, 145, 40, 38, 27];//键盘上功能键键值数组
        this.holdText = null;//输入框中原始输入的内容
        this.searchBox = [];

        //初始化插入自动补全div，并在document注册mousedown，点击非div区域隐藏div
        this.init = function () {
            bigAutocomplete.searchBox.append("<div id='bigAutocompleteContent' class='bigautocomplete-layout'></div>");
            $(document).bind('mousedown', function (event) {
                var $target = $(event.target);
                if ((!($target.parents().andSelf().is('#bigAutocompleteContent'))) && (!$target.is(bigAutocomplete.currentInputText))) {
                    bigAutocomplete.hideAutocomplete();
                }
            })

            //鼠标悬停时选中当前行
            $("#bigAutocompleteContent").delegate("tr", "mouseover", function () {
                $("#bigAutocompleteContent tr").removeClass("ct");
                $(this).addClass("ct");
            }).delegate("tr", "mouseout", function () {
                $("#bigAutocompleteContent tr").removeClass("ct");
            });


            //单击选中行后，选中行内容设置到输入框中，并执行callback函数
            $("#bigAutocompleteContent").delegate("tr", "click", function () {
                bigAutocomplete.currentInputText.val($(this).find("div:last").attr("data-title"));
                var callback_ = bigAutocomplete.currentInputText.data("config").callback;
                if ($("#bigAutocompleteContent").css("display") != "none" && callback_ && $.isFunction(callback_)) {
                    callback_($(this).data("jsonData"));

                }
                bigAutocomplete.hideAutocomplete();
            })

        }

        this.autocomplete = function (param) {
            switch ($.fn.SearchInput) {
                case "jq_search_keyword":
                    bigAutocomplete.searchBox = $(".search_input1");
                    break;
                case "jq_search_keyword2":
                    bigAutocomplete.searchBox = $(".search_input2");
                    break;
                default:
                    bigAutocomplete.searchBox = $("body");
                    break;
            }
            if (bigAutocomplete.searchBox.length > 0 && $("#bigAutocompleteContent").length <= 0) {
                bigAutocomplete.init();//初始化信息
            }

            var $this = $(this);//为绑定自动补全功能的输入框jquery对象

            var $bigAutocompleteContent = $("#bigAutocompleteContent");

            this.config = {
                //width:下拉框的宽度，默认使用输入框宽度
                width: $this.outerWidth() - 2,
                //url：格式url:""用来ajax后台获取数据，返回的数据格式为data参数一样
                url: null,
                /*data：格式{data:[{title:null,result:{}},{title:null,result:{}}]}
                url和data参数只有一个生效，data优先*/
                data: null,
                //callback：选中行后按回车或单击时回调的函数
                callback: null
            };
            $.extend(this.config, param);

            $this.data("config", this.config);

            //输入框keydown事件
            $this.keydown(function (event) {
                switch (event.keyCode) {
                    case 40://向下键

                        if ($bigAutocompleteContent.css("display") == "none") return;

                        var $nextSiblingTr = $bigAutocompleteContent.find(".ct");
                        if ($nextSiblingTr.length <= 0) {//没有选中行时，选中第一行
                            $nextSiblingTr = $bigAutocompleteContent.find("tr:first");
                        } else {
                            $nextSiblingTr = $nextSiblingTr.next();
                        }
                        $bigAutocompleteContent.find("tr").removeClass("ct");

                        if ($nextSiblingTr.length > 0) {//有下一行时（不是最后一行）
                            $nextSiblingTr.addClass("ct");//选中的行加背景
                            $this.val($nextSiblingTr.find("div:last").attr("data-title"));//选中行内容设置到输入框中

                            //div滚动到选中的行,jquery-1.6.1 $nextSiblingTr.offset().top 有bug，数值有问题
                            $bigAutocompleteContent.scrollTop($nextSiblingTr[0].offsetTop - $bigAutocompleteContent.height() + $nextSiblingTr.height());

                        } else {
                            $this.val(bigAutocomplete.holdText);//输入框显示用户原始输入的值
                        }


                        break;
                    case 38://向上键
                        if ($bigAutocompleteContent.css("display") == "none") return;

                        var $previousSiblingTr = $bigAutocompleteContent.find(".ct");
                        if ($previousSiblingTr.length <= 0) {//没有选中行时，选中最后一行行
                            $previousSiblingTr = $bigAutocompleteContent.find("tr:last");
                        } else {
                            $previousSiblingTr = $previousSiblingTr.prev();
                        }
                        $bigAutocompleteContent.find("tr").removeClass("ct");

                        if ($previousSiblingTr.length > 0) {//有上一行时（不是第一行）
                            $previousSiblingTr.addClass("ct");//选中的行加背景
                            $this.val($previousSiblingTr.find("div:last").attr("data-title"));//选中行内容设置到输入框中

                            //div滚动到选中的行,jquery-1.6.1 $$previousSiblingTr.offset().top 有bug，数值有问题
                            $bigAutocompleteContent.scrollTop($previousSiblingTr[0].offsetTop - $bigAutocompleteContent.height() + $previousSiblingTr.height());
                        } else {
                            $this.val(bigAutocomplete.holdText);//输入框显示用户原始输入的值
                        }

                        break;
                    case 27://ESC键隐藏下拉框

                        bigAutocomplete.hideAutocomplete();
                        break;
                }
            });

            //粘贴事件
            var doc = document.getElementById($.fn.SearchInput);
            //返回数据来源 0：Interfacce 1:Internal
            var resultSource = 0;
            doc.addEventListener('paste', function (e) {

                if (!(e.clipboardData && e.clipboardData.items)) {
                    return;
                } else {
                    for (var i = 0, len = e.clipboardData.items.length; i < len; i++) {
                        var item = e.clipboardData.items[i];
                        if (item.kind === "string") {
                            item.getAsString(function (str) {
                                loadDdl();
                            })
                        }
                    }
                }
            });
            //输入框keyup事件
            $this.keyup(function (event) {
                var k = event.keyCode;
                var ctrl = event.ctrlKey;
                var isFunctionalKey = false;//按下的键是否是功能键
                for (var i = 0; i < bigAutocomplete.functionalKeyArray.length; i++) {
                    if (k == bigAutocomplete.functionalKeyArray[i]) {
                        isFunctionalKey = true;
                        break;
                    }
                }
                //k键值不是功能键或是ctrl+c、ctrl+x时才触发自动补全功能
                if (!isFunctionalKey && (!ctrl || (ctrl && k == 67) || (ctrl && k == 88))) {
                    loadDdl();
                }
                //回车键
                if (k == 13) {
                    //var callback_ = $this.data("config").callback;
                    if ($bigAutocompleteContent.css("display") != "none") {
                        //if (callback_ && $.isFunction(callback_)) {
                        //    callback_($bigAutocompleteContent.find(".ct").data("jsonData"));
                        //}
                        $bigAutocompleteContent.hide();
                    }
                }
            });
            //输入框focus事件
            $this.focus(function () {
                bigAutocomplete.currentInputText = $this;
                loadDdl();
            });

            //加载下拉数据
            function loadDdl() {
                var config = $this.data("config");
                var offset = $this.offset();
                $bigAutocompleteContent.width(config.width);
                var h = $this.outerHeight() - 1;
                $bigAutocompleteContent.css({ 'top': offset.top + h });
                switch ($.fn.SearchInput) {
                    case "jq_search_keyword":
                        $(".search_input1").append($bigAutocompleteContent);
                        $bigAutocompleteContent.css('cssText', 'top:' + (offset.top + h) + 'px !important;left: initial;');
                        break;
                    case "jq_search_keyword2":
                        $(".search_input2").append($bigAutocompleteContent);
                        $bigAutocompleteContent.css('cssText', 'position: fixed !important;top:60px !important;left: initial;');
                        break;
                    default:
                        $("body").append($bigAutocompleteContent);
                        $bigAutocompleteContent.css('cssText', 'top:' + (offset.top + h) + 'px !important;left: ' + offset.left + 'px !important;');
                        break;
                }
                var data = config.data;
                var url = "";
                var params = {};
                var currVal = $.trim($("#" + $.fn.SearchInput).val());
                var keyword_ = currVal;
                if (keyword_ == null || keyword_ == "") {
                    bigAutocomplete.hideAutocomplete();
                    return;
                }
                if ((keyword_.length >= 5 && companyName(keyword_)) || ($.fn.SearchTag && $.fn.SearchTag == 1))
                    resultSource = 1;
                else
                    resultSource = 0;
                url = config.url[resultSource];
                params = config.params[resultSource];
                if (data != null && $.isArray(data)) {
                    var data_ = new Array();
                    for (var i = 0; i < data.length; i++) {
                        var originalT = data[i];
                        if (resultSource == 0)
                            originalT = data[i].title;
                        if (originalT.indexOf(keyword_) > -1) {
                            data_.push(originalT);
                        }
                    }
                    makeContAndShow(data_);
                    var regString = /[a-zA-Z]+/;
                } else if (url != null && url != "" && (keyword_.length >= 3 || (keyword_.match(/^[\u4E00-\u9FA5]{1,}$/) && keyword_.length >= 2)) && (keyword_.match(/^[A-Za-z]+$/) || keyword_.match(/^[\u4E00-\u9FA5]{1,}$/))) {
                    params.keyword = keyword_;
                    $.post(url, params, function (result) {
                        if (!result.ret)
                            $bigAutocompleteContent.hide();
                        else
                            makeContAndShow(result.other2, keyword_)
                    }, "json")
                }
                bigAutocomplete.holdText = currVal;
            }

            //判断公司名称是否是全名
            function companyName(s) {
                var str_key = "办事处,公司,小学,中学,学校,中心,局,银行,分行,社,总队,处,电站,院,酒店,矿,政府,所,部,协会,厂,场,集团,馆,行,会,署,网";
                var key = str_key.split(",");
                var r = 0;
                for (var i = 0; i < str_key.length; i++) {
                    if (s.indexOf(key[i]) > -1) {
                        return true;
                    }
                }
                return false;
            }
            //组装下拉框html内容并显示
            function makeContAndShow(data_, key) {
                if (resultSource == 0)
                    data_ = data_.data;
                if (data_ == null || data_.length <= 0) {
                    return;
                }

                var cont = [];
                cont.push("<table><tbody>");
                for (var i = 0; i < data_.length; i++) {
                    var originalT = data_[i];
                    if (resultSource == 0)
                        originalT = data_[i].title;
                    var showT = originalT;
                    for (var c in key) {
                        showT = showT.replace(new RegExp(key[c], "gm"), "<b>" + key[c] + "</b>");
                    }
                    cont.push("<tr><td><div data-title='" + originalT + "' >" + showT + "</div></td></tr>")
                }

                cont.push("</tbody></table>");
                $bigAutocompleteContent.html(cont);
                $bigAutocompleteContent.show();

                //每行tr绑定数据，返回给回调函数
                $bigAutocompleteContent.find("tr").each(function (index) {
                    var rdata = data_[index];
                    if (resultSource == 0)
                        rdata = data_[index].title;
                    $(this).data("jsonData", rdata);
                })
            }
        }
        //隐藏下拉框
        this.hideAutocomplete = function () {
            var $bigAutocompleteContent = $("#bigAutocompleteContent");
            if ($bigAutocompleteContent.css("display") != "none") {
                $bigAutocompleteContent.find("tr").removeClass("ct");
                $bigAutocompleteContent.hide();
            }
        }
    };
    $.fn.bigAutocomplete = bigAutocomplete.autocomplete;

})(jQuery)