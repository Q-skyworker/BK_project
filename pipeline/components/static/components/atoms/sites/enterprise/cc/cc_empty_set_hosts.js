(function(){
    $.atoms.cc_empty_set_hosts = [
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
    ]
})();