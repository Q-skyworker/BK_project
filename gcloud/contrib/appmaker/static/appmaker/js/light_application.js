(function ($) {

})(jQuery);

function on_load(iframe) {
    //iframe第一次加载时会报错，请忽略
    try{
        template.getListData();
    }catch(err){
        console.log(err)
    }
}

$('body').off('blur', '#username').on('blur', '#username', function () {
    if ($(this).val().trim().length == 0) {
        template.$data.notName = true;
        template.$data.moreUserName = false;
        template.$data.hasName = false;
        //$(this).focus();
    }
});

$('body').off('blur', '#username_modify').on('blur', '#username_modify', function () {
    if ($(this).val().trim().length == 0) {
        template.$data.change_not_name = true;
        template.$data.change_more_name = false;
        //$(this).focus();
    }
});

var template = new Vue({
    el: '#light-list',
    data: {
        ListData: [],
        people_data: [],
        get_category: [],
        u_name: '',
        desc_data: '',
        name_data: '',
        name: '',
        template_name: '',
        http_p: '',
        is_add: false,
        is_xiu: false,
        arrya: '',
        app_id: '',
        template_id: '',
        isHide: true,
        moreUserName: false,
        hasName: false,
        notName: false,
        change_more_name: false,
        change_not_name: false,
    },
    watch: {
        'u_name': function (val, oldval) {
            if (val.length > 20) {
                this.moreUserName = true;
                this.hasName = false;
                this.notName = false;
            } else {
                this.moreUserName = false;
                this.hasName = false;
                this.notName = false;
            }
            ;
            if (val.length == 0) {
                this.notName = true;
                this.moreUserName = false;
                this.hasName = false;
            }
        },
        'name_data': function (val, oldval) {
            if (val.trim().length > 20) {
                this.change_more_name = true;
                this.change_not_name = false;
            } else {
                this.change_more_name = false;
                this.change_not_name = false;
            }
            ;
            if (val.trim().length == 0) {
                this.change_not_name = true;
                this.change_more_name = false;
            }
        }
    },
    methods: {
        getListData: function () {
            var self = this;
            $.ajax({
                url: site_url + 'api/v3/appmaker/?business__cc_id=' + biz_cc_id,
                type: 'GET',
                dataType: 'json',
                success: function (req) {
                    self.ListData = req.objects;
                    // 控制前端提示信息是否展示
                    if (self.ListData.length != 0) {
                        self.isHide = true;
                    } else {
                        self.isHide = false;
                    }
                },
                error: function (response) {
                    console.log(response.responseText);
                }
            })
        },
        close: function () {
            var self = this;
            self.is_xiu = false;
            self.is_add = false;
            $(".col-sm-7 #e4").select2('val', '');
            //名称
            //self.template_id = template_id;
            $(".col-sm-7 #username").val("");
            //简介
            $(".form-group #introduction").val("");
            //选择文件
            $(".file-box").find("input[type='file']").val("");
            $(".form-group .name_text").hide();
            $(".form-group .name_20").hide();
            $(".form-group .name_30").hide();
        },
        edit_delete_icon: function (id) {
            //确认是否删除
            var self = this;
            self.app_id = id;
            var d = dialog({
                width: 440,
                height: 83,
                skin: 'min-bbb auto-center',
                title: gettext('操作确认'),
                content: '<div class="king-notice-box king-notice-warning"><p class="king-notice-text">' + gettext('确定要删除该轻应用吗？') + '</p></div>',
                onshow: function (arguments) {
                },
                okValue: gettext('确认'),
                ok: function () {
                    var delId = id;
                    $.ajax({
                        url: site_url + 'appmaker/del_app/' + biz_cc_id + '/',
                        data: {'app_id': delId},
                        type: 'POST',
                        dataType: 'json',
                        success: function (data) {
                            if (data.res) {
                                alert_msg(gettext("轻应用删除成功"), 2);
                                self.getListData();
                            } else {
                                alert_msg(data.msg, 4);
                            }
                        },
                        error: function (response) {
                            console.log(response.responseText);
                        }
                    });
                },
                cancelValue: gettext('取消'),
                cancel: function () {
                    // do something
                }
            });
            // d.show();
            d.showModal();
            //})
        },
        // 跳转到轻应用链接
        go_to_app: function (app_code, link) {
            Bk_api.open_other_app(app_code, link);
        },
        //增加轻应用弹窗
        add_box: function () {
            var self = this;
            self.is_add = true;
            $(".col-sm-7 #e4").select2('val', '');
            //名称
            //self.template_id = template_id;
            $(".col-sm-7 #username").val("");
            //简介
            $(".form-group #introduction").val("");
            //选择文件
            $(".file-box").find("input[type='file']").val("");
            $(".form-group .name_text").hide();
            $(".form-group .name_20").hide();
            $(".form-group .name_30").hide();
            $(".form-group .name_50").hide();
        },
        getUserData: function (obj) {  //转换下拉框数据结构
            this.get_category = obj.objects;
            var data = obj.objects;
            var Arry = [];
            var len = data.length;
            for (var i = 0; i < len; i++) {
                var a = {
                    id: data[i].id,
                    text: data[i].name
                };
                Arry.push(a);
            }
            ;
            return Arry;
        },
        //修改轻应用弹窗
        edit_delete_pencil: function (id) {
            var self = this;
            self.is_xiu = true;
            self.app_id = id;
            // $('#e5').select2()
            $(".form-group .name_text").hide();
            $(".form-group .name_20").hide();
            $(".form-group .name_30").hide();
            $(".form-group .name_50").hide();

            $.ajax({
                url: site_url + 'api/v3/appmaker/' + id + '/',
                type: 'GET',
                dataType: 'json',
                success: function (req) {
                    self.desc_data = req.desc;
                    self.name_data = req.name;
                    self.template_id = req.task_template_id;
                    self.template_name = req.task_template_name;
                    self.http_p = req.logo_url;
                    var a = self.http_p;
                    self.arrya = a.split('/').pop();
                    // select2 下拉选项多选

                },
                error: function (response) {
                    console.log(response.responseText);
                }
            })
        },
        //获取模板列表
        get_category_data: function () {
            var self = this;

            $("#e4").select2({
                data: null,
                ajax: {
                    url: site_url + 'api/v3/template/?business__cc_id=' + biz_cc_id,
                    dataType: 'json',
                    quietMillis: 250,
                    data: function (term) {
                        if(term){
                            return {
                                pipeline_template__name__contains: term    //搜索参数
                            };
                        }
                    },
                    results: function (data) {
                        return {
                            results: self.getUserData(data)  //搜索返回的数组
                        }
                    },
                    cache: true

                }
            }).on("change", function (e) {
                var a = $("#e4").val();
                for (var i = 0; i < self.get_category.length; i++) {
                    if (self.get_category[i].id == a) {
                        self.u_name = self.get_category[i].name.slice(0, 20);
                    }
                }
            });

        },
        // 保存新增轻应用
        save_people_data: function (event) {
            var self = this;
            var tar = $(event.target);
            tar.addClass('disabled');
            // 选择已有模板的数据id
            var template_id = $(".col-sm-7 #e4").select2("val");
            //名称
            var name_data = $(".col-sm-7 #username").val();
            //简介
            var description = $(".form-group #introduction").val();
            //选择文件
            var files = $(".file-box").find("input[type='file']").val();
            var img_url = $(".img-w img");
            var param = {
                "template_id": template_id,
                "app_name": name_data,
                "app_desc": description,
                "app_id": 0,
            };
            var data_validate = validate_app_data(param)
            if (data_validate) {
                $.ajax({
                    url: SITE_URL + 'appmaker/save_app/' + biz_cc_id + '/',
                    type: 'POST',
                    dataType: 'json',
                    data: param,
                    success: function (data) {
                        if (data.res) {
                            self.is_add = false;
                            var logo_data = data.data;
                            var logo_data_div = $('#div_m_logo');
                            $('[name=app_maker_code]', logo_data_div).val(logo_data.app_maker_code);
                            $('[name=operator]', logo_data_div).val(logo_data.operator);
                            $('[name=' + USER_UIN + ']', logo_data_div).val(logo_data.user_uin);
                            $('[name=' + USER_KEY + ']', logo_data_div).val(logo_data.user_key);
                            var logo = $('input[name=logo]', logo_data_div).val();

                            //图片存在，需要上传logo
                            if (logo && logo.substring(logo.lastIndexOf(".") + 1) == "png") {
                                tar.removeClass('disabled');
                                $('[name=form_logo]', logo_data_div).submit();
                            }
                            else {
                                tar.removeClass('disabled');
                                self.getListData();
                            }
                        }
                        else {
                            alert_msg(data.msg, 4);
                            tar.removeClass('disabled');
                        }
                    },
                    error: function (response) {
                        console.log(response.responseText);
                        tar.removeClass('disabled');
                    }
                });
            } else {
                tar.removeClass("disabled");
                return false;
            }
            // 点击完成操作,关闭弹出框
            //$("#add_light_bbox").hide();
            //self.is_add = false;
        },
        // 保存修改轻应用
        save_people_data_xiu: function (event) {
            var self = this;
            var tar = $(event.target);
            tar.addClass('disabled');
            //名称
            var name_data_xiu = $(".col-sm-7 #username_modify").val();
            //简介
            var description_xiu = $(".form-group #introduction_modify").val();
            var param = {
                "template_id": self.template_id,
                "app_name": name_data_xiu,
                "app_desc": description_xiu,
                "app_id": this.app_id,
            };
            var data_validate = validate_app_data(param);
            if (data_validate) {
                $.ajax({
                    url: SITE_URL + 'appmaker/save_app/' + biz_cc_id + '/',
                    type: 'POST',
                    dataType: 'json',
                    data: param,
                    success: function (data) {
                        if (data.res) {
                            self.is_xiu = false;
                            var logo_data = data.data;
                            var logo_data_div = $('#div_m_logo_edit');
                            $('[name=app_maker_code]', logo_data_div).val(logo_data.app_maker_code);
                            $('[name=operator]', logo_data_div).val(logo_data.operator);
                            $('[name=' + USER_UIN + ']', logo_data_div).val(logo_data.user_uin);
                            $('[name=' + USER_KEY + ']', logo_data_div).val(logo_data.user_key);
                            var logo = $('input[name=logo]', logo_data_div).val();
                            //图片存在，需要上传logo
                            if (logo && logo.substring(logo.lastIndexOf(".") + 1) == "png") {
                                tar.removeClass('disabled');
                                $('[name=form_logo]', logo_data_div).submit();
                            }
                            else {
                                tar.removeClass('disabled');
                                self.getListData();
                            }
                        } else {
                            alert_msg(data.msg, 4);
                            tar.removeClass("disabled");
                        }
                    },
                    error: function (response) {
                        console.log(response.responseText);
                        tar.removeClass('disabled');
                    }
                });
            } else {
                tar.removeClass("disabled");
                return false;
            }
        },
        quxiao: function () {
            var self = this;
            self.is_add = false;
            $(".col-sm-7 #e4").select2('val', '');
            //名称
            //self.template_id = template_id;
            $(".col-sm-7 #username").val("");
            //简介
            $(".form-group #introduction").val("");
            //选择文件
            $(".file-box").find("input[type='file']").val("");
        },
        quxiao_xiu: function () {
            var self = this;
            self.is_xiu = false;
        },
        showLoading: function () {
            if ($('#stand_loading').length > 0) {
                $('#stand_loading').show();
            } else {
                var loadingNode = $('<div id="stand_loading" class="stand_loading" style="padding:17px; position: fixed; background: rgba(245, 245, 245, 0.79);border-radius: 8px; top:50%; left:50%; margin-top:-40px; margin-left:-40px; z-index: 1000;"><img alt="loadding" src="' + STATIC_URL + 'images/loading_2_24x24.gif"></div>');
                loadingNode.appendTo($('body'));
            }
        },
        Cancle_hide: function () {
            $('#stand_loading').hide();
        }
        ,
        introduction_key_up: function (e) {
            $(e.target).val($(e.target).val().replace(/[<>~!@#$^&*￥]/g, ''));
        },
    },

    ready: function () {
        this.showLoading();
        this.getListData();
        this.get_category_data();
        this.Cancle_hide();
        // 这里不暂停一会会报Uncaught TypeError: Cannot read property 'appendChild' of null的错误
        function sleep(d) {
            for (var t = Date.now(); Date.now() - t <= d;);
        }

        sleep(500); //当前方法暂停5秒
    }
});

function validate_app_data(param) {

    var template_id = param['template_id']
    var app_name = param['app_name']
    if (!template_id) {
        $(".form-group .name_30").show();
        /*show_msg('请先选择关联的已有模板！',4);*/
        return false;
    }
    if (!app_name) {
        $(".form-group .name_text").show();
        $(".form-group .name_20").hide();
        $(".form-group .name_50").hide();
        /*show_msg('请填写APP名称！',4);*/
        return false;
    }
    if (app_name.length > 20) {
        /* show_msg('APP名称必须少于20个字符！',4);*/
        $(".form-group .name_20").show();
        $(".form-group .name_text").hide();
        $(".form-group .name_50").hide();
        return false;
    }
    var app_id = param['app_id']
    // 校验是否重名
    if (app_id == 0) {
        var app_name_already_exist = false;
        $.ajax({
            url: site_url + "api/v3/appmaker/?business__cc_id=" + BIZ_CC_ID,
            type: "GET",
            async: false,
            dataType: "JSON",
            complete: function (response) {
                if (response.status < 300 && response.status >= 200) {
                    var data = JSON.parse(response.responseText);
                    if (data.objects.filter(function (item) {
                            return item.name == app_name;
                        }).length) {
                        app_name_already_exist = true;
                    }
                } else {
                    console.error(e);
                }
            }
        });
        if (app_name_already_exist) {
            $(".form-group .name_50").show();
            $(".form-group .name_20").hide();
            $(".form-group .name_text").hide();
            template.$data.hasName = true;
            //show_msg("业务下已经有一个轻应用名为: " + app_name, 4);
            return false;
        }
    }
    var logo = $('input[name=logo]').val();
    if (logo && logo.substring(logo.lastIndexOf(".") + 1) != "png") {
        show_msg(gettext('上传图片须为png格式'), 4);
        return false;
    }
    return true;
}