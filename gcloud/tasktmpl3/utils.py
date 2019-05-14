# -*- coding: utf-8 -*-
import itertools

from django.db import transaction
from django.http import HttpResponseForbidden
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from guardian.shortcuts import (assign_perm,
                                remove_perm,
                                get_users_with_perms,
                                get_groups_with_perms,
                                get_group_perms,
                                get_user_perms
                                )

from common.log import logger

from gcloud.core.roles import CC_PERSON_GROUP, CC_ROLES
from gcloud.core.utils import get_business_obj


@transaction.atomic
def assign_tmpl_perms(request, perms, groups, tmpl_inst):
    user = request.user
    biz = tmpl_inst.business

    if user.has_perm('manage_business', biz):
        # 先删除所有有当前要授权权限的分组的权限
        perm_groups = get_groups_with_perms(tmpl_inst)
        for group in perm_groups:
            perm_list = get_group_perms(group, tmpl_inst)
            for perm in perm_list:
                if perm in perms:
                    remove_perm(perm, group, tmpl_inst)
        # 给当前有权限的分组授权
        for perm, group in itertools.product(perms, groups):
            assign_perm(perm, group, tmpl_inst)
    else:
        return HttpResponseForbidden()


@transaction.atomic
def assign_tmpl_perms_user(request, perms, users, tmpl_inst):
    user = request.user
    biz = tmpl_inst.business

    if user.has_perm('manage_business', biz):
        # 删除有当前要授权权限的所有拥有用户的授权信息
        perm_users = get_users_with_perms(tmpl_inst)
        for name in perm_users:
            perm_list = get_user_perms(name, tmpl_inst)
            for perm in perm_list:
                if perm in perms:
                    remove_perm(perm, name, tmpl_inst)
        # then assign perms
        for perm, name in itertools.product(perms, users):
            assign_perm(perm, name, tmpl_inst)
    else:
        return HttpResponseForbidden()


def get_notify_group_by_biz_core(biz_cc_id):
    """
    @summary: 获取默认通知分组加业务自定义通知分组
    @param biz_cc_id:
    @return:
    """
    # 出错通知人员分组
    notify_group_list = list(CC_PERSON_GROUP)
    return notify_group_list


def get_notify_receivers(username, biz_cc_id, receiver_group, more_receiver):
    """
    @summary: 根据通知分组和附加通知人获取最终通知人
    @param username: 请求人
    @param biz_cc_id: 业务CC ID
    @param receiver_group: 通知分组
    @param more_receiver: 附加通知人
    @return:
    """
    # produce a request on backend
    request = RequestFactory().get('/')
    User = get_user_model()
    user = User.objects.get(username=username)
    setattr(request, 'user', user)

    biz_info, __, role_info = get_business_obj(request, biz_cc_id,
                                               use_maintainer=True)
    notify_receivers = [username]
    if not isinstance(receiver_group, list):
        receiver_group = receiver_group.split(',')
    if not isinstance(more_receiver, list):
        if more_receiver.strip():
            more_receiver = more_receiver.strip().split(',')
            notify_receivers += more_receiver
    for group in receiver_group:
        if group in CC_ROLES:
            role_members = role_info.get(group, '')
            if role_members:
                # ESB组件接口返回的人员信息，多个人是用;分隔的
                notify_receivers += role_members.split(';')
    notify_receivers = list(set(notify_receivers))
    return notify_receivers


def get_template_context(obj):
    try:
        from gcloud.tasktmpl3.models import TaskTemplate
        template = TaskTemplate.objects.get(pipeline_template=obj)
    except TaskTemplate.DoesNotExist as e:
        logger.warning('TaskTemplate Does not exit: pipeline_template.id=%s' % obj.pk)
        return {}
    context = {
        'biz_cc_id': template.business.cc_id,
        'biz_cc_name': template.business.cc_name
    }
    return context
