# -*- coding: utf-8 -*-
from pipeline import models
from django.contrib import admin


@admin.register(models.PipelineTemplate)
class PipelineTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'template_id', 'name', 'create_time', 'edit_time']
    list_filter = ['is_deleted']
    search_fields = ['name']
    raw_id_fields = ['snapshot']


@admin.register(models.PipelineInstance)
class PipelineInstanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'template', 'name', 'instance_id', 'create_time', 'start_time', 'finish_time',
                    'is_deleted']
    list_filter = ['is_started', 'is_finished', 'is_deleted']
    search_fields = ['name']
    raw_id_fields = ['template', 'snapshot', 'execution_snapshot']


@admin.register(models.VariableModel)
class VariableModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'status']
    list_filter = ['status']
    search_fields = ['code', 'status']
