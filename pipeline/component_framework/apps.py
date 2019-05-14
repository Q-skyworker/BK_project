# -*- coding: utf-8 -*-
from django.apps import AppConfig

from pipeline.conf import settings
from pipeline.utils.register import autodiscover_collections


class ComponentFrameworkConfig(AppConfig):

    name = 'pipeline.component_framework'
    verbose_name = 'PipelineComponentFramework'

    def ready(self):
        try:
            autodiscover_collections('components.collections')
            autodiscover_collections('components.collections.sites.%s' % settings.RUN_VER)
            from pipeline.component_framework.models import ComponentModel
            from pipeline.component_framework.library import ComponentLibrary
            ComponentModel.objects.exclude(code__in=ComponentLibrary.components.keys()).update(status=False)
        except:
            pass
