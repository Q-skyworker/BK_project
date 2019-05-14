# -*- coding: utf-8 -*-
import importlib

from django.conf.urls import url
from django.conf import settings

from gcloud.tasktmpl3 import views, api

import_data = importlib.import_module('gcloud.tasktmpl3.sites.%s.import_data' % settings.RUN_VER)
import_v2_data = importlib.import_module('gcloud.tasktmpl3.sites.%s.import_data_2_to_3' % settings.RUN_VER)

urlpatterns = [
    url(r'^home/(?P<biz_cc_id>\d+)/$', views.home),
    url(r'^newtask/(?P<biz_cc_id>\d+)/selectnode/$', views.newtask_selectnode),
    url(r'^newtask/(?P<biz_cc_id>\d+)/paramfill/$', views.newtask_paramfill),

    url(r'^new/(?P<biz_cc_id>\d+)/$', views.new),
    url(r'^edit/(?P<biz_cc_id>\d+)/$', views.edit),
    url(r'^clone/(?P<biz_cc_id>\d+)/$', views.clone),

    url(r'^api/clone/(?P<biz_cc_id>\d+)/$', api.clone),
    url(r'^api/form/(?P<biz_cc_id>\d+)/$', api.form),
    url(r'^api/collect/(?P<biz_cc_id>\d+)/$', api.collect),
    url(r'^api/get_perms/(?P<biz_cc_id>\d+)/$', api.get_perms),
    url(r'^api/save_perms/(?P<biz_cc_id>\d+)/$', api.save_perms),

    url(r'^get_business_basic_info/(?P<biz_cc_id>\d+)/$', api.get_business_basic_info),

    url(r'^api/import_v1/(?P<biz_cc_id>\d+)/$', import_data.import_v1),
    url(r'^api/import_v2/(?P<biz_cc_id>\d+)/$', import_v2_data.import_v2),
]
