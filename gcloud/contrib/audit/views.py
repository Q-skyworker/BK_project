# -*- coding: utf-8 -*-
from django.http import HttpResponseForbidden

from bk_api import is_user_auditor
from common.mymako import render_mako_context
from gcloud.core.utils import prepare_view_all_business


def home(request):
    # 只有审计人员可以查看
    is_auditor = is_user_auditor(request)
    if not is_auditor:
        return HttpResponseForbidden()
    prepare_view_all_business(request)
    return render_mako_context(request, '/audit/home.html')
