# -*- coding:utf-8 -*-

from django.contrib import admin

from pipeline.component_framework import models


@admin.register(models.ComponentModel)
class ComponentModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'status']
    search_fields = ['code', 'name']
    list_filter = ['status']
