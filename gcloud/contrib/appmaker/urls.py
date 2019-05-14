# -*- coding: utf-8 -*-
from django.conf.urls import patterns

urlpatterns = patterns(
    'gcloud.contrib.appmaker.views',
    (r'^home/(?P<biz_cc_id>\d+)/$', 'home'),
    # 创建轻应用
    (r'^save_app/(?P<biz_cc_id>\d+)/$', 'save_app'),
    # 删除轻应用
    (r'^del_app/(?P<biz_cc_id>\d+)/$', 'del_app'),

    # 打开一个轻应用，直接进入参数填写阶段
    (r'^(?P<app_id>\d+)/newtask/(?P<biz_cc_id>\d+)/selectnode/$', 'newtask_selectnode'),
    (r'^(?P<app_id>\d+)/newtask/(?P<biz_cc_id>\d+)/paramfill/$', 'newtask_paramfill'),
    # 从轻应用的任务记录跳转到任务详情
    (r'^(?P<app_id>\d+)/execute/(?P<biz_cc_id>\d+)/$', 'execute'),
    # 轻应用中任务列表
    (r'^(?P<app_id>\d+)/task_home/(?P<biz_cc_id>\d+)/$', 'task_home'),
)
