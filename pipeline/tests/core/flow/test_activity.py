# -*- coding: utf-8 -*-

from django.test import TestCase
from pipeline.core.flow.activity import *


class TestActivity(TestCase):
    def test_base_activity(self):
        act_id = '1'
        base_act = Activity(act_id)
        self.assertTrue(isinstance(base_act, FlowNode))
        self.assertEqual(act_id, base_act.id)

    def test_service_activity(self):
        act_id = '1'
        service = 'a_service'
        inputs = {'args': [1, 2, 3], 'kwargs': {'1': 1, '2': 2}}
        service_act = ServiceActivity(id=act_id, service=service, data=inputs)
        self.assertTrue(isinstance(service_act, Activity))
        self.assertEqual(service, service_act.service)

    def test_subprocess(self):
        act_id = '1'

        class MockPipeline(object):
            def __init__(self, data):
                self.data = data

        pipeline = MockPipeline('data')
        sub_process = SubProcess(act_id, pipeline)
        self.assertTrue(isinstance(sub_process, Activity))
        self.assertEqual(sub_process.data, pipeline.data)
