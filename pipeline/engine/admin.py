# -*- coding:utf-8 -*-

from django.contrib import admin

from pipeline.engine import models


@admin.register(models.PipelineModel)
class PipelineModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'process']
    search_fields = ['id']
    raw_id_fields = ['process']


@admin.register(models.PipelineProcess)
class PipelineProcessAdmin(admin.ModelAdmin):
    list_display = ['id', 'root_pipeline_id', 'current_node_id', 'destination_id',
                    'parent_id', 'need_ack', 'ack_num', 'is_alive', 'is_sleep']
    search_fields = ['id']
    list_filter = ['is_alive', 'is_sleep']
    raw_id_fields = ['snapshot']


@admin.register(models.Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'state', 'retry', 'skip', 'loop',
                    'created_time', 'started_time', 'archived_time']
    search_fields = ['id']
    list_filter = ['state', 'skip']


@admin.register(models.ScheduleService)
class ScheduleServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'activity_id', 'process_id', 'schedule_times',
                    'wait_callback', 'is_finished']
    search_fields = ['id']
    list_filter = ['wait_callback', 'is_finished']


@admin.register(models.ProcessCeleryTask)
class ProcessCeleryTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'process_id', 'celery_task_id']
    search_fields = ['id', 'process_id']


@admin.register(models.Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ['id', 'inputs', 'outputs', 'ex_data']
    search_fields = ['id']
