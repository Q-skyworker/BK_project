# -*- coding: utf-8 -*-
from django.apps import AppConfig


class Taskflow3Config(AppConfig):
    name = 'gcloud.taskflow3'
    verbose_name = 'GcloudTaskflow3'

    def ready(self):
        from gcloud.taskflow3.signals.handlers import pipeline_post_save_handler
        from gcloud.taskflow3.signals.dispatch import dispatch_activity_failed
        dispatch_activity_failed()
