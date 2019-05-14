(function () {
    $.atoms.cc_transfer_host_module = [
        {
            tag_code: "cc_host_ip",
            type: "textarea",
            attrs: {
                name: gettext("主机内网IP"),
                placeholder: gettext("请输入主机内网IP，多个用换行符分隔"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "cc_module_select",
            type: "tree",
            attrs: {
                name: gettext("模块"),
                hookable: true,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/cc_search_topo/module/' + $.context.biz_cc_id + '/',
                remote_data_init: function(resp) {
                    return resp.data;
                },
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            methods: {}
        },
        {
            tag_code: "cc_is_increment",
            type: "radio",
            attrs: {
                name: gettext("转移方式"),
                hookable: true,
                items: [
                    {"name": gettext("覆盖"), "value": false},
                    {"name": gettext("追加"), "value": true},
                ],
                default: false,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
    ]
})();