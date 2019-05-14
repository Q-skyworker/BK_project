/**
 * Created by Administrator on 2018/11/20.
 */
(function () {
    $.atoms.create_vm = [
        // {
        //     tag_code: "is_interface",
        //     type: "input",
        //     attrs: {
        //         name: gettext("接口调用"),
        //         placeholder: gettext("必填(true/false)"),
        //         hookable: true
        //     },
        //     validation: [
        //         {
        //             type: "required"
        //         }
        //     ]
        // },
        {
            tag_code: "host",
            type: "input",
            attrs: {
                name: gettext("主机"),
                placeholder: gettext("必填，主机IP"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "account",
            type: "input",
            attrs: {
                name: gettext("VC账号"),
                placeholder: gettext("必填，VC账号"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "password",
            type: "input",
            attrs: {
                name: gettext("VC密码"),
                placeholder: gettext("必填，VC密码"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "dc_moId",
            type: "input",
            attrs: {
                name: gettext("dc_moId"),
                placeholder: gettext("必填，datacenter moId"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "hc_moId",
            type: "input",
            attrs: {
                name: gettext("hc_moId"),
                placeholder: gettext("必填,独立主机/集群MoId"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "ds_moId",
            type: "input",
            attrs: {
                name: gettext("ds_moId"),
                placeholder: gettext("必填,存储MoId"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "vs_moId",
            type: "input",
            attrs: {
                name: gettext("vs_moId"),
                placeholder: gettext("必填,网卡MoId"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "vs_name",
            type: "input",
            attrs: {
                name: gettext("vs_name"),
                placeholder: gettext("必填,网卡名称"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "folder_moId",
            type: "input",
            attrs: {
                name: gettext("folder_moId"),
                placeholder: gettext("必填,文件夹MoId"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "vmtemplate_os",
            type: "input",
            attrs: {
                name: gettext("tem_os"),
                placeholder: gettext("必填，模板操作系统（windows/linux）"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "vmtemplate_moId",
            type: "input",
            attrs: {
                name: gettext("teme_moId"),
                placeholder: gettext("必填，模板MoId"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "computer_name",
            type: "input",
            attrs: {
                name: gettext("com_name"),
                placeholder: gettext("必填，主机名"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "vm_name",
            type: "input",
            attrs: {
                name: gettext("vm_name"),
                placeholder: gettext("必填， VC上的机器名称"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "vmtemplate_pwd",
            type: "input",
            attrs: {
                name: gettext("tem_pwd"),
                placeholder: gettext("必填，模板密码"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "cpu",
            type: "input",
            attrs: {
                name: gettext("cpu"),
                placeholder: gettext("必填，cpu大小"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "mem",
            type: "input",
            attrs: {
                name: gettext("内存"),
                placeholder: gettext("必填，内存大小"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "disk_type",
            type: "input",
            attrs: {
                name: gettext("磁盘类型"),
                placeholder: gettext("非必填（thin/thick）"),
                hookable: true
            },
            validation: [
                // {
                //     type: "required"
                // }
            ]
        },
        {
            tag_code: "disk_size",
            type: "input",
            attrs: {
                name: gettext("磁盘大小"),
                placeholder: gettext("非必填,当磁盘类型不为空时，必填。"),
                hookable: true
            },
            validation: [
                // {
                //     type: "required"
                // }
            ]
        },
        {
            tag_code: "ip",
            type: "input",
            attrs: {
                name: gettext("ip"),
                placeholder: gettext("必填"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "mask",
            type: "input",
            attrs: {
                name: gettext("子网掩码"),
                placeholder: gettext("必填"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
         {
            tag_code: "gateway",
            type: "input",
            attrs: {
                name: gettext("网关"),
                placeholder: gettext("必填"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "dns",
            type: "input",
            attrs: {
                name: gettext("DNS列表"),
                placeholder: gettext("必填，多个以逗号分割"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        }



    ]
})();

