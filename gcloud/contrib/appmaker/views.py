# -*- coding: utf-8 -*-
import json

import jsonschema
from django.http.response import HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _

from common.mymako import render_mako_context, render_json
from common.log import logger

from gcloud.conf import settings
from gcloud.core.decorators import check_user_perm_of_business
from gcloud.core.models import Business
from gcloud.core.constant import TASK_CATEGORY
from gcloud.core.utils import _get_user_info
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.appmaker.decorators import check_db_object_exists
from gcloud.contrib.appmaker.schema import APP_MAKER_PARAMS_SCHEMA


def home(request, biz_cc_id):
    """
    @summary: 轻应用
    @param request:
    """
    ctx = {
        'APP_MAKER_MODIFY_LOGO_URL': settings.APP_MAKER_UPLOAD_LOGO_URL,
        'user_uin': settings.APP_MAKER_UPLOAD_LOGO_USER_UIN,
        'user_key': settings.APP_MAKER_UPLOAD_LOGO_USER_KEY,
    }
    return render_mako_context(request, '/appmaker/Light_APP.html', ctx)


@check_user_perm_of_business('manage_business')
def save_app(request, biz_cc_id):
    """
    @summary: 创建或编辑app maker
    @param: task_id: 创建app_maker所选的任务id
            app_id: app_maker_id  判断是新建还是编辑
            app_name:　名称
            app_desc: 简介
    """

    params = request.POST.dict()
    try:
        jsonschema.validate(params, APP_MAKER_PARAMS_SCHEMA)
    except jsonschema.ValidationError as e:
        logger.warning(u"APP_MAKER_PARAMS_SCHEMA raise error: %s" % e)
        message = _(u"任务参数格式错误！")
        return render_json({'res': False, 'msg': message})

    # 获取用户基本信息
    user_info = _get_user_info(request)
    company_code = user_info.get('company_code') or ''

    params.update({
        "username": request.user.username,
        "company_code": company_code,
    })

    # 保存APP maker信息
    template_id = params.pop("template_id")
    app_id = params.get("app_id")
    if app_id == '0':
        app_id = None

    if settings.RUN_MODE == 'PRODUCT':
        params['app_link_prefix'] = settings.APP_MAKER_LINK_PREFIX
        result, data = AppMaker.objects.save_app_maker(
            biz_cc_id, template_id, params, app_id
        )
    elif settings.RUN_MODE == 'TEST':
        params['app_link_prefix'] = settings.TEST_APP_MAKER_LINK_PREFIX
        result, data = AppMaker.objects.save_app_maker(
            biz_cc_id, template_id, params, app_id
        )
    else:
        params['app_link_prefix'] = '%s/' % request.get_host()
        result, data = AppMaker.objects.save_app_maker(
            biz_cc_id, template_id, params, app_id, True
        )

    if not result:
        return render_json({'res': False, 'msg': data})
    app_code = data

    user_uin = request.COOKIES.get(settings.APP_MAKER_UPLOAD_LOGO_USER_UIN, '')
    user_key = request.COOKIES.get(settings.APP_MAKER_UPLOAD_LOGO_USER_KEY, '')
    if not user_uin:
        user_uin = request.GET.get(settings.APP_MAKER_UPLOAD_LOGO_USER_UIN)
        user_key = request.GET.get(settings.APP_MAKER_UPLOAD_LOGO_USER_KEY)

    data = {
             'app_maker_code': app_code,
             'operator': params['username'],
             'user_uin': user_uin if settings.RUN_VER != 'clouds' else params['username'],
             'user_key': user_key,
            }
    return render_json({"res": True, "data": data})


@check_user_perm_of_business('manage_business')
def del_app(request, biz_cc_id):
    """
    @summary: 删除创建的APP maker，将状态置为0
    """
    # 获取用户基本信息
    user_info = _get_user_info(request)
    company_code = user_info.get('company_code') or ''

    app_id = request.POST.get("app_id")
    if app_id == '0':
        app_id = None

    if settings.RUN_MODE in ['PRODUCT', 'TEST']:
        fake = False
    else:
        fake = True
    result, data = AppMaker.objects.del_app_maker(
         biz_cc_id, app_id, company_code, fake
    )
    if not result:
        return render_json({'res': False, 'msg': data})
    return render_json({'res': True, 'data': _(u"删除成功！")})


@check_db_object_exists('AppMaker')
def task_home(request, app_id, biz_cc_id):
    """
    @summary 通过appmaker创建任务
    @param request:
    @param app_id:
    @param biz_cc_id:
    @return:
    """
    business = Business.objects.get(cc_id=biz_cc_id)
    app_maker = AppMaker.objects.get(pk=app_id, business=business)

    ctx = {
        'view_mode': 'appmaker',
        'app_id': app_id,
        'template_id': app_maker.task_template.pk,
    }
    return render_mako_context(request, '/taskflow3/home.html', ctx)


@check_db_object_exists('AppMaker')
def newtask_selectnode(request, app_id, biz_cc_id):
    """
    @summary 通过appmaker创建任务
    @param request:
    @param app_id:
    @param biz_cc_id:
    @return:
    """
    context = {
        # 等于app的时候是在标准运维打开的
        'view_mode': 'appmaker',
        'app_id': app_id,
    }
    return render_mako_context(request, "/core/base_vue.html", context)


@check_db_object_exists('AppMaker')
def newtask_paramfill(request, app_id, biz_cc_id):
    """
    @summary 通过appmaker创建任务
    @param request:
    @param app_id:
    @param biz_cc_id:
    @return:
    """
    context = {
        # 等于app的时候是在标准运维打开的
        'view_mode': 'appmaker',
        'app_id': app_id,
    }
    return render_mako_context(request, "/core/base_vue.html", context)


@check_db_object_exists('AppMaker')
def execute(request, app_id, biz_cc_id):
    """
    @summary: 在轻应用中查看任务详情
    @param request:
    @param app_id:
    @param biz_cc_id:
    @return:
    """
    context = {
        'view_mode': 'appmaker',
        'app_id': app_id,
    }
    return render_mako_context(request, "/core/base_vue.html", context)
