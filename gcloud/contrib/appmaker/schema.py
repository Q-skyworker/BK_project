# -*- coding: utf-8 -*-

APP_MAKER_PARAMS_SCHEMA = {
    'type': 'object',
    'required': ['template_id', 'app_name'],
    'properties': {
        'template_id': {
            'type': 'string',
        },
        'app_name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 20,
        },
    }
}

