# -*- coding: utf-8 -*-
import importlib

from django.conf import settings

ver_settings = importlib.import_module('gcloud.conf.sites.%s.ver_settings' % settings.RUN_VER)

for _setting in dir(ver_settings):
    if _setting.upper() == _setting:
        locals()[_setting] = getattr(ver_settings, _setting)
