# -*- coding: utf-8 -*-
import logging
import re
import os

from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from blueapps.utils.esbclient import get_client_by_request
from gcloud.core.models import Business
from pipeline.conf import settings


logger = logging.getLogger('root')


def cc_get_set_list(request, biz_cc_id):
    """
    @summary: 获取配置平台的业务所有集群列表
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    kwargs = {
        'app_id': biz_cc_id,
    }
    cc_result = client.cc.get_topo_tree_by_app_id(kwargs)
    if not cc_result['result']:
        message = _(u"查询配置平台(CMDB)的业务[app_id=%s]的集群拓扑接口cc.get_topo_tree_by_app_id返回失败: %s") % (
            biz_cc_id, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    set_list = [{
        'value': '0',
        'text': _(u"所有集群(all)"),
    }]
    set_data = cc_result['data'].get('Children', [])
    for _set in set_data:
        set_list.append({
            'value': _set['SetID'],
            'text': _set['SetName']
        })
    return JsonResponse({'result': True, 'data': set_list})


def cc_get_module_name_list(request, biz_cc_id):
    """
    @summary: 获取配置平台的业务所有模块名称列表
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    kwargs = {
        'app_id': biz_cc_id,
    }
    cc_result = client.cc.get_modules(kwargs)
    if not cc_result['result']:
        message = _(u"查询配置平台(CMDB)的业务[app_id=%s]的所有模块接口cc.get_modules返回失败: %s") % (
            biz_cc_id, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    module_name_list = [_(u"所有模块(all)")]
    for mod in cc_result['data']:
        if mod['ModuleName'] not in module_name_list:
            module_name_list.append(mod['ModuleName'])
    module_name_list = [{'value': mod, 'text': mod} for mod in module_name_list]
    return JsonResponse({'result': True, 'data': module_name_list})


def cc_get_plat_id(request, biz_cc_id):
    client = get_client_by_request(request)
    biz = Business.objects.get(cc_id=biz_cc_id)
    cc_owner = biz.cc_owner
    cc_result = client.cc.get_plat_id({'plat_company': biz.cc_company})
    if not cc_result['result']:
        message = _(u"查询配置平台(CMDB)的云区域列表接口cc.get_plat_id返回失败: %s") % (
            biz_cc_id, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    data = []
    for plat in cc_result['data']:
        if 'plat_id' in plat:
            plat_id = plat['plat_id']
            plat_company = plat['plat_company']
            plat_name = plat['plat_name']
        else:
            plat_id = plat['platId']
            plat_company = plat['platCompany']
            plat_name = plat['platName']
        if plat_company == cc_owner:
            data.append({
                'value': plat_id,
                'text': plat_name,
            })
    return JsonResponse({'result': True, 'data': data})


def job_get_job_tasks_by_biz(request, biz_cc_id):
    client = get_client_by_request(request)
    job_result = client.job.get_task({'app_id': biz_cc_id})
    if not job_result['result']:
        message = _(u"查询作业平台(JOB)的作业模板[app_id=%s]接口job.get_task返回失败: %s") % (
            biz_cc_id, job_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)
    task_list = []
    for task in job_result['data']:
        task_list.append({
            'value': task['id'],
            'text': task['name'],
        })
    return JsonResponse({'result': True, 'data': task_list})


def job_get_job_task_detail(request, biz_cc_id, task_id):
    client = get_client_by_request(request)
    job_result = client.job.get_task_detail({'app_id': biz_cc_id,
                                             'task_id': task_id})
    if not job_result['result']:
        message = _(u"查询作业平台(JOB)的作业模板详情[app_id=%s]接口job.get_task_detail返回失败: %s") % (
            biz_cc_id, job_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    job_step_type_name = {
        1: _(u"脚本"),
        2: _(u"文件"),
        4: u"SQL"
    }
    task_detail = job_result['data']
    global_var = []
    steps = []
    for var in task_detail.get('globalVarList', []):
        # 1-字符串，2-IP
        if var['type'] == 1:
            value = var.get('defaultValue', '')
        else:
            value = var.get('ipList', '')
        global_var.append({
            'id': var['id'],
            'name': var['name'],
            'type': var['type'],
            'value': value
        })
    for info in task_detail.get('nmStepBeanList', []):
        # 1-执行脚本，2-传文件，4-传SQL
        steps.append({
            'stepId': info['stepId'],
            'name': info['name'],
            'scriptParams': info.get('scriptParam', ''),
            'account': info.get('account', ''),
            'ipList': '',
            'type': info['type'],
            'type_name': job_step_type_name.get(info['type'], info['type'])
        })
    return JsonResponse({'result': True, 'global_var': global_var, 'steps': steps})


def file_upload(request, biz_cc_id):
    """
    @summary: 本地文件上传
    @param request:
    @param biz_cc_id:
    @return:
    """
    try:
        file_obj = request.FILES['file']
        file_content = file_obj.read()
        file_name = file_obj.name
        file_size = file_obj.size
        # 文件名不能包含中文， 文件大小不能大于500M
        if file_size > 500 * 1024 * 1024:
            message = _(u"文件上传失败， 文件大小超过500M")
            response = JsonResponse({'result': False, 'message': message})
            response.status_code = 400
            return response
        chinese_pattern = ur'[\u4e00-\u9fa5\\/:*?"<>|]'
        if re.compile(chinese_pattern).findall(file_name):
            message = _(u"文件上传失败，文件名不能包含中文和\/:*?\"<>|等特殊字符")
            response = JsonResponse({'result': False, 'message': message})
            response.status_code = 400
            return response
        now_str = timezone.datetime.now().strftime('%Y%m%d%H%M%S')
        bk_path = '%s/USERRES/bkupload/%s/%s/' % (settings.PROJECT_ROOT, biz_cc_id, now_str)
        logger.info(u"/components/query/file_upload file path: %s" % bk_path)
        if not os.path.exists(bk_path):
            os.makedirs(bk_path)
        file_obj = os.open(r'%s%s' % (bk_path, file_name), os.O_WRONLY | os.O_CREAT)
        os.write(file_obj, file_content)
        os.close(file_obj)
        result = {
            'result': True,
            'time_str': now_str,
            'name': file_name,
            'size': file_size,
        }
        return JsonResponse(result)
    except Exception as e:
        logger.error(u"/components/query/file_upload exception, error=%s" % e)
        message = _(u"文件上传失败，路径不合法或者程序异常")
        response = JsonResponse({'result': False, 'message': message})
        response.status_code = 400
        return response
