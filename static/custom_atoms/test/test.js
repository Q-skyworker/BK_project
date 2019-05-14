(function () {
    $.atoms.test_Atom = [
        {
            tag_code: "app_id",
            type: "input",
            attrs: {
                name: gettext("业务名称"),
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