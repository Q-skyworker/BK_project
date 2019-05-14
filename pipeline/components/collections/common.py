# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

import requests
from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component


__group_name__ = _(u"蓝鲸服务(BK)")
logger = logging.getLogger(__name__)


class HttpRequestService(Service):

    def execute(self, data, parent_data):
        method = data.get_one_of_inputs('bk_http_request_method')
        url = data.get_one_of_inputs('bk_http_request_url')
        body = data.get_one_of_inputs('bk_http_request_body')
        other = {

        }

        if method.upper() not in ["GET", "HEAD"]:
            other["data"] = body
            other["headers"] = {'Content-type': 'application/json'}

        try:
            response = requests.request(
                method=method,
                url=url,
                **other
            )
        except Exception as e:
            data.set_outputs('ex_data', _(u"请求异常，详细信息: %s") % e.message)
            return False

        try:
            resp = response.json()
        except:
            data.set_outputs('ex_data', _(u"请求响应数据格式非 JSON"))
            data.set_outputs('status_code', response.status_code)
            return False

        if not (200 <= response.status_code < 300):
            data.set_outputs('ex_data', _(u"请求失败，状态码: %s，响应: %s") % (response.status_code, resp))
            data.set_outputs('status_code', response.status_code)
            return False

        data.set_outputs('data', resp)
        data.set_outputs('status_code', response.status_code)
        return True

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'响应内容'), key='data', type='str'),
            self.OutputItem(name=_(u'状态码'), key='status_code', type='int')
        ]


class HttpComponent(Component):
    name = _(u'HTTP 请求')
    code = 'bk_http_request'
    bound_service = HttpRequestService
    form = settings.STATIC_URL + 'components/atoms/bk/http.js'
