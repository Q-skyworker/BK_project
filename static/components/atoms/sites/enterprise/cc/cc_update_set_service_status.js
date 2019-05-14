(function(){
    $.atoms.cc_update_set_service_status = [
        {
            tag_code: "cc_set_select",
            type: "tree",
            attrs: {
                name: gettext("集群"),
                hookable: true,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/cc_search_topo/set/' + $.context.biz_cc_id + '/',
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
            tag_code: "cc_set_status",
            type: "radio",
            attrs: {
                name: gettext("服务状态"),
                hookable: true,
                items: [
                    {"name": "开放", "value": "1"},
                    {"name": "关闭", "value": "2"},
                ],
                default: "1",
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
    ]
})();