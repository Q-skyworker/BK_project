# -*- coding: utf-8 -*-
from django.conf.urls import patterns

urlpatterns = patterns(
    'gcloud.contrib.audit.views',
    (r'^home/$', 'home'),
)
