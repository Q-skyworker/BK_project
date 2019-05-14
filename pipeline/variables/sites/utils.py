# -*- coding: utf-8 -*-
import importlib

from django.conf import settings

utils = importlib.import_module('pipeline.variables.sites.%s.utils' % settings.RUN_VER)

get_ip_by_zoneid = getattr(utils, 'get_ip_by_zoneid')
