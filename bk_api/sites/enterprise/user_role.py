# -*- coding: utf-8 -*-
from django.core.cache import cache

from common.log import logger
from gcloud.conf import settings


CACHE_PREFIX = __name__.replace('.', '_')
ROLE_MAPS = {
    'functor': '3',
    'auditor': '4'
}


def get_operate_user_list(request):
    """
    获取职能化人员列表
    """
    return get_role_user_list(request, 'functor')


def get_auditor_user_list(request):
    """
    获取职能化人员列表
    """
    return get_role_user_list(request, 'auditor')


def get_role_user_list(request, role):
    if role not in ROLE_MAPS or settings.RUN_VER == 'community':
        return []
    cache_key = "%s_get_%s_user_list" % (CACHE_PREFIX, role)
    user_list = cache.get(cache_key)

    if user_list is None:
        client = settings.ESB_GET_CLIENT_BY_REQUEST(request)
        auth = getattr(client, settings.ESB_AUTH_COMPONENT_SYSTEM)
        result = auth.get_all_user(
            {'role': ROLE_MAPS[role]}
        )
        if result['result']:
            user_list = [user['username'] for user in result['data']]
        else:
            logger.warning('client.%s.get_all_user error: %s' % (
                settings.ESB_AUTH_COMPONENT_SYSTEM,
                result))
            user_list = []
        cache.set(cache_key, user_list, settings.DEFAULT_CACHE_TIME_FOR_AUTH)

    return user_list


def is_user_functor(request):
    """
    判断是否是职能化人员
    """
    return is_user_role(request, 'functor')


def is_user_auditor(request):
    """
    判断是否是审计人员
    """
    return is_user_role(request, 'auditor')


def is_user_role(request, role):
    if role not in ROLE_MAPS or settings.RUN_VER == 'community':
        return False
    cache_key = "%s_is_user_%s_%s" % (CACHE_PREFIX, role, request.user.username)
    is_role = cache.get(cache_key)

    if is_role is None:
        client = settings.ESB_GET_CLIENT_BY_REQUEST(request)
        auth = getattr(client, settings.ESB_AUTH_COMPONENT_SYSTEM)
        get_user_info = getattr(auth, settings.ESB_AUTH_GET_USER_INFO)
        result = get_user_info({})
        if result['result'] and result['data']['role'] == ROLE_MAPS[role]:
            is_role = True
        else:
            is_role = False
        cache.set(cache_key, is_role, settings.DEFAULT_CACHE_TIME_FOR_AUTH)

    return is_role


if __name__ == '__main__':
    test_result = get_operate_user_list()
    print repr(test_result)
