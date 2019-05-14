(function(){
    var vm = new Vue({
        el: '#config_home',
        data:{
            biz_cc_id: BIZ_CC_ID,
            executor: executor,
        },
        methods: {
            set_biz_executor: function(e){
                e.preventDefault();
                $(e.target).addClass('disabled');
                var self = this;
                $.ajax({
                    url: site_url + 'config/api/biz_executor/' + self.biz_cc_id + '/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        'executor': self.executor,
                    },
                    success: function(response){
                        if(response.result){
                            show_msg(gettext("保存成功"), 2);
                        }else{
                            show_msg(response.message, 4);
                        }
                        $(e.target).removeClass('disabled');
                    }
                });
            }
        },
        ready: function(){
        }
    });
})(jQuery);
