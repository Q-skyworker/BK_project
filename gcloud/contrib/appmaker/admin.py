# coding=utf-8
from gcloud.contrib.appmaker import models
from django.contrib import admin


@admin.register(models.AppMaker)
class AppMakerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'business', 'task_template', 'is_deleted']
    list_filter = ('business', 'is_deleted')
    search_fields = ['name', 'code']
    raw_id_fields = ['business', 'task_template']
