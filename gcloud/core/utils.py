# -*- coding: utf-8 -*-
import re

from django.core.cache import cache
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import assign_perm

from bk_api import (is_user_functor,
                    get_operate_user_list,
                    is_user_auditor,
                    get_auditor_user_list
                    )
from common.log import logger
from gcloud.conf import settings
from gcloud import exceptions
from gcloud.core.models import Business, BusinessGroupMembership
from gcloud.core import roles

CACHE_PREFIX = __name__.replace('.', '_')

DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC

# LifeCycle：'1'：测试中， '2'：已上线， '3'： 停运， 其他如'0'、''是非法值


def _get_user_business_list(request, use_cache=True):
    """Get authorized business list for a exact username.

    :param object request: django request object.
    :param bool use_cache: (Optional)
    """
    user = request.user
    cache_key = "%s_get_user_business_list_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        client = settings.ESB_GET_CLIENT_BY_REQUEST(request)
        result = client.cc.get_app_by_user_role({
            'user_role': ','.join(roles.CC_ROLES),
            # 'user_role': roles.MAINTAINERS,
        })

        if result['result']:
            data = result['data']

            # 获取用户所属开发商信息
            user_info = _get_user_info(request)
            # 兼容多开发商和单开发商模式
            if user_info.get('company_list', []):
                owner_list = [owner['company_code'] for owner in user_info['company_list']]
            elif user_info.get('company_code'):
                owner_list = [user_info.get('company_code')]
            else:
                owner_list = []

            # 按照开发商过滤
            for role, biz_list in data.iteritems():
                temp_list = []
                for item in biz_list:
                    if item.get('LifeCycle') not in ['3', _(u"停运")]:
                        if owner_list:
                            if item['Owner'] in owner_list:
                                temp_list.append(item)
                        else:
                            temp_list.append(item)
                data.update({role: temp_list})
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103, '20201', 20201,
                                '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                'cc',
                'get_app_by_user_role',
                result.get('detail_message', result['message'])
            )

    return data


def _get_user_info(request, use_cache=True):
    """
    获取用户基本信息
    @param request:
    @param use_cache:
    @return:
    """
    user = request.user
    cache_key = "%s_get_user_info_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)
    if not (use_cache and data):
        client = settings.ESB_GET_CLIENT_BY_REQUEST(request)
        auth = getattr(client, settings.ESB_AUTH_COMPONENT_SYSTEM)
        get_user_info = getattr(auth, settings.ESB_AUTH_GET_USER_INFO)
        userinfo = get_user_info({})
        userinfo.setdefault('code', -1)
        if userinfo['result']:
            data = userinfo['data']
            if data:
                cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        elif userinfo['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(userinfo['message'])
        elif userinfo['code'] in ('20103', 20103, '20201', 20201,
                                  '20202', 20202):
            raise exceptions.Forbidden(userinfo['message'])
        else:
            raise exceptions.APIError(
                settings.ESB_AUTH_COMPONENT_SYSTEM,
                'get_user',
                userinfo.get('detail_message', userinfo['message'])
            )
    return data


def _get_business_info(request, app_id, use_cache=True, use_maintainer=False):
    """Get detail infomations for a exact app_id.

    @param object request: django request object.
    @param int app_id: cc_id of core.business model.
    @param use_maintainer: 使用运维身份请求
    """
    username = request.user.username
    cache_key = "%s_get_business_info_%s_%s" % (CACHE_PREFIX, app_id, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        if use_maintainer:
            client = get_client_by_user_and_biz_id(username, app_id)
        else:
            client = settings.ESB_GET_CLIENT_BY_REQUEST(request)
        result = client.cc.get_app_by_id({
            'app_id': app_id,
            'uin_to_openid_column': ','.join(roles.CC_ROLES),
        })
        if result['result']:
            data = result['data'][0]
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103, '20201', 20201,
                                '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                'cc',
                'get_app_by_id',
                result.get('detail_message', result['message'])
            )

        cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)

    return data


