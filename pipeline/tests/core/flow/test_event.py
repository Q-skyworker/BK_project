# -*- coding: utf-8 -*-

from django.test import TestCase
from pipeline.core.flow.event import *


class TestEvent(TestCase):
    def test_event(self):
        event_id = '1'
        event = Event(event_id)
        self.assertTrue(isinstance(event, FlowNode))
        self.assertEqual(event_id, event.id)

    def test_throw_event(self):
        event_id = '1'
        event = ThrowEvent(event_id)
        self.assertTrue(isinstance(event, Event))

    def test_catch_event(self):
        event_id = '1'
        event = CatchEvent(event_id)
        self.assertTrue(isinstance(event, Event))

    def test_start_event(self):
        event_id = '1'
        event = StartEvent(event_id)
        self.assertTrue(isinstance(event, CatchEvent))

    def test_end_event(self):
        event_id = '1'
        event = EndEvent(event_id)
        self.assertTrue(isinstance(event, ThrowEvent))

    def test_empty_start_event(self):
        event_id = '1'
        event = EmptyStartEvent(event_id)
        self.assertTrue(isinstance(event, StartEvent))

    def test_empty_end_event(self):
        event_id = '1'
        event = EmptyEndEvent(event_id)
        self.assertTrue(isinstance(event, EndEvent))

