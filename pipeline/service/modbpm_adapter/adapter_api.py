# -*- coding: utf-8 -*-

from modbpm import api

import modbpm_adapter
from pipeline.exceptions import InvalidOperationException
from pipeline.core.data.base import DataObject

TRANSPARENT_PROCESS = ['pipeline.service.modbpm_adapter.SerialProcess']

STATE_MAP = {
    'CREATED': 'RUNNING',
    'READY': 'RUNNING',
    'RUNNING': 'RUNNING',
    'BLOCKED': 'BLOCKED',
    'SUSPENDED': 'SUSPENDED',
    'FINISHED': 'FINISHED',
    'FAILED': 'FAILED',
    'REVOKED': 'REVOKED'
}


def run_pipeline(pipeline, instance_id=None):
    try:
        api.get_model_inst()
        raise InvalidOperationException('This pipeline already started.')
    except:
        pass
    api.create_activity(modbpm_adapter.PipelineProcess, args=(pipeline, instance_id), identifier_code=pipeline.id)


def pause_pipeline(pipeline_id):
    return api.pause_activity(pipeline_id)


def revoke_pipeline(pipeline_id):
    return api.revoke_activity(pipeline_id)


def resume_pipeline(pipeline_id):
    return api.resume_activity(pipeline_id)


def pause_activity(act_id):
    return api.pause_activity(act_id)


def resume_activity(act_id):
    return api.resume_activity(act_id)


def revoke_activity(act_id):
    return api.revoke_activity(act_id)


def retry_activity(act_id, inputs):
    if not inputs:
        api.retry_activity(act_id)
    origin_inputs = api.get_inputs(act_id)
    origin_inputs[0][0].data = DataObject(inputs)
    api.retry_activity(act_id, args=origin_inputs[0])


def skip_activity(act_id):
    api.supersede_activity(act_id, name='pipeline.service.modbpm_adapter.modbpm_adapter.SkipUsingTask')


def get_state(node_id):
    """
    获取某个任务的子任务结构以及其状态
    :param task_id: 任务 ID
    :return: 状态树
    """
    # get all child for atom
    tree = api.get_tree_nodes(node_id, max_depth=100)
    res = {
        'state': _get_node_state(tree),
        'start_time': _better_time_or_none(tree['date_created']),
        'finish_time': _better_time_or_none(tree['date_archived']),
        'retry': len(tree['retries'])
    }

    # collect all atom
    descendants = {}
    _collect_descendants(tree, descendants)
    res['children'] = descendants

    # return
    return res


def _get_node_state(tree):
    status = []

    # return state when meet leaf
    if 'children' not in tree:
        return STATE_MAP[tree['state']]

    # iterate children and get child state recursively
    for identifier_code, child_tree in tree['children'].iteritems():
        status.append(_get_node_state(child_tree))

    # summary parent state
    return STATE_MAP[_get_parent_state_from_children_state(tree['state'], status)]


def _get_parent_state_from_children_state(parent_state, children_state_list):
    """
    @summary: 根据子任务状态计算父任务状态
    @param parent_state:
    @param children_state_list:
    @return:
    """
    if 'RUNNING' in children_state_list:
        parent_state = 'RUNNING'
    else:
        if parent_state == 'BLOCKED':
            if 'FAILED' in children_state_list:
                parent_state = 'FAILED'
            elif 'SUSPENDED' in children_state_list:
                parent_state = 'SUSPENDED'
            else:
                parent_state = 'RUNNING'
    return parent_state


def _collect_descendants(tree, descendants):
    # iterate children for tree
    for identifier_code, child_tree in tree['children'].iteritems():

        # ignore process which user should not concern
        retries = child_tree['retries']
        if child_tree['name'] not in TRANSPARENT_PROCESS:
            child_status = {
                'state': _get_node_state(child_tree),
                'start_time': _better_time_or_none(child_tree['date_created']),
                'finish_time': _better_time_or_none(child_tree['date_archived']),
                'retry': len(retries),
                'name': child_tree['name']
            }
            descendants[identifier_code] = child_status

        # collect children
        if 'children' in child_tree and child_tree['children']:
            _collect_descendants(child_tree, descendants)


def _better_time_or_none(time):
    return time.strftime('%Y-%m-%d %H:%M:%S') if time else time


def get_topo_tree(pipeline_id):
    # TODO waiting for parser
    pass


def get_inputs(act_id):
    return api.get_inputs(act_id)[0][0].data.get_inputs()


def get_outputs(act_id):
    return api.get_inputs(act_id)[0][0].data.get_outputs()
