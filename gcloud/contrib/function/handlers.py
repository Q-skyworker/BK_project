# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.dispatch import receiver

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.signals import taskflow_started, taskflow_finished
from gcloud.contrib.function.models import FunctionTask


@receiver(post_save, sender=TaskFlowInstance)
def function_task_create_handler(sender, instance, created, **kwargs):
    if created and instance.flow_type == 'common_func':
        FunctionTask.objects.create(
            task=instance,
            creator=instance.creator,
        )


@receiver(taskflow_started)
def function_task_started_handler(sender, username, **kwargs):
    if sender.flow_type == 'common_func':
        FunctionTask.objects.filter(task=sender).update(status='executed')


@receiver(taskflow_finished)
def function_task_finished_handler(sender, username, **kwargs):
    if sender.flow_type == 'common_func':
        FunctionTask.objects.filter(task=sender).update(status='finished')


@receiver(post_save, sender=FunctionTask)
def function_task_post_save_handler(sender, instance, created, **kwargs):
    if created:
        # TODO send message to functors to claim task
        pass
