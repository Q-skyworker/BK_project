(function () {
    $.atoms.bk_http_request = [
        {
            tag_code: "bk_http_request_method",
            type: "select",
            attrs: {
                name: gettext("请求方式"),
                hookable: true,
                items: [
                    {text: "GET", value: "GET"},
                    {text: "POST", value: "POST"},
                    {text: "PUT", value: "PUT"},
                    {text: "DELETE", value: "DELETE"},
                    {text: "PATCH", value: "PATCH"},
                    {text: "HEAD", value: "HEAD"},
                    {text: "CONNECT", value: "CONNECT"},
                    {text: "OPTIONS", value: "OPTIONS"},
                    {text: "TRACE", value: "TRACE"},
                ],
                default: "GET"
            },
        },
        {
            tag_code: "bk_http_request_url",
            type: "input",
            attrs: {
                name: "URL",
                hookable: true,
                validation: [
                    {
                        type: "required"
                    },
                    {
                        type: "custom",
                        args: function (value) {
                            var result = {
                                result: true,
                                error_message: ""
                            }
                            var strRegex = '^((https|http)://)'
                                + '(([0-9]{1,3}.){3}[0-9]{1,3}'
                                + '|'
                                + '([0-9a-z_!~*\'()-]+.)*'
                                + '([0-9a-z][0-9a-z-]{0,61})?[0-9a-z].'
                                + '[a-z]{2,6})'
                                + '(:[0-9]{1,4})?'
                                + '((/?)|'
                                + '(/[0-9a-z_!~*\'().;?:@&=+$,%#-]+)+/?)$';
                            var re = new RegExp(strRegex)
                            if (!re.test(value)) {
                                result.result = false
                                result.error_message = "请输入正确的 URL"
                            }
                            return result
                        }
                    }
                ]
            }
        },
        {
            tag_code: "bk_http_request_body",
            type: "textarea",
            attrs: {
                name: "Body",
                hookable: true,
            }
        }
    ]
})();