# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import query


urlpatterns = [
    url(r'^cc_search_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$', query.cc_search_object_attribute),
    url(r'^cc_search_topo/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$', query.cc_search_topo),
    url(r'^cc_search_prev_topo/(?P<biz_cc_id>\d+)/$', query.cc_search_prev_topo),
]
