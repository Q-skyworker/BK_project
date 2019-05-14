# -*- coding: utf-8 -*-
import importlib

from pipeline.conf import settings

adapter_api = importlib.import_module(settings.PIPELINE_ENGINE_ADAPTER_API)


def run_pipeline(pipeline, instance_id=None):
    adapter_api.run_pipeline(pipeline, instance_id)


def pause_pipeline(pipeline_id):
    return adapter_api.pause_pipeline(pipeline_id)


def revoke_pipeline(pipeline_id):
    return adapter_api.revoke_pipeline(pipeline_id)


def resume_pipeline(pipeline_id):
    return adapter_api.resume_pipeline(pipeline_id)


def pause_activity(act_id):
    return adapter_api.pause_activity(act_id)


def resume_activity(act_id):
    return adapter_api.resume_activity(act_id)


def revoke_activity(act_id):
    return adapter_api.revoke_activity(act_id)


def retry_activity(act_id, inputs=None):
    return adapter_api.retry_activity(act_id, inputs=inputs)


def skip_activity(act_id):
    return adapter_api.skip_activity(act_id)


def skip_exclusive_gateway(gateway_id, flow_id):
    return adapter_api.skip_exclusive_gateway(gateway_id, flow_id)


def forced_fail(act_id):
    return adapter_api.forced_fail(act_id)


def get_state(node_id):
    return adapter_api.get_state(node_id)


def get_topo_tree(pipeline_id):
    return adapter_api.get_topo_tree(pipeline_id)


def get_inputs(act_id):
    return adapter_api.get_inputs(act_id)


def get_outputs(act_id):
    return adapter_api.get_outputs(act_id)


def get_activity_histories(act_id):
    return adapter_api.get_activity_histories(act_id)


def callback(act_id, data=None):
    return adapter_api.callback(act_id, data)


def get_single_state(act_id):
    return adapter_api.get_single_state(act_id)
