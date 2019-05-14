# -*- coding: utf-8 -*-
from django.http import HttpResponseForbidden

from bk_api import is_user_functor
from common.mymako import render_mako_context
from gcloud.core.utils import prepare_view_all_business


def home(request):
    # 只有职能化人员可以查看
    is_functor = is_user_functor(request)
    if not is_functor:
        return HttpResponseForbidden()
    prepare_view_all_business(request)
    return render_mako_context(request, '/function/home.html')
