(function () {
    $.atoms.start_vm = [
        {
            tag_code: "is_interface",
            type: "input",
            attrs: {
                name: gettext("接口调用"),
                placeholder: gettext("必填(true/false)"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
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
            tag_code: "vm_moId",
            type: "input",
            attrs: {
                name: gettext("vm_moId"),
                placeholder: gettext("必填，虚拟机ID"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        }
    ];
})();