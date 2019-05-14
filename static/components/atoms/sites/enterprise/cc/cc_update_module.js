(function(){
    $.atoms.cc_update_module = [
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
            tag_code: "cc_module_property",
            type: "select",
            attrs: {
                name: gettext("模块属性"),
                placeholder: gettext("请选择需要更新的模块属性"),
                hookable: true,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/cc_search_object_attribute/module/' + $.context.biz_cc_id + '/',
                remote_data_init: function(resp) {
                    return resp.data;
                },
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "cc_module_prop_value",
            type: "input",
            attrs: {
                name: gettext("属性值"),
                placeholder: gettext("请输入更新后的属性值"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
    ]
})();