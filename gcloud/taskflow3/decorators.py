# -*- coding: utf-8 -*-
from functools import wraps

from django.utils.decorators import available_attrs
from django.http import HttpResponseForbidden

from gcloud.taskflow3.models import TaskFlowInstance


def check_user_perm_of_task(permit_flow=None):
    """
    @summary 请求的任务是否存在
    @param permit_flow: 鉴权的任务阶段
    @return:
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            biz_cc_id = kwargs.get('biz_cc_id')
            instance_id = kwargs.get('instance_id') or request.POST.get('instance_id')
            taskflow = TaskFlowInstance.objects.filter(pk=instance_id, business__cc_id=biz_cc_id)
            if not taskflow.count():
                # return HttpResponseNotFound() 返回404不能显示404.html
                return HttpResponseForbidden()
            # 判断权限
            if permit_flow and not taskflow[0].user_has_perm(
                    request.user, permit_flow):
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
