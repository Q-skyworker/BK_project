# -*- coding: utf-8 -*-
from django.contrib import admin

from gcloud.taskflow3 import models


@admin.register(models.TaskFlowInstance)
class TaskFlowInstanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'business', 'category', 'create_method', 'flow_type',
                    'current_flow', 'pipeline_instance', 'is_deleted']
    list_filter = ['business', 'category', 'create_method', 'flow_type', 'is_deleted']
    search_fields = ['id', 'pipeline_instance__name', 'create_info']
    raw_id_fields = ['pipeline_instance']
    actions = ['fake_delete']

    def fake_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    fake_delete.short_description = 'Fake delete'
