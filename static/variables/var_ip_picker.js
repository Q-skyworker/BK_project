(function () {
    $.atoms.var_ip_picker = [
        {
            tag_code: "ip_picker",
            type: "combine",
            attrs: {
                name: "IP/DNS选择器",
                hookable: true,
                children: [
                    {
                        tag_code: "var_ip_method",
                        type: "select",
                        attrs: {
                            name: gettext("填参方式"),
                            items: [
                                {value: "custom", text: gettext("自定义输入")},
                                {value: "select", text: gettext("选择集群和模块自动获取")},
                                {value: "input", text: gettext("输入集群名和模块名自动获取")},
                            ],
                            default: "custom",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "init",
                                action: function(){
                                    var self = this;
                                    function init_self(self){
                                        setTimeout(function(){
                                            self.emit_event(self.tag_code, "change", self.value)
                                        }, 500)
                                    }
                                    init_self(self);
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_value_type",
                        type: "radio",
                        attrs: {
                            name: gettext("值类型"),
                            items: [
                                {value: "ip", name: gettext("IP")},
                                {value: "dns", name: gettext("DNS")},
                                {value: "zone_id", name: gettext("服ID")},
                            ],
                            default: "ip",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function(value){
                                    var self = this;
                                    if(value === 'custom'){
                                        self.items = [
                                            {value: "ip", name: gettext("IP")},
                                            {value: "dns", name: gettext("DNS")},
                                            {value: "zone_id", name: gettext("服ID")},
                                        ];
                                    }else{
                                        self.items = [
                                            {value: "ip", name: gettext("IP")},
                                            {value: "dns", name: gettext("DNS")},
                                        ];
                                        if(self._get_value() === 'zone_id'){
                                            self._set_value('ip');
                                            // TODO
                                            //self.trigger('change');
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_custom_value",
                        type: "textarea",
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("IP必须填写【集群名称|模块名称|IP】、【云区域ID:IP】或者【IP】格式之一，多个用换行符分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的")
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function(value){
                                    var self = this;
                                    if(value === 'custom'){
                                        self.show();
                                    }else{
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "var_ip_value_type",
                                type: "change",
                                action: function(value){
                                    var self = this;
                                    if(value === 'dns'){
                                        self.name = gettext("DNS");
                                        self.placeholder = gettext("DNS必须填【IP#端口】格式或者直接填DNS，多个请用换行分隔");
                                    }else if(value === 'zone_id'){
                                        self.name = gettext("服ID");
                                        self.placeholder = gettext("服ID用于GCS原子自动获取域名，多个请用空格分隔");
                                    }else{
                                        self.name = gettext("IP");
                                        self.placeholder = gettext("IP必须填写【集群名称|模块名称|IP】、【云区域ID:IP】或者【IP】格式之一，多个用换行符分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的");
                                    }
                                }
                            }

                        ]
                    },
                    {
                        tag_code: "var_ip_select_set",
                        type: "select",
                        attrs: {
                            name: gettext("集群名称"),
                            remote: false,
                            hidden: true,
                            multiple: true
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function(value){
                                    var self = this;
                                    if(value === 'select'){
                                        self.show();
                                        $.ajax({
                                            url: $.context.site_url + 'pipeline/cc_get_set_list/' + $.context.biz_cc_id + '/',
                                            type: 'GET',
                                            dataType: 'json',
                                            success: function(resp){
                                                if(!resp.result){
                                                    show_msg(resp.message, 4);
                                                }else{
                                                    self.items = resp.data;
                                                }
                                            },
                                            error: function(resp){
                                                show_msg(gettext("请求后台接口异常:") + resp.status + ',' + resp.statusText, 4);
                                            }
                                        })
                                    }else{
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_select_module",
                        type: "select",
                        attrs: {
                            name: gettext("模块名称"),
                            remote: false,
                            hidden: true,
                            multiple: true
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function(value){
                                    var self = this;
                                    if(value === 'select'){
                                        self.show();
                                        $.ajax({
                                            url: $.context.site_url + 'pipeline/cc_get_module_name_list/' + $.context.biz_cc_id + '/',
                                            type: 'GET',
                                            dataType: 'json',
                                            success: function(resp){
                                                if(!resp.result){
                                                    show_msg(resp.message, 4);
                                                }else{
                                                    self.items = resp.data;
                                                }
                                            },
                                            error: function(resp){
                                                show_msg(gettext("请求后台接口异常:") + resp.status + ',' + resp.statusText, 4);
                                            }
                                        })
                                    }else{
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_input_set",
                        type: "input",
                        attrs: {
                            name: gettext("集群名称"),
                            hidden: true,
                            placeholder: gettext("多个用,分隔，all代表所有集群")
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function(value){
                                    var self = this;
                                    if(value === 'input'){
                                        self.show();
                                    }else{
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_input_module",
                        type: "input",
                        attrs: {
                            name: gettext("模块名称"),
                            hidden: true,
                            placeholder: gettext("多个用,分隔，all代表所有模块")
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function(value){
                                    var self = this;
                                    if(value === 'input'){
                                        self.show();
                                    }else{
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                ],
            }
        },

    ]
})();
