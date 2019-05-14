# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component

__group_name__ = _(u"测试原子(module)")


class Testservice(Service):
    __need_schedule__ = False

    def execute(self, data, parent_data):
        app_id = data.get_one_of_inputs('app_id')
        data.set_outputs('result', app_id)
        return True

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'执行结果'), key='result', type='str')
        ]


class TestAtom(Component):
    name = _(u'原子测试')
    code = 'test_Atom'
    bound_service = Testservice
    form = settings.STATIC_URL + 'custom_atoms/test/test.js'


