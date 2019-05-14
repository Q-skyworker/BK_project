# -*- coding: utf-8 -*-

from django.test import TestCase
from pipeline.core.flow.base import SequenceFlow, FlowElement
from pipeline.core.flow.activity import ServiceActivity


class TestSequenceFlow(TestCase):
    def test_sequence_flow(self):
        flow_id = '1'
        source = ServiceActivity(id='1', service=None)
        target = ServiceActivity(id='2', service=None)
        flow = SequenceFlow(flow_id, source, target)
        self.assertTrue(isinstance(flow, FlowElement))
        self.assertEqual(flow_id, flow.id)
        self.assertEqual(source, flow.source)
        self.assertEqual(target, flow.target)
        self.assertEqual(False, flow.is_default)
