# -*- coding: utf-8 -*-
"""
@summary: 任务流程实例views
"""
from common.mymako import render_mako_context


def home(request, biz_cc_id):
    """
    @summary: 任务记录首页
    @param request:
    @param biz_cc_id:
    @return:
    """
    ctx = {
        "view_mode": "app",
        "app_id": "",
        "template_id": request.GET.get('template_id', ''),
    }
    return render_mako_context(request, '/taskflow3/home.html', ctx)


def execute(request, biz_cc_id):
    return render_mako_context(request, "/core/base_vue.html", {})
