# -*- coding: utf-8 -*-
import copy

from pipeline import exceptions
from pipeline.core.data import var, library
from pipeline.component_framework.constant import ConstantPool


def format_web_data_to_pipeline(web_pipeline):
    """
    @summary:
    @param web_pipeline:
    @return:
    """
    pipeline_tree = copy.deepcopy(web_pipeline)
    constants = pipeline_tree.pop('constants')
    constant_pool = {}
    data_inputs = {}
    acts_outputs = {}
    for key, info in constants.iteritems():
        if info['source_tag']:
            var_cls = library.VariableLibrary.get_var_class(info['source_tag'].split('.')[0])
        if info['source_type'] == 'component_outputs':
            source_key = info['source_info'].values()[0][0]
            source_step = info['source_info'].keys()[0]
            data_inputs[key] = {
                'type': 'splice',
                'source_act': source_step,
                'source_key': source_key,
                'value': info['value'],
            }
            acts_outputs.setdefault(source_step, {}).update(
                {
                    source_key: key,
                }
            )
        # 自定义的Lazy类型变量
        elif info['source_tag'] and var_cls and isinstance(var_cls, var.LazyVariable):
            data_inputs[key] = {
                'type': 'lazy',
                'source_tag': info['source_tag'],
                'value': info['value'],
            }
        else:
            constant_pool[key] = info

    pool_obj = ConstantPool(constant_pool)
    resolved_constants = pool_obj.pool
    data_inputs = calculate_constants_type(resolved_constants, data_inputs)
    pipeline_tree['data'] = {
        'inputs': data_inputs,
        'outputs': {key: key for key in pipeline_tree.pop('outputs')},
    }

    for act_id, act in pipeline_tree['activities'].iteritems():
        if act['type'] == 'ServiceActivity':
            act_data = act['component'].pop('data')
            for key, info in act_data.iteritems():
                info['value'] = pool_obj.resolve_value(info['value'])

            all_inputs = calculate_constants_type(act_data,
                                                  data_inputs)
            act['component']['inputs'] = {
                key: value for key, value in all_inputs.iteritems()
                if key in act_data
            }
            act['component']['global_outputs'] = acts_outputs.get(act_id, {})
        elif act['type'] == 'SubProcess':
            act_data = {}
            act_constants = {}
            for key, info in act['pipeline']['constants'].iteritems():
                if info['show_type'] == 'show':
                    info['value'] = pool_obj.resolve_value(info['value'])
                    act_constants[key] = info
                    act_data[key] = info
                else:
                    act_constants[key] = info
            act['pipeline']['constants'] = act_constants
            act['exposed_constants'] = act_data.keys()
            all_inputs = calculate_constants_type(act_data,
                                                  data_inputs)

            act['pipeline'] = format_web_data_to_pipeline(act['pipeline'])
            for key in act['exposed_constants']:
                act['pipeline']['data']['inputs'][key] = all_inputs[key]
        else:
            raise exceptions.FlowTypeError(u"Unknown Activity type: %s" %
                                           act['type'])

    return pipeline_tree


def calculate_constants_type(input_constants, output_constants):
    """
    @summary:
    @param input_constants:
    @param output_constants:
    @return:
    """
    data = copy.deepcopy(output_constants)
    for key, info in input_constants.iteritems():
        ref = var.get_data_reference(var.CONSTANT_EXP, info['value'])
        if ref:
            data.setdefault(key, {
                'type': 'splice',
                'value': info['value'],
            })
        elif info.get('type', 'plain') != 'plain':
            data.setdefault(key, {
                'type': info['type'],
                'value': info['value'],
            })
        else:
            data.setdefault(key, {
                'type': 'plain',
                'value': info['value'],
            })

    return data
