# -*- coding: utf-8 -*-
'''
@summary: 用户自定义URLconf
'''

from django.conf.urls import patterns, include, url

# 用户自定义 urlconf
urlpatterns_custom = patterns(
    '',
    url(r'^', include('gcloud.core.urls')),
    url(r'^config/', include('gcloud.config.urls')),
    url(r'^apigw/', include('gcloud.apigw.urls')),
    url(r'^template/', include('gcloud.tasktmpl3.urls')),
    url(r'^taskflow/', include('gcloud.taskflow3.urls')),
    url(r'^', include('gcloud.webservice3.urls')),
    url(r'^appmaker/', include('gcloud.contrib.appmaker.urls')),
    url(r'^function/', include('gcloud.contrib.function.urls')),
    url(r'^audit/', include('gcloud.contrib.audit.urls')),
    url(r'^pipeline/', include('pipeline.components.urls')),
)
