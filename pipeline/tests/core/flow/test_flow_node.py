# -*- coding: utf-8 -*-

from django.test import TestCase
from pipeline.core.flow.base import FlowNode, FlowElement, SequenceFlowCollection


class MockNode(FlowNode):
    def next(self):
        raise Exception()


class TestFlowNode(TestCase):
    def test_flow_node(self):
        node_id = '1'
        flow_node = MockNode(node_id)
        self.assertTrue(isinstance(flow_node, FlowElement))
        self.assertEqual(node_id, flow_node.id)
        default_collection_node = MockNode(node_id)
        self.assertTrue(isinstance(default_collection_node.incoming, SequenceFlowCollection))
        self.assertTrue(isinstance(default_collection_node.outgoing, SequenceFlowCollection))
