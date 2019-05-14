# -*- coding=utf-8 -*-
import requests
import json

from django.http import HttpResponse
from django.conf import settings

from gcloud.core.decorators import check_user_perm_of_business
from gcloud.core.models import Business
from gcloud.tasktmpl3.models import TaskTemplate
from pipeline.utils.uniqid import uniqid
from gcloud.tasktmpl3.sites.utils import draw_pipeline_automatic

# v2 atom id : v3 component code
component_code_v2_to_v3 = {
    'requests': 'bk_http_request'
}

var_type_v2_to_v3 = {
    'simple_input_tag': 'input',
    'simple_textarea_tag': 'textarea',
    'simple_datetime_tag': 'datetime',
    'kendo_numeric_integer': 'int',
    'kendo_numeric_float': 'input',
    'var_ip_picker': 'ip'
}

# v2 tag_code : v3 source tag
source_tag_from_v2 = {
    'requests_url': 'bk_http_request.bk_http_request_url',
    'requests_body': 'bk_http_request.bk_http_request_body',
    'requests_method': 'bk_http_request.bk_http_request_method'
}


@check_user_perm_of_business('manage_business')
def import_v2(request, biz_cc_id):
    return HttpResponse("功能尚未开放")
    result = import_template_data()
    if not result['result']:
        message = u"获取 v2 模板信息失败，请重试"
    else:
        message = u"恭喜您成功迁移%s个模板，请返回标准运维任务流程页面并刷新查看数据" % result['data']
    return HttpResponse(message)


def import_template_data():
    data_url = getattr(settings, 'V2_DATA_URL')
    if not data_url:
        data_url = '%s/o/gcloud/template/export/' % settings.BK_PAAS_HOST

    response = requests.post(data_url, data=json.dumps({
        'key': '___export___v2___template___'
    }))
    resp_data = json.loads(response.content)

    if not response.ok or not resp_data['result']:
        return {'result': False, 'data': 0}

    data_list = resp_data['data']
    template_list = []
    for tmpl in data_list[::-1]:
        default_user = 'admin'
        default_company = 'admin'
        business, __ = Business.objects.get_or_create(
            cc_id=tmpl['biz_cc_id'],
            cc_name=tmpl['biz_cc_name'],
            defaults={
                'cc_owner': default_user,
                'cc_company': default_company,
            }
        )

        stage_data = json.loads(tmpl['stage_data'])
        param_data = json.loads(tmpl['parameters'])
        pipeline_tree = convert_stage_and_params_from_v2_to_v3(stage_data, param_data)

        pipeline_template_kwargs = {
            'name': tmpl['name'],
            'creator': tmpl['creator'],
            'pipeline_tree': pipeline_tree,
            'description': '',
        }
        pipeline_template = TaskTemplate.objects.create_pipeline_template(**pipeline_template_kwargs)
        pipeline_template.editor = tmpl['editor']
        pipeline_template.create_time = tmpl['create_time']
        pipeline_template.edit_time = tmpl['edit_time']
        pipeline_template.save()

        template_list.append(
            TaskTemplate(
                business=business,
                category=tmpl['category'],
                pipeline_template=pipeline_template,
                notify_type=tmpl['default_notify_type'],
                notify_receivers=tmpl['default_notify_receiver'],
                time_out=tmpl['default_time_out_notify_time']
            )
        )

    TaskTemplate.objects.bulk_create(template_list)
    return {'result': True, 'data': len(template_list)}


