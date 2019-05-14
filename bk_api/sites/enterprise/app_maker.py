# -*- coding: utf-8 -*-
"""
@date: 2014-11-28
@summary: APP Maker api
@note: 本接口只在测试和正式环境下生效
"""
from django.utils.translation import ugettext_lazy as _

from settings import BK_URL
from common.log import logger
from bk_api.utils import http_request_workbench

# 创建APP
CREATE_APP = '%s/paas/api/app_maker/app/create/' % BK_URL
# 修改APP
EDIT_APP = '%s/paas/api/app_maker/app/edit/' % BK_URL
# 删除APP
DEL_APP = '%s/paas/api/app_maker/app/del/' % BK_URL


def create_maker_app(creator, app_name, app_url, developer='', app_tag='', introduction='', add_user='',
                     company_code=''):
    """
    @summary: 创建 maker app
    @param creator：创建者英文id
    @param app_name：app名称
    @param app_url：app链接, 请填写绝对地址
    @param developer: 填写开发者英文id列表，请用英文分号";"隔开
                                只有开发者才有操作该maker app的权限
    @param app_tag: 可选	String	轻应用分类
    @param introduction: 可选	String	轻应用描述
    @param add_user: 可选，目前无效	String	把轻应用自动添加到用户桌面
    @param company_code: 可选，目前无效	String	轻应用所属开发商，一般和creator开发商一致
    @return: {'result': True, 'message':'', 'app_code':app_maker_code}
    {'result': False, 'message':u"APP Maker 创建出错", 'app_code':''}
    """
    try:
        post_param = {
            "creator": creator,
            'app_name': app_name,
            'app_url': app_url,
            'developer': developer,
            'app_tag': app_tag,
            'introduction': introduction,
        }
        resp = http_request_workbench(CREATE_APP, 'POST', post_param)
        return resp
    except Exception as e:
        logger.exception(_(u"调用创建app maker接口失败，错误信息:%s") % e)
        return {'result': False, 'message': _(u"调用创建app maker接口失败"), 'app_code': ''}


def edit_maker_app(operator, app_maker_code, app_name='', app_url='', developer='', app_tag='', introduction='',
                   add_user='', company_code=''):
    """
    @summary: 修改 maker app
    @param operator：操作者英文id
    @param app_maker_code: maker app编码
    @param app_name：app名称,可选参数，为空则不修改名称
    @param app_url：app链接，可选参数，为空则不修改链接
    @param developer: 填写开发者英文id列表，请用英文分号";"隔开, 可选参数，为空则不修改开发者
                                    需传入修改后的所有开发者信息
    @param app_tag: 可选	String	轻应用分类
    @param introduction: 可选	String	轻应用描述
    @param add_user: 可选，目前无效	String	把轻应用自动添加到用户桌面
    @param company_code: 可选，目前无效	String	轻应用所属开发商，一般和creator开发商一致
    @return: {'result': True, 'message':u"APP Maker 修改成功"}
    {'result': False, 'message':u"APP Maker 修改出错"}
    """
    try:
        post_param = {
            "operator": operator,
            'app_maker_code': app_maker_code,
            'app_name': app_name,
            'app_url': app_url,
            'developer': developer,
            'app_tag': app_tag,
            'introduction': introduction,
        }
        resp = http_request_workbench(EDIT_APP, 'POST', post_param)
        return resp
    except Exception as e:
        logger.exception(_(u"调用修改app maker接口失败，错误信息:%s") % e)
        return {'result': False, 'message': _(u"调用修改app maker接口失败")}


def del_maker_app(operator, app_maker_code):
    """
    @summary: 删除 maker app
    @param operator：操作者英文id
    @param app_maker_code: maker app编码
    @return: {'result': True, 'message':u"APP Maker 删除成功"}
    {'result': False, 'message':u"APP Maker 删除失败"}
    """
    try:
        post_param = {
            "operator": operator,
            'app_maker_code': app_maker_code,
        }
        resp = http_request_workbench(DEL_APP, 'POST', post_param)
        return resp
    except Exception as e:
        logger.exception(_(u"调用修改app maker接口失败，错误信息:%s") % e)
        return {'result': False, 'message': _(u"调用修改app maker接口失败")}
