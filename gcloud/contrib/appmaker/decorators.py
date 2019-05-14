# -*- coding: utf-8 -*-
from functools import wraps

from django.utils.decorators import available_attrs
from django.http import HttpResponseForbidden

from gcloud.contrib.appmaker.models import AppMaker


def check_db_object_exists(model):
    """
    @summary 请求的DB数据是否存在
    @return:
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            biz_cc_id = kwargs.get('biz_cc_id')
            if model == 'AppMaker':
                app_id = kwargs.get('app_id')
                if not AppMaker.objects.filter(pk=app_id, business__cc_id=biz_cc_id, is_deleted=False).exists():
                    # return HttpResponseNotFound() 返回404不能显示404.html
                    return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
