# -*- coding: utf-8 -*-

from pipeline.core.pipeline import Pipeline
from pipeline.engine import models
from pipeline.engine import signals
from pipeline.engine.signals import handlers


# DISPATCH_UID = __name__.replace('.', '_')


def dispatch_pipeline_ready():
    signals.pipeline_ready.connect(
        handlers.pipeline_ready_handler,
        sender=Pipeline,
        dispatch_uid='_pipeline_ready'
    )


def dispatch_child_process_ready():
    signals.child_process_ready.connect(
        handlers.child_process_ready_handler,
        sender=models.PipelineProcess,
        dispatch_uid='_child_process_ready'
    )


def dispatch_process_ready():
    signals.process_ready.connect(
        handlers.process_ready_handler,
        sender=models.PipelineProcess,
        dispatch_uid='_process_ready'
    )


def dispatch_batch_process_ready():
    signals.batch_process_ready.connect(
        handlers.batch_process_ready_handler,
        sender=models.PipelineProcess,
        dispatch_uid='_batch_process_ready'
    )


def dispatch_wake_from_schedule():
    signals.wake_from_schedule.connect(
        handlers.wake_from_schedule_handler,
        sender=models.ScheduleService,
        dispatch_uid='_wake_from_schedule'
    )


def dispatch_schedule_ready():
    signals.schedule_ready.connect(
        handlers.schedule_ready_handler,
        sender=models.ScheduleService,
        dispatch_uid='_schedule_ready'
    )


def dispatch_process_unfreeze():
    signals.process_unfreeze.connect(
        handlers.process_unfreeze_handler,
        sender=models.PipelineProcess,
        dispatch_uid='_process_unfreeze'
    )


def dispatch():
    dispatch_pipeline_ready()
    dispatch_child_process_ready()
    dispatch_process_ready()
    dispatch_batch_process_ready()
    dispatch_wake_from_schedule()
    dispatch_schedule_ready()
    dispatch_process_unfreeze()
