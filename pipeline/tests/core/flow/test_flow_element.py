# -*- coding: utf-8 -*-

from django.test import TestCase
from pipeline.core.flow.base import FlowElement


class TestBase(TestCase):
    def test_flow_element(self):
        element_id = '1'
        name = 'name'
        flow_element = FlowElement(element_id, name)
        self.assertEqual(element_id, flow_element.id)
        self.assertEqual(name, flow_element.name)
