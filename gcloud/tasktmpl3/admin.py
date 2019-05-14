# -*- coding: utf-8 -*-
from django.contrib import admin

from gcloud.tasktmpl3 import models


@admin.register(models.TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'business', 'category', 'pipeline_template', 'is_deleted']
    list_filter = ['business', 'category', 'is_deleted']
    search_fields = ['id', 'pipeline_template__name']
    raw_id_fields = ['pipeline_template']
    actions = ['fake_delete']

    def fake_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    fake_delete.short_description = 'Fake delete'
