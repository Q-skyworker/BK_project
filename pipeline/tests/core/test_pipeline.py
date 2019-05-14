from django.test import TestCase
from pipeline.core.pipeline import *
from pipeline.core.flow.base import SequenceFlow
from pipeline.core.flow.activity import ServiceActivity
from pipeline.core.flow.event import EmptyStartEvent, EmptyEndEvent


class TestPipeline(TestCase):
    def test_node(self):
        start_event = EmptyStartEvent(id='a')
        act = ServiceActivity(id='b', service=None)
        end_event = EmptyEndEvent(id='c')

        flow_ab = SequenceFlow('ab', start_event, act)
        flow_bc = SequenceFlow('bc', act, end_event)

        start_event.outgoing.add_flow(flow_ab)
        act.incoming.add_flow(flow_ab)
        act.outgoing.add_flow(flow_bc)
        end_event.incoming.add_flow(flow_bc)

        spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], None, None)
        pipeline = Pipeline('pipeline', spec)
        self.assertEqual(act, pipeline.node('b'))

    def test_start_event(self):
        start_event = EmptyStartEvent(id='a')
        act = ServiceActivity(id='b', service=None)
        end_event = EmptyEndEvent(id='c')

        flow_ab = SequenceFlow('ab', start_event, act)
        flow_bc = SequenceFlow('bc', act, end_event)

        start_event.outgoing.add_flow(flow_ab)
        act.incoming.add_flow(flow_ab)
        act.outgoing.add_flow(flow_bc)
        end_event.incoming.add_flow(flow_bc)

        spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], None, None)
        pipeline = Pipeline('pipeline', spec)
        self.assertEqual(start_event, pipeline.start_event())

    def test_end_event(self):
        start_event = EmptyStartEvent(id='a')
        act = ServiceActivity(id='b', service=None)
        end_event = EmptyEndEvent(id='c')

        flow_ab = SequenceFlow('ab', start_event, act)
        flow_bc = SequenceFlow('bc', act, end_event)

        start_event.outgoing.add_flow(flow_ab)
        act.incoming.add_flow(flow_ab)
        act.outgoing.add_flow(flow_bc)
        end_event.incoming.add_flow(flow_bc)

        spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], None, None)
        pipeline = Pipeline('pipeline', spec)
        self.assertEqual(end_event, pipeline.end_event())
