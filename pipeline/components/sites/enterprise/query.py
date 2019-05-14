# -*- coding: utf-8 -*-
import importlib
import logging

from pipeline.conf import settings
from django.http import JsonResponse

from blueapps.utils.esbclient import get_client_by_request

atoms_cc = importlib.import_module('pipeline.components.collections.sites.%s.cc' % settings.RUN_VER)

logger = logging.getLogger('root')


def cc_search_object_attribute(request, obj_id, biz_cc_id):
    """
    @summary: 获取对象自定义属性
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    kwargs = {
        'bk_obj_id': obj_id,
    }
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result['result']:
        message = atoms_cc.cc_handle_api_error('cc.search_object_attribute', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    host_property = []
    for item in cc_result['data']:
        if item['editable']:
            host_property.append({
                'value': item['bk_property_id'],
                'text': item['bk_property_name']
            })

    return JsonResponse({'result': True, 'data': host_property})


def cc_format_topo_data(data, obj_id):
    tree_data = []
    for item in data:
        tree_item = {
            'id': item['bk_inst_id'],
            'label': item['bk_inst_name']
        }
        if item['bk_obj_id'] != obj_id and item.get('child'):
            tree_item['children'] = cc_format_topo_data(item['child'], obj_id)
        tree_data.append(tree_item)
    return tree_data


def cc_format_prev_topo_data(data, obj_id):
    tree_data = []
    for item in data:
        if item['bk_obj_id'] != obj_id:
            tree_item = {
                'id': item['bk_inst_id'],
                'label': item['bk_inst_name']
            }
            if item.get('child'):
                tree_item['children'] = cc_format_topo_data(item['child'], obj_id)

            tree_data.append(tree_item)
    return tree_data


def cc_search_topo(request, obj_id, biz_cc_id):
    """
    @summary: 查询对象拓扑
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    kwargs = {
        'bk_biz_id': biz_cc_id
    }
    cc_result = client.cc.search_biz_inst_topo(kwargs)
    if not cc_result['result']:
        message = atoms_cc.cc_handle_api_error('cc.search_biz_inst_topo', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    cc_topo = cc_format_topo_data(cc_result['data'], obj_id)
    return JsonResponse({'result': True, 'data': cc_topo})


def cc_search_prev_topo(request, biz_cc_id):
    """
    @summary: 查询集群上层拓扑树
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    kwargs = {
        'bk_biz_id': biz_cc_id
    }
    cc_result = client.cc.search_biz_inst_topo(kwargs)
    if not cc_result['result']:
        message = atoms_cc.cc_handle_api_error('cc.search_biz_inst_topo', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    prev_topo = cc_format_prev_topo_data(cc_result['data'], 'set')
    return JsonResponse({'result': True, 'data': prev_topo})
