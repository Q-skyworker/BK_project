# -*- coding: utf-8 -*-
from django.conf import settings as django_settings
from pipeline.conf import default_settings


class PipelineSettings(object):

    def __getattr__(self, key):
        if hasattr(django_settings, key):
            return getattr(django_settings, key)

        if hasattr(default_settings, key):
            return getattr(default_settings, key)

        raise AttributeError('Settings object has no attribute %s' % key)


settings = PipelineSettings()
