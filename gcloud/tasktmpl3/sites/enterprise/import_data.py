# -*- coding=utf-8 -*-
from django.http import JsonResponse

from gcloud.core.decorators import check_user_perm_of_business


@check_user_perm_of_business('manage_business')
def import_v1(request, biz_cc_id):
    result = {
        'result': True,
        'data': 0,
        'message': 'nothing to do'
    }
    return JsonResponse(result)
