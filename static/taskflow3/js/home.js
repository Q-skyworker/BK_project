$(function () {
    "use strict"
    //任务类型
    var TASK_CATEGORY = [];
    var category = '';
    $.ajax({
        url: site_url + "template/get_business_basic_info/" + biz_cc_id + "/",
        type: 'GET',
        dataType: 'json',
        async: false,
        success: function (req) {
            TASK_CATEGORY = req.task_categories;
        },
        error: function (response) {
            console.log(response.responseText);
        }
    });

    var vm = new Vue({
        el: "#work_history_box",
        data: {
            taskCategory: TASK_CATEGORY,
            view_mode: VIEW_MODE,
            app_id: APP_ID,
        },
        methods: {
            choseCategory: function () {
                // debugger
                // debugger
                $(event.target).siblings('li').removeClass('active').end().addClass('active');

            }
        }
    });

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

    var datasource_api = SITE_URL + "api/v3/taskflow/?business__cc_id=" + BIZ_CC_ID;
    var columns = [
        {
            data: "id"
        },
        // NOTE 任务名称列在后续插入，需要先判断链接渲染方式
        {
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
                    return '<i class="fa fa-spinner fa-spin loading-state" data-id="' + data.id + '"></i>';
                } else {
                    return '<span class="label label-primary">' + gettext('未执行') + '</span>';
                }
            }
        }
    ];
    if (vm.view_mode == 'appmaker') {
        datasource_api += "&create_method=app_maker&create_info=" + APP_ID;
        var render_name_func = function (data) {
            return '<a class="recording" title="' + htmlspecialchars(data.name) + '" href="' + SITE_URL + 'appmaker/' + APP_ID + '/execute/' + BIZ_CC_ID + '/?instance_id=' + data.id + '">' + htmlspecialchars(data.name) + '</a>';
        };
    } else {
        if (TEMPLATE_ID) {
            datasource_api += '&template_id=' + TEMPLATE_ID;
        }
        var render_name_func = function (data) {
            return '<a class="recording" title="' + htmlspecialchars(data.name) + '" href="' + SITE_URL + 'taskflow/execute/' + BIZ_CC_ID + '/?instance_id=' + data.id + '">' + htmlspecialchars(data.name) + '</a>';
        };
    }
    columns.splice(1, 0, {
        data: null,
        render: render_name_func,
    });
    if (vm.view_mode !== 'appmaker') {
        columns.splice(8, 0, {
            data: null,
            orderable: false,
            render: function (data, type, row, meta) {
                var html = '<div class="elastic1">' +
                    '<button class="king-btn king-info w-auto mr5" style="border-radius: 0">' + gettext('克隆') + '</button>' +
                    '<a class="hide" href=""></a>';

                if (!data.is_started && !data.is_finished) {
                    html += '<a class="king-btn king-danger w-auto delete-btn">' + gettext('删除') + '</a>';
                }
                html += '</div>';
                return html;
            }
        });
    }

    $("#taskflow_datatables").dataTable({
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
            if (category && category !== "all") {
                params['category'] = category;
            }
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
                        data: response.objects.map(function (x) {
                            if (x.engine_task) {
                                x.bpm_task = x.engine_task;
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
                render_task_state(task_id, loading_objs.eq(i));
            }
        }
    }).on('draw.dt', function () {
        $("#taskflow_datatables_filter").parent().addClass('filter-myStyle').siblings('.col-sm-6').addClass('length-myStyle');
        $("#taskflow_datatables_filter input").attr('placeholder', gettext('请输入ID或者任务名称'));
    });

    var t = $("#taskflow_datatables").DataTable(); //获取datatables对象
    $(".taskflow-type").on('click', 'li', function () {
        category = $(this).attr('data-search');
        t.ajax.reload();
    });


    //克隆按钮绑定事件
    $("#taskflow_datatables tbody").on('click', '.elastic1 button', function () {
        var tr_dom = $(this).parents('tr');
        var row = t.row(tr_dom); //获取按钮所在的行
        var data = row.data();
        $.post(SITE_URL + 'taskflow/api/clone/' + BIZ_CC_ID + '/',
            {
                'instance_id': data.id,
                'create_method': vm.view_mode == 'appmaker' ? 'app_maker' : 'app',
                'create_info': vm.app_id,
            },
            function (response) {
                if (response.result) {
                    $(tr_dom.find('.elastic1 a')[0]).attr('href', SITE_URL + 'taskflow/execute/' + BIZ_CC_ID + '/?instance_id=' + response.data.new_instance_id);
                    tr_dom.find('.elastic1 a')[0].click();
                } else {
                    show_msg(result.message, 4);
                }
            }
        )
    });

    $("#taskflow_datatables tbody").on('click', '.elastic1 .delete-btn', function () {
        var tr_dom = $(this).parents('tr');
        var row = t.row(tr_dom); //获取按钮所在的行
        var data = row.data();
        var delDialog = dialog({
            width: 300,
            title: gettext('提示'),
            content: '<p style="font-size: 16px;text-align: center;">'+ gettext('您确定要删除该流程吗？') +'</p>',
            ok: function () {
                $.ajax({
                    url: SITE_URL + 'api/v3/taskflow/' + data.id + '/',
                    method: "delete",
                    success: function () {
                        show_msg(gettext("删除任务成功"), 2);
                        row.remove().draw();
                    },
                    error: function (response) {
                        show_msg(gettext("删除任务失败"), 4);
                    }
                });
            },
            okValue: gettext('确定'),
            cancel: function () {},
            cancelValue: gettext('取消')
        }).showModal()
    });

    //表格(DataTables) end

    $(".nav-left").on('click', 'li.border-ddd', function () {
        $(this).addClass("active").siblings().removeClass("active")
    });

});

// $('#taskflow_datatables_processing').css('display','none');

function render_task_state(task_id, obj) {
    $.ajax({
        url: SITE_URL + 'taskflow/api/status/' + BIZ_CC_ID + '/',
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
