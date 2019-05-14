# -*- coding: utf-8 -*-

import pickle

from pipeline.conf import settings
from pipeline.core.data import var


def get_object(key):
    pickle_str = settings.redis_inst.get(key)
    if not pickle_str:
        return None
    return pickle.loads(pickle_str)


def set_object(key, obj):
    return settings.redis_inst.set(key, pickle.dumps(obj))


def del_object(key):
    return settings.redis_inst.delete(key)


def set_schedule_data(schedule_id, parent_data):
    set_object('%s_schedule_parent_data' % schedule_id, parent_data)


def get_schedule_parent_data(schedule_id):
    return get_object('%s_schedule_parent_data' % schedule_id)


def delete_parent_data(schedule_id):
    del_object('%s_schedule_parent_data' % schedule_id)


# hydrate data of activity or subprocess

def hydrate_node_data(node):
    """
    替换当前节点的 data 中的变量
    :param node:
    :return:
    """
    data = node.data
    hydrated = hydrate_data(data.get_inputs())
    data.get_inputs().update(hydrated)


def hydrate_data(data):
    hydrated = {}
    for k, v in data.iteritems():
        if issubclass(v.__class__, var.Variable):
            hydrated[k] = v.get()
        else:
            hydrated[k] = v
    return hydrated
