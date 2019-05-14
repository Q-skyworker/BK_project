# -*- coding: utf-8 -*-
import importlib

from django.conf.urls import url

from pipeline.conf import settings
from pipeline.components import query

ver_url = importlib.import_module('pipeline.components.sites.%s.urls' % settings.RUN_VER)

urlpatterns = [
    url(r'^cc_get_set_list/(?P<biz_cc_id>\d+)/$', query.cc_get_set_list),
    url(r'^cc_get_module_name_list/(?P<biz_cc_id>\d+)/$', query.cc_get_module_name_list),
    url(r'^cc_get_plat_id/(?P<biz_cc_id>\d+)/$', query.cc_get_plat_id),

    url(r'^job_get_job_tasks_by_biz/(?P<biz_cc_id>\d+)/$', query.job_get_job_tasks_by_biz),
    url(r'^job_get_job_detail_by_biz/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$', query.job_get_job_task_detail),

    url(r'^file_upload/(?P<biz_cc_id>\d+)/$', query.file_upload),
]
urlpatterns += getattr(ver_url, 'urlpatterns', [])
