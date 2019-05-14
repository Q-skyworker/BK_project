# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = 'gcloud.core'
    verbose_name = 'GcloudCore'

    def ready(self):
        from gcloud.core.handlers import business_post_save_handler
        if not hasattr(settings, 'REDIS'):
            try:
                from gcloud.core.models import EnvironmentVariables
                settings.REDIS = {
                    'host': EnvironmentVariables.objects.get_var('BKAPP_REDIS_HOST'),
                    'port': EnvironmentVariables.objects.get_var('BKAPP_REDIS_PORT'),
                    'password': EnvironmentVariables.objects.get_var('BKAPP_REDIS_PASSWORD')
                }
            except:
                pass
