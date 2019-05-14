# -*- coding: utf-8 -*-
import redis

from django.apps import AppConfig
from django.conf import settings

from pipeline.core.data.library import VariableLibrary
from pipeline.utils.register import autodiscover_collections


class PipelineConfig(AppConfig):
    name = 'pipeline'
    verbose_name = 'Pipeline'

    def ready(self):
        # auto discover collections
        try:
            autodiscover_collections('variables.collections')
            autodiscover_collections('variables.collections.sites.%s' % settings.RUN_VER)
            from pipeline.models import VariableModel
            VariableModel.objects.exclude(code__in=VariableLibrary.variables.keys()).update(status=False)
        except:
            pass

        # init redis pool
        if hasattr(settings, 'REDIS'):
            pool = redis.ConnectionPool(**settings.REDIS)
            r = redis.Redis(connection_pool=pool)
            settings.redis_inst = r
