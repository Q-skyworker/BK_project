/**
 * Created by Administrator on 2018/11/20.
 */
(function () {
    $.atoms.create_OrSql = [
        {
            tag_code: "user",
            type: "input",
            attrs: {
                name: gettext("用户名:"),
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
            tag_code: "password",
            type: "input",
            attrs: {
                name: gettext("密码:"),
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
            tag_code: "account",
            type: "input",
            attrs: {
                name: gettext("IP/端口/库名:"),
                placeholder: gettext("10.115.161.205:1521/Db_name"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "choice",
            type: "input",
            attrs: {
                name: gettext("执行操作:"),
                placeholder: gettext("create/select"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "sql",
            type: "input",
            attrs: {
                name: gettext("Sql语句:"),
                placeholder: gettext("必填"),
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
