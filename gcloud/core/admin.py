# -*- coding: utf-8 -*-
from gcloud.core import models
from django.contrib import admin


@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['cc_id', 'cc_name', 'cc_company', 'executor']
    list_filter = ('cc_company',)
    search_fields = ['cc_name', 'cc_id', 'cc_company']
    editable_fields = ['cc_name', 'cc_id', 'cc_company', 'executor']


@admin.register(models.UserBusiness)
class UserBusinessAdmin(admin.ModelAdmin):
    list_display = ['user', 'default_buss']
    search_fields = ['user', 'default_buss']


@admin.register(models.EnvironmentVariables)
class EnvironmentVariablesAdmin(admin.ModelAdmin):
    list_display = ['key', 'name', 'value']
    search_fields = ['key', 'name']
