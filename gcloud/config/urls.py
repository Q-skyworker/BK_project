# -*- coding: utf-8 -*-
from django.conf.urls import url

from gcloud.config import views, api


urlpatterns = [
    url(r'^home/(?P<biz_cc_id>\d+)/$', views.home),

    url(r'^api/biz_executor/(?P<biz_cc_id>\d+)/$', api.biz_executor),
]
