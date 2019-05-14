# -*- coding: utf-8 -*-
from common.mymako import render_mako_context
from gcloud.core.models import Business


def home(request, biz_cc_id):
    """
    @summary: 业务配置列表页面跳转
    @param request:
    @param biz_cc_id:
    @return:
    """
    business = Business.objects.get(cc_id=biz_cc_id)
    ctx = {
        'executor': business.executor,
    }
    return render_mako_context(request, "/config/biz_executor.html", ctx)
