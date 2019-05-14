# -*- coding: utf-8 -*-

from pipeline.engine.signals import activity_failed
from gcloud.taskflow3.signals.handlers import taskflow_node_failed_handler


def dispatch_activity_failed():
    activity_failed.connect(
        taskflow_node_failed_handler,
        dispatch_uid='_taskflow_node_failed',
    )
