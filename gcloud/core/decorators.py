# -*- coding: utf-8 -*-
from functools import wraps

from django.http import HttpResponseForbidden
from django.utils.decorators import available_attrs

from gcloud.core.models import Business


def check_user_perm_of_business(permit):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            biz_cc_id = kwargs.get('biz_cc_id') or kwargs.get('bk_biz_id')
            try:
                biz = Business.objects.get(cc_id=biz_cc_id)
            except Business.DoesNotExist:
                return HttpResponseForbidden()
            if not request.user.has_perm(permit, biz):
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
