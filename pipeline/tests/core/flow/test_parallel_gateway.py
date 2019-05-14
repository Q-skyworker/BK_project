# -*- coding: utf-8 -*-

from django.test import TestCase
from pipeline.core.flow.base import FlowNode
from pipeline.core.flow.gateway import Gateway, ParallelGateway
from pipeline.exceptions import InvalidOperationException


class TestParallelGateway(TestCase):
    def test_parallel_gateway(self):
        gw_id = '1'
        pl_gateway = ParallelGateway(gw_id, 'cvg')
        self.assertTrue(isinstance(pl_gateway, FlowNode))
        self.assertTrue(isinstance(pl_gateway, Gateway))

    def test_next(self):
        gw_id = '1'
        pl_gateway = ParallelGateway(gw_id, None, None)
        self.assertRaises(InvalidOperationException, pl_gateway.next)
