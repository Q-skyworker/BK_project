# -*- coding: utf-8 -*-

from django.test import TestCase
from pipeline.core.flow.base import FlowNode, SequenceFlow
from pipeline.core.flow.gateway import Gateway, ConvergeGateway, ParallelGateway


class TestConvergeGateway(TestCase):
    def test_converge_gateway(self):
        gw_id = '1'
        cvg_gateway = ConvergeGateway(gw_id)
        self.assertTrue(isinstance(cvg_gateway, FlowNode))
        self.assertTrue(isinstance(cvg_gateway, Gateway))

    def test_next(self):
        cvg_gateway = ConvergeGateway('1')
        parallel_gateway = ParallelGateway('2', 'cvg')
        out_flow = SequenceFlow('flow', cvg_gateway, parallel_gateway)
        cvg_gateway.outgoing.add_flow(out_flow)
        parallel_gateway.incoming.add_flow(out_flow)
        self.assertEqual(parallel_gateway, cvg_gateway.next())


