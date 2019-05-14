(function(){
    var com = new Vue({
        el: '#header',
        data:{
            busi_data: [],
            biz_cc_name: BIZ_CC_NAME,
        },
        methods: {
            // 点击下拉
            select_biz: function(){
                //console.log("444");
                $("#busi_select").select2('open');
            },
            get_common_data: function(){
                var self = this;
                $.ajax({
                    url: site_url + 'get_authorized_biz_list/',
                    type: 'GET',
                    dataType: 'json',
                    // async: false,
                    success: function(req){
                        self.busi_data = req.data;
                        $("#busi_select").select2({
                            placeholder: gettext("请选择业务"),
                            allowClear: true,
                            data: self.busi_data
                        }).val(biz_cc_id).trigger("change")
                        .on('select2-open',function(){
                            $('.sear i.fa-sort-down').addClass('on');
                            $('.select2-drop-active').css({'border':'1px solid #ddd','box-shadow':'0px 3px 6px rgba(0,0,0,0.1)','-webkit-box-shadow':'0px 3px 6px rgba(0,0,0,0.1)'});
                        })
                        .on('select2-close',function(){
                            $('.sear i.fa-sort-down').removeClass('on');
                            // 选中下拉菜单时触发事件
                            var biz_id = $('#busi_select').val();      //被选中的id
                            //业务没有改变，直接返回
                            if(biz_id == biz_cc_id){
                                return false;
                            }
                            //后台更新当前用户的默认业务
                            $.ajax({
                                url: site_url + 'change_user_default_biz/' + biz_id + '/',
                                type: 'POST',
                                dataType: 'json',
                                success: function(req){ }
                            });
                            window.location.href = site_url + "business/home/" + biz_id +"/?hide_header=" + HIDE_HEADER;
                        })
                    }
                });
            }
        },
        ready: function(){
            this.get_common_data();
            $(".business-show").hide();
        }
    });
})(jQuery);


function show_msg(message, type){
   alert_msg(message, type);
}


function alert_msg(message, type){
    var info_list = [
        'info',
        'violet',
        'success',
        'warning',
        'error',
    ];
    var position = "toast-top-center";
    var time = 3000;
    if(type==4){
        time = 0;
    }
    var c_message = htmlspecialchars(message);
    toastr.remove();
    toastr[info_list[type]](c_message, '',{
        positionClass: position,
        showMethod: "slideDown",
        timeOut: time,
    });
}

/*
@summary: 按钮发送请求前统一处理为loading状态
 */
function button_pre_save(obj){
    var old_html = obj.html();
    obj.html('<i class="fa fa-spinner fa-spin"></i>').addClass('disabled');
    return old_html;
}

/*
@summary: 按钮发送请求成功或者失败返回后统一为原状态
 */
function button_after_save(obj, old_html){
    obj.html(old_html).removeClass('disabled');
    return true;
}


function mock_alert(msg){
    alert_msg(msg, 4);
}

window.alert = mock_alert;  // 替换系统默认弹框

function htmlspecialchars(str){

    var r_str = String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
    return String(r_str).replace(/&lt;br\/&gt;/g, "<br/>")

}

//禁止输入特殊字符
function TextValidate(){
    var code;
    var character;
    if (document.all)
    {
        code = window.event.keyCode; // 处理IE
    }
    else
    {
        code = arguments.callee.caller.arguments[0].which;
    }
    character = String.fromCharCode(code);

    var txt=new RegExp("[ ,\\`,\\~,\\!,\\@,\#,\\%,\\^,\\+,\\*,\\&,\\?,\\:,\\.,\\<,\\>,\\{,\\},\\(,\\),\\',\\;,\\=,\"]");
    if (txt.test(character))
    {
        if (document.all)
        {
            window.event.returnValue = false;
        }
        else
        {
            arguments.callee.caller.arguments[0].preventDefault();
        }
    }
}
