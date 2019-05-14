# -*- coding: utf-8 -*-

from abc import ABCMeta
from pipeline.core.flow.base import FlowNode


class Event(FlowNode):
    __metaclass__ = ABCMeta

    def __init__(self, id, name=None, data=None):
        super(Event, self).__init__(id, name, data)

    def next(self):
        return self.outgoing.unique_one().target


class ThrowEvent(Event):
    __metaclass__ = ABCMeta


class CatchEvent(Event):
    __metaclass__ = ABCMeta


class EndEvent(ThrowEvent):
    __metaclass__ = ABCMeta


class StartEvent(CatchEvent):
    __metaclass__ = ABCMeta


class EmptyStartEvent(StartEvent):
    pass


class EmptyEndEvent(EndEvent):
    pass
