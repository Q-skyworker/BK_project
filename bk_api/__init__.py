# -*- coding: utf-8 -*-
import importlib

from django.conf import settings

app_maker = importlib.import_module('bk_api.sites.%s.app_maker' % settings.RUN_VER)
user_role = importlib.import_module('bk_api.sites.%s.user_role' % settings.RUN_VER)

for func_name in ['create_maker_app', 'edit_maker_app', 'del_maker_app']:
    locals()[func_name] = getattr(app_maker, func_name)

for func_name in ['get_operate_user_list', 'get_auditor_user_list', 'is_user_functor', 'is_user_auditor']:
    locals()[func_name] = getattr(user_role, func_name)

__all__ = ['create_maker_app', 'edit_maker_app', 'del_maker_app', 'get_operate_user_list',
           'get_auditor_user_list', 'is_user_functor', 'is_user_auditor']
