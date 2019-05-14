# -*- coding: utf-8 -*-
from gcloud.core.constant import TASK_FLOW


APIGW_CREATE_TASK_PARAMS = {
    'type': 'object',
    'required': ['name'],
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 40,
        },
        'flow_type': {
            'type': 'string',
            'enum': TASK_FLOW.keys()
        },
        'constants': {
            'type': 'object',
        },
        'exclude_task_nodes_id': {
            'type': 'array',
        }
    }
}
