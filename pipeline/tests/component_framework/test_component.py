# -*- coding: utf-8 -*-

from django.test import TestCase

from pipeline.core.flow.activity import Service
from pipeline.component_framework import tag
from pipeline.component_framework.component import Component
from pipeline.component_framework.constant import ConstantPool


class TestComponent(TestCase):
    def setUp(self):
        class CCUpdateHostModuleService(Service):
            def execute(self, data, parent_data):
                pass

        class CCUpdateHostModuleComponent(Component):
            name = u'修改主机所属模块'
            bound_service = CCUpdateHostModuleService
            code = 'cc_update_module'

            cc_host_ip = tag.InputTag(
                tag_code='cc_host_ip',
                name=u'IP地址',
                index=1,
                could_be_hooked=True,
                attributes={
                    'placeholder': u'请输入IP',
                    'required': True,
                },
            )

            cc_plat_id = tag.InputTag(
                tag_code='cc_plat_id',
                name=u'子网名称',
                index=2,
                could_be_hooked=True,
            )

            cc_module = tag.InputTag(
                tag_code='cc_module',
                name=u'迁移到的模块名称',
                index=3,
                could_be_hooked=True,
            )

            def outputs_format(self):
                return {
                    'result': bool,
                    'message': str
                }

            def clean_execute_data(self, context):
                pass

        self.service = CCUpdateHostModuleService
        self.component = CCUpdateHostModuleComponent
        self.tags = {
            'cc_host_ip': CCUpdateHostModuleComponent.cc_host_ip,
            'cc_plat_id': CCUpdateHostModuleComponent.cc_plat_id,
            'cc_module': CCUpdateHostModuleComponent.cc_module
        }

    def test_init(self):
        component = self.component({})
        self.assertEqual(self.tags, component.tags)

    def test_data_for_execution(self):
        data_dict = {
            'cc_host_ip': {
                'hook': False,
                'value': '127.0.0.1'
            },
            'cc_plat_id': {
                'hook': False,
                'value': '1'
            },
            'cc_module': {
                'hook': False,
                'value': '2'
            }
        }
        component = self.component(data_dict)
        do = component.data_for_execution(ConstantPool({}))
        data_dict = {
            'cc_host_ip': '127.0.0.1',
            'cc_plat_id': '1',
            'cc_module': '2'
        }
        self.assertEqual(data_dict, do.get_inputs())
