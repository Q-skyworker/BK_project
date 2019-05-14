# -*- coding: utf-8 -*-
from importlib import import_module

from pipeline.conf import settings


def get_pipeline_context(obj, obj_type):
    context = {}
    if obj_type == 'template':
        context_path = settings.PIPELINE_TEMPLATE_CONTEXT
    elif obj_type == 'instance':
        context_path = settings.PIPELINE_INSTANCE_CONTEXT
    else:
        return context
    if context_path:
        mod, func = context_path.rsplit('.', 1)
        mod = import_module(mod)
        func = getattr(mod, func)
        context = func(obj)
    if not isinstance(context, dict):
        context = {'data': context}
    return context
