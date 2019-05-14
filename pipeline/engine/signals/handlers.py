# -*- coding: utf-8 -*-

from pipeline.engine import tasks
from pipeline.engine.models import ProcessCeleryTask, ScheduleCeleryTask


def pipeline_ready_handler(sender, process_id, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=process_id,
        start_func=tasks.start.apply_async,
        kwargs={
            'args': [process_id]
        }
    )


def child_process_ready_handler(sender, child_id, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=child_id,
        start_func=tasks.dispatch.apply_async,
        kwargs={
            'args': [child_id]
        }
    )


def process_ready_handler(sender, process_id, current_node_id=None, call_from_child=False, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=process_id,
        start_func=tasks.process_wake_up.apply_async,
        kwargs={
            'args': [process_id, current_node_id, call_from_child]
        }
    )


def batch_process_ready_handler(sender, process_id_list, pipeline_id, **kwargs):
    tasks.batch_wake_up.apply_async(args=[process_id_list, pipeline_id])


def wake_from_schedule_handler(sender, process_id, activity_id, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=process_id,
        start_func=tasks.wake_from_schedule.apply_async,
        kwargs={
            'args': [process_id, activity_id]
        }
    )


def process_unfreeze_handler(sender, process_id, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=process_id,
        start_func=tasks.process_unfreeze.apply_async,
        kwargs={
            'args': [process_id]
        }
    )


def schedule_ready_handler(sender, process_id, schedule_id, countdown, **kwargs):
    ScheduleCeleryTask.objects.start_task(
        schedule_id=schedule_id,
        start_func=tasks.service_schedule.apply_async,
        kwargs={
            'args': [process_id, schedule_id],
            'countdown': countdown
        }
    )
