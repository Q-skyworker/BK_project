# -*- coding: utf-8 -*-

from django.conf.urls import url

from pipeline.contrib.web import views_web

urlpatterns = [
    url(r'^$', views_web.home),
    url(r'^template/$', views_web.template),
    url(r'^newtask/$', views_web.newtask),
    url(r'^instance/$', views_web.instance)
]
