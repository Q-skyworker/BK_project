(function () {
    $.atoms.job_fast_push_file = [
        {
            tag_code: "job_source_files",
            type: "datatable",
            attrs: {
                name: gettext("源文件"),
                editable: true,
                add_btn: true,
                columns: [
                    {
                        tag_code: "ip",
                        title: gettext("IP"),
                        type: "input",
                        width: '100px',
                        editable: true,
                        attrs: {
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "files",
                        title: gettext("文件路径"),
                        type: "input",
                        width: '200px',
                        editable: true,
                        attrs: {
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "account",
                        title: gettext("执行账户"),
                        type: "input",
                        width: '100px',
                        editable: true,
                        attrs: {
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    }
                ],
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_ip_list",
            type: "textarea",
            attrs: {
                name: gettext("目标IP"),
                placeholder: gettext("IP必须填写【集群名称|模块名称|IP】、【云区域ID:IP】或者【IP】格式之一，多个用换行符分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_account",
            type: "input",
            attrs: {
                name: gettext("目标账户"),
                placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_target_path",
            type: "input",
            attrs: {
                name: gettext("目标路径"),
                placeholder: gettext("请输入绝对路径"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();