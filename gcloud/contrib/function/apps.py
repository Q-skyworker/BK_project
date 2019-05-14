# -*- coding: utf-8 -*-
from django.apps import AppConfig


class FunctionConfig(AppConfig):
    name = 'gcloud.contrib.function'
    verbose_name = 'GcloudContribFunction'

    def ready(self):
        from gcloud.contrib.function.handlers import (
            function_task_create_handler,
            function_task_post_save_handler,
            function_task_started_handler,
            function_task_finished_handler
        )
