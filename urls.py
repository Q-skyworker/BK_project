# -*- coding: utf-8 -*-
# admin.autodiscover()
from django.conf import settings
from django.conf.urls import include, patterns, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from conf.urls_custom import urlpatterns_custom
from gcloud.core.views import page_not_found

urlpatterns = patterns('',
                       # django后台数据库管理
    url(r'^admin/', include(admin.site.urls)),
                       # 用户账号--不要修改
    url(r'^accounts/', include('account.urls')),
                       # app系统控制（目前只包括功能控制开关，后续可扩展）--不要修改
    url(r'^app_control/', include('app_control.urls')),
)

# app自定义路径
urlpatterns += urlpatterns_custom

if settings.RUN_MODE == 'DEVELOP':
    urlpatterns += patterns('',
        # media
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
    if not settings.DEBUG:
        urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT})
        )

if settings.RUN_MODE in settings.DEBUG_TOOLBAR_RUN_MODE:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

handler404 = page_not_found
