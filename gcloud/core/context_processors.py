# -*- coding: utf-8 -*-
"""
context_processor for common(setting)

** 除setting外的其他context_processor内容，均采用组件的方式(string)
"""
from django.utils.translation import ugettext_lazy as _

from bk_api import is_user_functor, is_user_auditor
from common.log import logger
from gcloud.conf import settings
from gcloud.core.models import Business


def get_cur_pos_from_url(request):
    """
    @summary: 返回公共变量给前端导航
    """
    site_url = settings.SITE_URL
    app_path = request.path
    # 首页
    if app_path == site_url:
        cur_pos = ''
    else:
        relative_path = app_path.split(site_url, 1)[1]
        path_list = relative_path.split('/')
        cur_pos = path_list[0]
    return cur_pos


def mysetting(request):
    # 嵌入CICD
    hide_header = request.GET.get('hide_header', '')
    is_maintainer = False
    is_functor = is_user_functor(request)
    is_auditor = is_user_auditor(request)

    if request.resolver_match:
        biz_cc_id = request.resolver_match.kwargs.get('biz_cc_id')
    else:
        biz_cc_id = ''
    biz_cc_name = ''
    if biz_cc_id:
        try:
            biz = Business.objects.get(cc_id=biz_cc_id)
            is_maintainer = request.user.has_perm("manage_business", biz)
            biz_cc_name = biz.cc_name
        except Exception as e:
            logger.error('mysetting get business[biz_cc_id=%s] info error: %s' % (biz_cc_id, e))
    return {
        'MEDIA_URL': settings.MEDIA_URL,                  # MEDIA_URL
        'STATIC_URL': settings.STATIC_URL,                # 本地静态文件访问
        'BK_PAAS_HOST': settings.BK_PAAS_HOST,
        'APP_PATH': request.get_full_path(),              # 当前页面，主要为了login_required做跳转用
        'LOGIN_URL': settings.LOGIN_URL,                           # 登录链接
        'LOGOUT_URL': settings.LOGOUT_URL,                         # 登出链接
        'RUN_MODE': settings.RUN_MODE,                    # 运行模式
        'APP_CODE': settings.APP_CODE,                    # 在蓝鲸系统中注册的  "应用编码"
        'SITE_URL': settings.SITE_URL,                    # URL前缀
        'REMOTE_STATIC_URL': settings.REMOTE_STATIC_URL,  # 远程静态资源url
        'STATIC_VERSION': settings.STATIC_VERSION,        # 静态资源版本号,用于指示浏览器更新缓存
        'BK_URL': settings.BK_URL,                        # 蓝鲸平台URL
        'gettext': _,                                     # 国际化
        '_': _,                                           # 国际化
        'LANGUAGES': settings.LANGUAGES,                  # 国际化

        # 自定义变量
        'RUN_VER': settings.RUN_VER,
        'RUN_VER_NAME': settings.RUN_VER_NAME,
        'REMOTE_ANALYSIS_URL': settings.REMOTE_ANALYSIS_URL,
        'REMOTE_API_URL': settings.REMOTE_API_URL,
        'USERNAME': request.user.username,
        # 'NICK': request.session.get('nick', ''),          # 用户昵称
        'NICK': request.user.username,          # 用户昵称
        'AVATAR': request.session.get('avatar', ''),      # 用户头像
        'CUR_POS': get_cur_pos_from_url(request),
        'BIZ_CC_ID': biz_cc_id,
        'BIZ_CC_NAME': biz_cc_name,
        'HIDE_HEADER': 1 if str(hide_header) == '1' else 0,
        'is_maintainer': 1 if is_maintainer else 0,
        'is_functor': 1 if is_functor else 0,
        'is_auditor': 1 if is_auditor else 0,
    }


def get_constant_settings():
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'LOGIN_URL': settings.LOGIN_URL,
        'LOGOUT_URL': settings.LOGOUT_URL,
        'RUN_MODE': settings.RUN_MODE,                              # 运行模式
        'APP_CODE': settings.APP_CODE,                              # 在蓝鲸系统中注册的  "应用编码"
        'SITE_URL': settings.SITE_URL,                              # URL前缀
        'REMOTE_STATIC_URL': settings.REMOTE_STATIC_URL,            # 远程静态资源url
        'STATIC_VERSION': settings.STATIC_VERSION,                  # 静态资源版本号,用于指示浏览器更新缓存
        'BK_PAAS_HOST': settings.BK_PAAS_HOST,
        'BK_CC_HOST': settings.BK_CC_HOST,
    }
