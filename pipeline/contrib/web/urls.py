# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from tastypie.api import Api

from pipeline.contrib.web.webresource.resource import (PipelineTemplateResource,
                                                       ComponentModelResource,
                                                       PipelineInstanceResource,
                                                       TemplateSchemeResource)
from pipeline.contrib.web import urls_v1, urls_web
from pipeline.components import urls

v1_api = Api(api_name='v1')
v1_api.register(PipelineTemplateResource())
v1_api.register(ComponentModelResource())
v1_api.register(PipelineInstanceResource())
v1_api.register(TemplateSchemeResource())


urlpatterns = [
    url(r'^', include(urls_web)),
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/v1/', include(urls_v1)),
    url(r'^', include(urls)),
]
