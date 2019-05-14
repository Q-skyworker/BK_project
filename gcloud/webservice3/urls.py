# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from gcloud.webservice3.resources import (
    BusinessResource,
    TaskTemplateResource,
    ComponentModelResource,
    TemplateSchemeResource,
    TaskFlowInstanceResource,
    AppMakerResource,
    FunctionTaskResource,
    VariableModelResource
)
from tastypie.api import Api


class JsonApi(Api):

    def top_level(self, request, api_name=None):
        request.META.update(HTTP_ACCEPT="application/json")
        return super(JsonApi, self).top_level(request, api_name)


v3_api = JsonApi(api_name='v3')
v3_api.register(BusinessResource())
v3_api.register(TaskTemplateResource())
v3_api.register(ComponentModelResource())
v3_api.register(VariableModelResource())
v3_api.register(TemplateSchemeResource())
v3_api.register(TaskFlowInstanceResource())
v3_api.register(AppMakerResource())
v3_api.register(FunctionTaskResource())


# Standard bits...
urlpatterns = [
    url(r'^api/', include(v3_api.urls)),
]
