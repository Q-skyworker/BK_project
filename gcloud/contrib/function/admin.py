# -*- coding: utf-8 -*-
from django.contrib import admin

from gcloud.contrib.function import models


@admin.register(models.FunctionTask)
class TaskFlowInstanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'creator', 'create_time', 'claimant', 'claim_time', 'status']
    list_filter = ['status']
    search_fields = ['id', 'task', 'creator', 'claimant']
    raw_id_fields = ['task']
