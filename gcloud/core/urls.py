# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.contrib.auth.decorators import user_passes_test

from gcloud.core.command import get_cache_key, delete_cache_key


urlpatterns = patterns(
    'gcloud.core.views',
    (r'^$', 'home'),
    (r'^business/home/(?P<biz_cc_id>\d+)/$', 'biz_home'),
    (r'^get_authorized_biz_list/$', 'get_authorized_biz_list'),
    (r'^change_user_default_biz/(?P<biz_cc_id>\d+)/$', 'change_user_default_biz'),
    (r'^get_biz_person_list/(?P<biz_cc_id>\d+)/$', 'get_biz_person_list'),
    (r'^get_task_flow_type/$', 'get_task_flow_type'),
    (r'^set_lang/$', 'set_language'),
)

urlpatterns += patterns(
    'gcloud.core.command',
    (r'^get_cache_key/(?P<key>\w+)/$', user_passes_test(lambda user: user.is_superuser)(get_cache_key)),
    (r'^delete_cache_key/(?P<key>\w+)/$', user_passes_test(lambda user: user.is_superuser)(delete_cache_key)),
)

urlpatterns += patterns(
    '',
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog')
)