def convert_stage_and_params_from_v2_to_v3(stage_data, params):
    constants = convert_params_from_v2_to_v3(params)

    pipeline_tree = {
        'start_event': {
            'id': uniqid(),
            'incoming': '',
            'outgoing': '',
            'type': 'EmptyStartEvent',
            'name': '',
        },
        'end_event': {
            'id': uniqid(),
            'incoming': '',
            'outgoing': '',
            'type': 'EmptyEndEvent',
            'name': '',
        },
        'activities': {},
        'gateways': {},
        'flows': {},
        'constants': constants,
        'outputs': []
    }
    last_node = pipeline_tree['start_event']

    for stage in stage_data:
        is_parallel = stage.get('is_parallel')
        step_data = stage['steps']

        if is_parallel:
            flow = {
                'id': uniqid(),
                'source': last_node['id'],
                'target': '',
                'is_default': False,
            }
            last_node['outgoing'] = flow['id']

            parallel_gateway = {
                'id': uniqid(),
                'incoming': flow['id'],
                'outgoing': [],
                'type': 'ParallelGateway',
                'name': '',
            }
            flow['target'] = parallel_gateway['id']
            converge_gateway = {
                'id': uniqid(),
                'incoming': [],
                'outgoing': '',
                'type': 'ConvergeGateway',
                'name': '',
            }

            pipeline_tree['gateways'].update({
                parallel_gateway['id']: parallel_gateway,
                converge_gateway['id']: converge_gateway,
            })
            pipeline_tree['flows'].update({
                flow['id']: flow
            })

            last_node = parallel_gateway

        for step in step_data:
            activity = convert_atom_from_v2_step_to_v3_act(step, constants)
            flow = {
                'id': uniqid(),
                'source': last_node['id'],
                'target': activity['id'],
                'is_default': False,
            }
            activity['incoming'] = flow['id']

            if is_parallel:
                parallel_gateway['outgoing'].append(flow['id'])

                flow2 = {
                    'id': uniqid(),
                    'source': activity['id'],
                    'target': converge_gateway['id'],
                    'is_default': False,
                }
                converge_gateway['incoming'].append(flow2['id'])
                activity['outgoing'] = flow2['id']

                pipeline_tree['flows'].update({
                    flow['id']: flow,
                    flow2['id']: flow2,
                })
            else:
                last_node['outgoing'] = flow['id']
                last_node = activity

                pipeline_tree['flows'].update({
                    flow['id']: flow
                })

            pipeline_tree['activities'].update({
                activity['id']: activity
            })

        if is_parallel:
            last_node = converge_gateway

    flow = {
        'id': uniqid(),
        'source': last_node['id'],
        'target': pipeline_tree['end_event']['id'],
        'is_default': False,
    }
    pipeline_tree['flows'].update({
        flow['id']: flow
    })
    last_node['outgoing'] = flow['id']
    pipeline_tree['end_event']['incoming'] = flow['id']

    # TODO GCS 适配

    return draw_pipeline_automatic(pipeline_tree)


def convert_params_from_v2_to_v3(params):
    constants = {}

    for index, param in enumerate(params):
        key = param['key']
        source_tag = ''
        custom_type = ''
        source_type = ''
        source_info = {}
        value = ''
        hook = False

        if param['source'] == 'from_steps':
            v2_tag_code = param['tag_data']['tag_code']
            value = param['tag_data']['data'][v2_tag_code]['value']
            source_tag = source_tag_from_v2[v2_tag_code]
            source_type = 'component_inputs'

        elif param['source'] == 'manual':
            v2_tag_code = param['tag_data']['tag_code']
            custom_type = var_type_v2_to_v3[v2_tag_code]
            value = param['tag_data']['data'][v2_tag_code]['value']
            source_type = 'custom'
            if v2_tag_code == 'var_ip_picker':
                source_tag = 'var_ip_picker.ip_picker'

        constants.update({
            key: {
                'name': param['name'],
                'key': key,
                'value': value,
                'index': index,
                'custom_type': custom_type,
                'source_tag': source_tag,
                'source_info': source_info,
                'show_type': param['show_type'],
                'source_type': source_type,
                'validation': param['validation'],
                'hook': hook,
                'desc': param['desc']
            }
        })

    return constants


# v2 tag_code : v3 tag code
tag_v2_to_v3 = {
    'requests': {
        'requests_url': 'bk_http_request_url',
        'requests_method': 'bk_http_request_method',
        'requests_body': 'bk_http_request_body'
    },
}


def convert_atom_from_v2_step_to_v3_act(step, constants):
    act_id = uniqid()
    v3_act = {
        'id': act_id,
        'incoming': '',
        'outgoing': '',
        'name': step['step_name'],
        'error_ignorable': bool(step['is_ignore']),
        'optional': bool(step['is_adjust']),
        'type': 'ServiceActivity',
        'loop': 1,
        'component': {
            'code': '',
            'data': {}
        }
    }

    tag_code = step['tag_code']
    component_code = component_code_v2_to_v3.get(tag_code)
    if not component_code:
        raise Exception("unknown tag code: %s" % tag_code)

    data = step['tag_data']['data']
    tag_data = {}

    if tag_code == 'requests':
        mount_constant(act_id, tag_code, data, constants)
        for key, val in data.items():
            hook = True if val['hook'] == 'on' else False
            tag_data[tag_v2_to_v3[tag_code][key]] = {
                'hook': hook,
                'value': val['constant'] if hook else val['value']
            }

    # TODO another tag

    v3_act['component']['code'] = component_code
    v3_act['component']['data'] = tag_data
    return v3_act


def mount_constant(act_id, tag_code, data, constants):
    for key, val in data.items():
        if val['hook'] == 'on':
            constants[val['constant']]['source_info'].update({
                act_id: [tag_v2_to_v3[tag_code][key]]})
