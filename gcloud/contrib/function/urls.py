# -*- coding: utf-8 -*-
from django.conf.urls import patterns

urlpatterns = patterns(
    'gcloud.contrib.function.views',
    (r'^home/$', 'home'),
)