def update_relationships(request, obj, extras, created=False, use_cache=True):
    """
    Update business-group(role) relationships & group-user memberships
    """
    cache_key = "%s_update_relationships_%s" % (CACHE_PREFIX, obj.cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        groups = {}
        # first, create related groups if not exist
        for role in roles.ALL_ROLES:
            group_name = "%s\x00%s" % (obj.cc_id, role)
            group, created = Group.objects.get_or_create(name=group_name)
            groups[group_name] = (group, created)

            if created:
                # assign view business perm for all roles
                assign_perm('view_business', group, obj)

                # assign manage business perm only for admin roles
                if role in roles.ADMIN_ROLES:
                    assign_perm('manage_business', group, obj)

        with transaction.atomic():
            try:
                Business.objects.select_for_update().get(pk=obj.pk)
            except Business.DoesNotExist:
                return None

            data = cache.get(cache_key)

            if not (use_cache and data):
                # If not created, clear business to group memberships
                if not created:
                    obj.groups.clear()

                for group_name in groups:
                    group, created = groups[group_name]
                    # If not created, clear group to user memberships
                    if not created:
                        group.user_set.clear()

                    BusinessGroupMembership.objects.get_or_create(
                        business=obj,
                        group=group
                    )

                    role = group_name.split('\x00')[1]
                    role_users = extras.get('{}'.format(role)) or ''
                    user_model = get_user_model()
                    user_list = role_users.split(';')

                    # 职能化人员单独授权
                    if role == roles.FUNCTOR:
                        user_list = get_operate_user_list(request)

                    # 审计人员单独授权
                    if role == roles.AUDITOR:
                        user_list = get_auditor_user_list(request)

                    for username in user_list:
                        if username:
                            user, _ = user_model.objects.get_or_create(
                                username=username)
                            user.groups.add(group)

                cache.set(cache_key, True, DEFAULT_CACHE_TIME_FOR_CC)


def prepare_view_all_business(request):
    """
    @summary：职能化和审计人员授权所有业务的查看权限
    """
    bizs = Business.objects.all()
    User = get_user_model()
    user = User.objects.get(username=request.user.username)

    for obj in bizs:
        group_name = "%s\x00%s" % (obj.cc_id, roles.AUDITOR)
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            # assign view business perm for all roles
            assign_perm('view_business', group, obj)

        BusinessGroupMembership.objects.get_or_create(
            business=obj,
            group=group
        )

        user.groups.add(group)


def get_business_obj(request, cc_id, use_cache=True, use_maintainer=False):
    cache_key = "%s_get_business_obj_%s" % (CACHE_PREFIX, cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        info = _get_business_info(request, cc_id, use_cache, use_maintainer)

        obj, created = Business.objects.update_or_create(
            cc_id=info['ApplicationID'],
            defaults={
                'cc_name': info['ApplicationName'],
                'cc_owner': info['Owner'],
                'cc_company': info['DeptName'],
                'time_zone': info.get('TimeZone') or settings.TIME_ZONE,
            }
        )

        data = (obj, created, info)

        cache.set(cache_key, (obj, False, info), DEFAULT_CACHE_TIME_FOR_CC)

    return data


def _update_user_info(info):
    if 'username' in info:
        info['uin'] = info['username']
    if 'nick_name' in info:
        info['first_name'] = info['nick_name']
        info['last_name'] = info['nick_name']
    User = get_user_model()
    User.objects.update_or_create(
        username=info['uin'],
        defaults=info
    )


def update_user_info(request, cc_id, use_cache=True):
    cache_key = "%s_update_user_info_%s" % (CACHE_PREFIX, cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        client = settings.ESB_GET_CLIENT_BY_REQUEST(request)
        auth = getattr(client, settings.ESB_AUTH_COMPONENT_SYSTEM)
        get_user_info = getattr(auth, settings.ESB_AUTH_GET_USER_INFO)
        result = get_user_info({})
        if result['result']:
            _update_user_info(result['data'])
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                settings.ESB_AUTH_COMPONENT_SYSTEM,
                'get_user',
                result.get('detail_message', result['message'])
            )

        cache.set(cache_key, True, DEFAULT_CACHE_TIME_FOR_CC)


def prepare_business(request, cc_id, use_cache=True):
    # first, get the business object
    user = request.user
    if user.is_superuser or is_user_functor(request) or is_user_auditor(request):
        try:
            obj, created, extras = get_business_obj(request, cc_id, use_cache)
        except:
            objs = Business.objects.filter(cc_id=cc_id)
            if not objs.exists():
                raise exceptions.Forbidden()
            obj = objs[0]
            extras = {}
    else:
        obj, created, extras = get_business_obj(request, cc_id, use_cache)

    # then, update business object relationships
    if extras:
        update_relationships(request, obj, extras)

    # update user info (uin and nick name)
    update_user_info(request, cc_id)

    return obj


def prepare_user_business(request, use_cache=True):
    user = request.user
    cache_key = "%s_prepare_user_business_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        data = []
        for _, l in _get_user_business_list(request, use_cache).iteritems():
            for info in l:
                if info["ApplicationName"] == u"资源池":
                    continue
                obj, _ = Business.objects.update_or_create(
                    cc_id=info['ApplicationID'],
                    defaults={
                        'cc_name': info['ApplicationName'],
                        'cc_owner': info['Owner'],
                        'cc_company': info['DeptName'],
                        'time_zone': info.get('TimeZone') or settings.TIME_ZONE,
                    }
                )
                if obj not in data:
                    data.append(obj)

        cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)

    return data


def get_biz_maintainer_info(biz_cc_id, username=''):
    """
    获取当前业务下登录过的运维人员信息，包括 operator和auth_token
    @param biz_cc_id:
    @param username: 当前操作者
    @return: operator   业务运维
    @return: auth_token  业务运维的认证信息
    """
    business = Business.objects.get(cc_id=biz_cc_id)
    role = roles.MAINTAINERS
    group_name = "%s\x00%s" % (biz_cc_id, role)
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist as e:
        logger.error('get_biz_maintainer_info raise error, group[%s] does not exist' % group_name)
        return '', ''
    user_list = group.user_set.order_by('last_login')

    if username:
        user = user_list.filter(username=username)
        if user.exists():
            # 如果操作者就是运维，则首先尝试返回自己的信息
            return username, user[0].auth_token

    if business.executor:
        user = user_list.filter(username=business.executor)
        if user.exists():
            return user[0].username, user[0].auth_token

    operator = ''
    auth_token = ''
    for item in user_list:
        if item.auth_token:
            operator = item.username
            auth_token = item.auth_token
            break

    return operator, auth_token


def get_client_by_user_and_biz_id(username, biz_cc_id):
    """
    @summary: 根据用户和业务获取运维身份的client
    :param username:
    :param biz_cc_id:
    :return:
    """
    # 首先以存在auth_token的运维身份调用接口
    maintainer, __ = get_biz_maintainer_info(biz_cc_id, username)
    if maintainer:
        return settings.ESB_GET_CLIENT_BY_USER(maintainer)

    # 无任何业务的运维auth_token信息，只能以自己身份执行
    return settings.ESB_GET_CLIENT_BY_USER(username)


def time_now_str():
    return timezone.localtime(timezone.now()).strftime('%Y%m%d%H%M%S')


def strftime_with_timezone(utc_time):
    if utc_time:
        return timezone.localtime(utc_time).strftime('%Y-%m-%d %H:%M:%S %z')
    else:
        return ''


def convert_readable_username(username):
    """将用户名转换成昵称"""
    return username


def name_handler(name, max_length):
    """名称处理"""
    # 替换特殊字符
    name_str = re.compile(r'[<>.,;~!@#^&*￥\'\"]+').sub('', name)
    # 长度截取
    return name_str[:max_length]
