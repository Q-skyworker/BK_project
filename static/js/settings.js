//-----------------------------------------------------------
/**
 * 调试配置，请只在这个地方进行设置，不要动其他代码
 */
var debug = true; // 是否是调试模式，注意：在上传代码的时候，要改为false
//-----------------------------------------------------------

//以下公用代码区域，使用范围非常广，请勿更改--------------------------------
document.write(" <script lanague=\"javascript\" src=\"" + static_url + "assets/artdialog/jquery.artDialog.js?skin=simple\"> <\/script>");
//csrftoken
document.write(" <script lanague=\"javascript\" src=\"" + static_url + "js/csrftoken.js\"> <\/script>");

/**
 * ajax全局设置
 */
// 在这里对ajax请求做一些统一公用处理
$.ajaxSetup({
//	timeout: 8000,
    statusCode: {
        // tastypie args error
        400: function (xhr) {
            var _src = xhr.responseText;
            alert(_src);
        },
        401: function (xhr) {
            var _src = xhr.responseText;
            var ajax_content = '<iframe name="403_iframe" frameborder="0" src="' + _src + '" style="width:570px;height:400px;"></iframe>';
            art.dialog({
                title: gettext("提示"),
                lock: true,
                content: ajax_content
            });
            return;
        },
        402: function (xhr) {
            // 功能开关
            var _src = xhr.responseText;
            var ajax_content = '<iframe name="403_iframe" frameborder="0" src="' + _src + '" style="width:570px;height:400px;"></iframe>';
            art.dialog({
                title: gettext("提示"),
                lock: true,
                content: ajax_content
            });
            return;
        },
        403: function (xhr) {
            var ajax_content = '<div class="king-exception-box king-500-page">' +
                '<img src="' + STATIC_URL + 'images/expre_403.png">' +
                '<h1>' + gettext('您没有访问权限') + '</h1>' +
                '</div>';
            art.dialog({
                title: gettext("提示"),
                lock: true,
                content: ajax_content
            });
            return;
        },
        405: function (xhr) {
            var ajax_content = '<div class="king-exception-box king-500-page">' +
                '<img src="' + STATIC_URL + 'images/expre_403.png">' +
                '<h2 >' + gettext('对不起，您没有权限进行此操作') + '</h2>' +
                '<div style="text-align: left;margin-left:77px;">' +
                '<p style="margin-bottom:10px;margin-top:30px;font-size:16px;font-weight:bold;">' + gettext('请尝试如下操作：') + '</p>' +
                '<ul>' +
                '<li style="list-style-type: disc;">' + gettext('联系业务“管理员”为您添加操作权限') + '</li>' +
                '</ul>' +
                '<br/>' +
                '</div>' +
                '</div>';
            art.dialog({
                title: gettext("提示"),
                lock: true,
                content: ajax_content
            });
            return;
        },
        500: function (xhr, textStatus) {
            // 异常
            if (debug) {
                console.log("系统出现异常(" + xhr.status + '):' + xhr.responseText);
            }
            alert(gettext("系统出现异常, 请记录下错误场景并与开发人员联系, 谢谢!"));
        }
    }
});