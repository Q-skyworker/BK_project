# -*- coding: utf-8 -*-
import ujson as json

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from guardian.shortcuts import (get_groups_with_perms,
                                get_group_perms,
                                get_users_with_perms,
                                get_user_perms)

from gcloud.core.constant import TASK_CATEGORY, TASK_FLOW_TYPE, NOTIFY_TYPE
from gcloud.core.decorators import check_user_perm_of_business
from gcloud.core.roles import ALL_ROLES
from gcloud.tasktmpl3.utils import (assign_tmpl_perms,
                                    assign_tmpl_perms_user,
                                    get_notify_group_by_biz_core)
from gcloud.tasktmpl3.models import TaskTemplate, FILL_PARAMS_PERM_NAME, EXECUTE_TASK_PERM_NAME


@require_GET
@check_user_perm_of_business('manage_business')
def clone(request, biz_cc_id):
    """
    @summary: 获取克隆的模板数据，未创建模板
    @param request:
    @param biz_cc_id:
    @return:
    """
    template_id = request.GET.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    ctx = {
        'result': True,
        'data': {
            'data': json.dumps(template.get_clone_pipeline_tree()),
            'name': 'clone%s' % timezone.now().strftime('%Y%m%d%H%M%S'),
        }
    }
    return JsonResponse(ctx)


@require_GET
def form(request, biz_cc_id):
    template_id = request.GET.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    ctx = {
        'form': template.get_form(),
        'outputs': template.get_outputs()
    }
    return JsonResponse(ctx)


@require_POST
def collect(request, biz_cc_id):
    template_id = request.POST.get('template_id')
    method = request.POST.get('method', 'add')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    ctx = template.user_collect(request.user.username, method)
    return JsonResponse(ctx)


@require_GET
def get_perms(request, biz_cc_id):
    template_id = request.GET.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    fill_params_groups = []
    execute_task_groups = []
    groups = get_groups_with_perms(template)
    # 获取有权限的分组列表
    for group in groups:
        perm_list = get_group_perms(group, template)
        for perm in perm_list:
            if perm == FILL_PARAMS_PERM_NAME:
                fill_params_groups.append({
                    "show_name": group.name.split("\x00")[-1]
                })
            elif perm == EXECUTE_TASK_PERM_NAME:
                execute_task_groups.append({
                    "show_name": group.name.split("\x00")[-1]
                })
    # 获取有权限的人员列表
    users = get_users_with_perms(template)
    for user in users:
        perm_list = get_user_perms(user, template)
        for perm in perm_list:
            if perm == FILL_PARAMS_PERM_NAME:
                fill_params_groups.append({
                    "show_name": user.username
                })
            elif perm == EXECUTE_TASK_PERM_NAME:
                execute_task_groups.append({
                    "show_name": user.username
                })
    ctx = {
        'result': True,
        'data': {
            'fill_params_groups': fill_params_groups,
            'execute_task_groups': execute_task_groups,
        }
    }
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_business('manage_business')
def save_perms(request, biz_cc_id):
    template_id = request.POST.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    user_model = get_user_model()
    for perm in [FILL_PARAMS_PERM_NAME, EXECUTE_TASK_PERM_NAME]:
        group_name_list = []
        user_name_list = []
        for data in json.loads(request.POST.get(perm, '[]')):
            if data in ALL_ROLES:
                group_name = "%s\x00%s" % (biz_cc_id, data)
                group_name_list.append(group_name)
            else:
                user_name_list.append(data)
        group_set = Group.objects.filter(name__in=group_name_list)
        assign_tmpl_perms(request, [perm], group_set, template)
        user_set = user_model.objects.filter(username__in=user_name_list)
        assign_tmpl_perms_user(request, [perm], user_set, template)
    ctx = {
        'result': True,
        'data': '',
    }
    return JsonResponse(ctx)


@require_GET
def get_business_basic_info(request, biz_cc_id):
    """
    @summary: 获取业务基本配置信息
    @param request:
    @param biz_cc_id:
    @return:
    """
    # 类型数据来源
    task_categories = []
    for item in TASK_CATEGORY:
        task_categories.append({
            'value': item[0],
            'name': item[1]
        })
    # 模板流程来源
    flow_type_list = []
    for item in TASK_FLOW_TYPE:
        flow_type_list.append({
            'value': item[0],
            'name': item[1]
        })

    # 出错通知人员分组
    notify_group = get_notify_group_by_biz_core(biz_cc_id)

    # 出错通知方式来源
    notify_type_list = []
    for item in NOTIFY_TYPE:
        notify_type_list.append({
            'value': item[0],
            'name': item[1]
        })

    ctx = {
        "task_categories": task_categories,
        "flow_type_list": flow_type_list,
        "notify_group": notify_group,
        "notify_type_list": notify_type_list,
    }
    return JsonResponse(ctx, safe=False)
