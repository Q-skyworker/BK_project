(function($) {
    // 导航线条
    var power_id;       //获取的数据源id
    var power_biz;      //获取的数据源id
    var power_name_id;  //可选择的人员
    var power_name_biz; //可执行的人员
    //表格(DataTables) start
    var language = {
        search: '',
        processing: gettext('加载中'),
        lengthMenu: gettext("每页显示 _MENU_ 记录"),
        zeroRecords: gettext("没找到相应的数据！"),
        info: gettext("共 _TOTAL_ 条记录，当前第 _PAGE_ / _PAGES_"),
        infoEmpty: gettext("暂无数据！"),
        infoFiltered: gettext("(从 _MAX_ 条数据中搜索)"),
        paginate: {
            first: gettext('首页'),
            last: gettext('尾页'),
            previous: gettext('上一页'),
            next: gettext('下一页'),
        }
    };
    var datasource_api = SITE_URL +  "api/v3/template/?business__cc_id="+ BIZ_CC_ID;
    $("#template_datatables").dataTable({
        autoWidth: false,
        //processing:false,
        lengthChange: false, //是否允许用户改变表格每页显示的记录数
        pageLength: 10, //每页显示几条数据
        lengthMenu: [5, 10, 20], //每页显示选项
        pagingType: 'full_numbers',
        processing: true,
        serverSide: true,
        current_draw: undefined,
        ajax: function(data, callback, oSettings){
            var that = this;
            var params = {
                limit: data.length,
                offset: data.start
            };
            // 关键字过滤
            if(data.search.value){
                params['q'] = data.search.value;
            }
            $.ajax({
                type: "GET",
                url: datasource_api,
                dataType: "JSON",
                data: params,
                success: function(response){
                    if(that.current_draw == undefined){
                       that.current_draw = data.draw;
                    }
                    var json = {
                        data: response.objects,
                        recordsTotal: response.meta.total_count,
                        draw: that.current_draw++,
                        //recordsFiltered: data.length,
                        recordsFiltered: response.meta.total_count,
                    }
                    callback(json);
                },
                error: function(response){
                    console.log(response.responseText);
                }
            });
        },
        ordering: false,
        columns: [{
            data: "id"
        }, {
            data: null,
            render:function (data){
                return '<a class="work-bre" title="' + htmlspecialchars(data.name) + '" href="' + site_url + 'template/edit/' + biz_cc_id+ '/?template_id=' + data.template_id + '">'+ htmlspecialchars(data.name) + '</a>';
            }
        },
            {
                data: "category_name"
            },{
            data: "edit_time"
        }, {
            data: "creator_name"
        },

            {
            data: null,
            orderable: false,
            render: function(data, type, row, meta) {
                var guide_name = '';
                if(meta['row'] == 0){
                    guide_name = "create-task-guide"
                }
                return '<div class="elastic1">' +
                    '<a class="king-btn king-info w-auto mr5 '+ guide_name + '" href="'+site_url+'template/newtask/'+biz_cc_id+'/selectnode/?template_id='+data.id+'">' + gettext('新建任务') + '</a>' +
                    '<a class="king-btn king-warning w-auto mr5" href="' + site_url + 'template/edit/' + biz_cc_id+ '/?template_id=' + data.template_id + '">' + gettext('编辑') + '</a>' +
                    '<a class="king-btn king-default w-auto mr5" href="'+ site_url + 'template/clone/' + biz_cc_id+ '/?template_id=' + data.template_id + '">' + gettext('克隆') + '</a>' +
                    '<a  class="king-btn king-default w-auto mr5 elastic"' + 'data-id="' + data.id + '" buz_id = "' + biz_cc_id + '" >' + gettext('权限管理') + '</a>' +
                    '<a  class="king-btn king-danger w-auto mr5 del">' + gettext('删除') + '</a>' +
                    '<a  class="king-btn king-default w-auto to-taskflow" href="' + site_url + 'taskflow/home/' + biz_cc_id + '/?template_id=' + data.id + '">' + gettext('执行历史') + '</a>' +
                    '</div> ';
            }
        }],
        language: language
    }).on('draw.dt', function() {
        $("#template_datatables_filter").parent().addClass('filter-myStyle').siblings('.col-sm-6').addClass('length-myStyle');
        $("#template_datatables_filter input").attr('placeholder', gettext('请输入ID或者流程名称'));
        $('.power-manage-btn').click(function() {
            $('#temp_power_manage').modal('show');
            $('.power-manage-ok').click(function(event) {
                $('#temp_power_manage').modal('hide');
            });
        })
    })
    // 权限管理弹窗
    $("#template_datatables").on('click', 'a.elastic', function(){
        var self = this;
        // $(".elastic-box").show();
        power_id = $(this).attr('data-id');
        power_biz = $(this).attr('buz_id');
        power_name_id = [];
        power_name_biz = [];
        $.when(
            $.ajax({
                url: SITE_URL + 'get_biz_person_list/' + BIZ_CC_ID + '/?original=tasktmpl_list',
                type: 'GET',
                dataType: 'json'
            }),
            $.ajax({
                url: SITE_URL + 'template/api/get_perms/' + power_biz + '/',
                type: 'GET',
                data: {'template_id': power_id},
                dataType: 'json'
            })
        ).done(function(fullList, selectedList){
            vm.$data.people_data = fullList[0].data;
            vm.$nextTick(function(){
                fill_name_into_input(selectedList[0].data.fill_params_groups, '#e2')
                fill_name_into_input(selectedList[0].data.execute_task_groups, '#e3')
                $(".elastic-box").addClass('onShow');
            })
        })
    })

    function fill_name_into_input(data, selectEl){
        var len = data && data.length;
        if( len > 0 ){
            var nameList = [];
            for(var i=0; i<len; i++){
                nameList.push(data[i].show_name)
            };
            $(selectEl).select2().val(nameList).trigger("change");
        }else{
            $(selectEl).select2("val","");
            $(selectEl).select2({
                placeholder: gettext("请选择人员")
            })
        };
    }

    var t = $("#template_datatables").DataTable(); //获取datatables对象
    //删除按钮绑定事件
    $("#template_datatables tbody").on('click', 'a.del', function() {
        var $this = $(this)
        var row = t.row($(this).parents('tr')), //获取按钮所在的行
            data = row.data();
        var delId = data.id;
        var delDialog = dialog({
            width: 300,
            title: gettext('提示'),
            content: '<p style="font-size: 16px;text-align: center;">'+ gettext('您确定要删除该流程吗？') +'</p>',
            ok: function () {
                $.ajax({
                    url: site_url + 'api/v3/template/'+ delId + '/ ',
                    type: 'DELETE',
                    dataType: 'default',
                    success: function() {
                        show_msg(gettext('删除流程成功'), 2);
                        row.remove().draw();
                    },
                    error: function(response){
                        show_msg(gettext('删除流程失败'), 4);
                    }
                });
            },
            okValue: gettext('确定'),
            cancel: function () {},
            cancelValue: gettext('取消')
        }).showModal()
        return
        
    });


    //表格(DataTables) end
    $(".btn-tow").find(".qx").click(function(){
        $(".elastic-box").removeClass('onShow');
    });
    //数据源请求
    var vm = new Vue({
        el: '#model-list',
        data:{
            people_data:[],      //数据源
            is_close: false
        },
        methods:{
            // 关闭弹窗
            powe_close: function(){
                var self = this;
                this.is_close = false;
                $(".elastic-box").removeClass('onShow');
            },
            // 保存权限管理
            save_power: function(){
                // 可填信息的人的数据id
                var info_data = $("#plugin3_demo4 .select2_box").select2("val");
                // 可执行人的数据id
                var exec_data = $("#plugin3_demo5 .select2_box").select2('val');
               // debugger
                $.ajax({
                    url: SITE_URL + 'template/api/save_perms/' + power_biz + '/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        'template_id': power_id,
                        "fill_params": JSON.stringify(info_data),
                        "execute_task": JSON.stringify(exec_data)
                    },
                    success: function(req){
                        show_msg(gettext("保存成功"), 2);
                    },
                    error: function(response){
                        console.log(response.responseText);
                    }
                });
                // 点击完成操作,关闭弹出框
                $(".elastic-box").removeClass('onShow');
            },
            get_people_data: function(){ //权限管理数据源
                var self = this;
                $.ajax({
                    url: SITE_URL + 'get_biz_person_list/' + BIZ_CC_ID + '/?original=tasktmpl_list',
                    type: 'GET',
                    dataType: 'json',
                    success: function(req){
                        self.people_data = req.data;
                        var list = self.people_data;
                            // select2 下拉选项多选
                            $("#e2").select2({
                                placeholder: gettext("请选择人员"),
                                allowClear: true,
                                maximumSelectionSize: 7
                            });
                            // select2 下拉选项多选
                            $("#e3").select2({
                                placeholder: gettext("请选择人员"),
                                allowClear: true,
                                maximumSelectionSize: 7
                            });
                    },
                    error: function(response){
                        console.log(response.responseText);
                    }
                })
            }
        },
        // ready:function(){
        //     this.get_people_data();
        // }
    });
})(jQuery);
