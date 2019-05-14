$(function() {
    "use strict"

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

    var datasource_api = SITE_URL + "api/v3/taskflow/";
    var columns = [
        {
            data: "id"
        },{
            data: null,
            render: function (data) {
                return data.business.cc_name;
            }
        }, {
            data: null,
            render: function (data) {
                return data.start_time ? data.start_time : '--';
            }
        }, {
            data: null,
            render: function (data) {
                return data.finish_time ? data.finish_time : '--';
            }
        }, {
            data: "category_name"
        }, {
            data: "creator_name"
        }, {
            data: null,
            render: function (data) {
                return data.executor_name ? data.executor_name : '--';
            }
        }, {
            data: null,
            render: function (data) {
                if (data.is_finished) {
                    return '<span class="label label-success">' + gettext('完成') + '</span>';
                } else if (data.is_started) {
                    return '<i class="fa fa-spinner fa-spin loading-state" data-id="' + data.id + '" data-cc_id="' + data.business.cc_id +'"></i>';
                } else {
                    return '<span class="label label-primary">' + gettext('未执行') + '</span>';
                }
            }
        }
    ];
    var render_name_func = function (data) {
        return '<a class="recording" title="' + htmlspecialchars(data.name) + '" href="' + SITE_URL + 'taskflow/execute/' + data.business.cc_id + '/?instance_id=' + data.id +'">' + htmlspecialchars(data.name) + '</a>';
    };
    columns.splice(9, 0, {
        data: null,
        orderable: false,
        render: function (data, type, row, meta) {
            return '<div class="elastic1">' +
                '<button class="king-btn king-info w-auto mr5" style="border-radius: 0">' + gettext('查看') + '</button>' +
                '</div> ';
        }
    });
    columns.splice(2, 0, {
        data: null,
        render: render_name_func,
    });

    $("#audit_datatables").dataTable({
        autoWidth: false,
        lengthChange: false, //是否允许用户改变表格每页显示的记录数
        pageLength: 10, //每页显示几条数据
        pagingType: 'full_numbers',
        processing: true,
        serverSide: true,
        current_draw: undefined,
        ajax: function (data, callback, oSettings) {
            var that = this;
            var params = {
                limit: data.length,
                offset: data.start,
            };
            // 关键字过滤
            if (data.search.value) {
                params['q'] = data.search.value;
            }
            // 任务类型过滤
            $.ajax({
                type: "GET",
                url: datasource_api,
                dataType: "JSON",
                data: params,
                success: function (response) {
                    if (that.current_draw == undefined) {
                        that.current_draw = data.draw;
                    }
                    var json = {
                        data: response.objects.map(function(x){
                            if(x.engine_task){
                                x.bpm_task=x.engine_task;
                            }
                            return x;
                        }),
                        recordsTotal: response.meta.total_count,
                        draw: that.current_draw++,
                        //recordsFiltered: data.length,
                        recordsFiltered: response.meta.total_count,
                    }
                    callback(json);
                },
                error: function (e) {
                    alert_msg(e);
                }
            });
        },
        ordering: false,
        // 表格对应列的数据
        columns: columns,
        language: language,
        drawCallback: function () {
            // 通过Ajax获取已开始但是未完成任务的状态
            var loading_objs = $('i.loading-state');
            var len_objs = loading_objs.length;
            for (var i = 0; i < len_objs; i++) {
                var task_id = loading_objs.eq(i).attr('data-id');
                var cc_id = loading_objs.eq(i).attr('data-cc_id');
                render_task_state(task_id, cc_id, loading_objs.eq(i));
            }
        }
    }).on('draw.dt', function () {
        $("#audit_datatables_filter").parent().addClass('filter-myStyle').siblings('.col-sm-6').addClass('length-myStyle');
        $("#audit_datatables_filter").find('input').attr('placeholder', gettext('请输入关键字'));
    });

    var t = $("#audit_datatables").DataTable(); //获取datatables对象

    //查看按钮绑定事件
    $("#audit_datatables tbody").on('click', '.elastic1 button', function() {
        var tr_dom = $(this).parents('tr');
        tr_dom.find('td a')[0].click();
    });
    //表格(DataTables) end

    $(".nav-left").on('click', 'li.border-ddd',function(){
        $(this).addClass("active").siblings().removeClass("active")
    });

});


function change_time_zone(origin_time, dest_tz) {
    if(origin_time.length !== 25 || !dest_tz){
        return origin_time;
    }
    var origin_time_core = origin_time.slice(0, 19);
    var origin_tz_num = origin_time.slice(20, 25);
    var dest_tz_num = moment().tz(dest_tz).format('Z').replace(':', '');
    var interval_hours = (eval(dest_tz_num) - eval(origin_tz_num)) / 100;
    return moment(origin_time_core).add(interval_hours, 'hours').format('YYYY-MM-DD HH:mm:ss') + ' ' + dest_tz_num;
}
// $('#taskflow_datatables_processing').css('display','none');

function render_task_state(task_id, cc_id, obj){
    $.ajax({
        url: SITE_URL + 'taskflow/api/status/' + cc_id + '/',
        method: "GET",
        data: {'instance_id': task_id},
        success: function (res) {
            if (res.result) {
                if (res.data.state == 'FINISHED') {
                    obj.replaceWith('<span class="label label-success">' + gettext('完成') + '</span>');
                } else if (res.data.state == 'RUNNING') {
                    obj.replaceWith('<span class="label label-warning">' + gettext('执行中') + '</span>');
                } else if (res.data.state == 'FAILED') {
                    obj.replaceWith('<span class="label label-danger">' + gettext('失败') + '</span>');
                } else if (res.data.state == 'BLOCKED') {
                    obj.replaceWith('<span class="label label-warning">' + gettext('执行中') + '</span>');
                } else if (res.data.state == 'SUSPENDED') {
                    obj.replaceWith('<span class="label label-warning ">' + gettext('暂停') + '</span>');
                } else if (res.data.state == 'REVOKED') {
                    obj.replaceWith('<span class="label label-danger">' + gettext('撤销') + '</span>');
                } else if (res.data.state == 'NODE_SUSPENDED') {
                    obj.replaceWith('<span class="label label-warning">' + gettext('节点暂停') + '</span>')
                } else {
                    obj.replaceWith('<span class="label label-danger">' + gettext('未知') + '</span>')
                    console.error(res.data.state);
                }
            } else {
                console.error(res);
                obj.replaceWith('<span class="label label-danger">' + gettext('未知') + '</span>');
            }
        },
        error: function (res) {
            console.error(res);
            obj.replaceWith('<span class="label label-warning">' + gettext('未知') + '</span>');
        }
    });
}
