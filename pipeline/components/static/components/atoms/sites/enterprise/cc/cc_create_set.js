(function(){
    $.atoms.cc_create_set = [
        {
            tag_code: "cc_set_parent_select",
            type: "tree",
            attrs: {
                name: gettext("父节点"),
                hookable: true,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/cc_search_set_parent_topo/' + $.context.biz_cc_id + '/',
                remote_data_init: function(resp) {
                    return resp.data;
                },
                validation: [
                ]
            },
            methods: {}
        },
    ]
})();