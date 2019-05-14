# -*- coding: utf-8 -*-
from __future__ import absolute_import

from pipeline.exceptions import PipelineException


class PipelineSpec(object):
    def __init__(self, start_event, end_event, flows, activities, gateways, data, context):
        objects = {
            start_event.id: start_event,
            end_event.id: end_event
        }
        for act in activities:
            objects[act.id] = act
        for gw in gateways:
            objects[gw.id] = gw

        self.start_event = start_event
        self.end_event = end_event
        self.flows = flows
        self.activities = activities
        self.gateways = gateways
        self.data = data
        self.objects = objects
        self.context = context


class Pipeline(object):
    def __init__(self, id, pipeline_spec, parent=None):
        self.id = id
        self.spec = pipeline_spec
        self.parent = parent

    @property
    def data(self):
        return self.spec.data

    def data_for_node(self, node):
        node = self.spec.objects.get(node.id)
        if not node:
            raise PipelineException('Can not find node %s in this pipeline.' % node.id)
        return node.data

    def node(self, id):
        return self.spec.objects.get(id)

    def start_event(self):
        return self.spec.start_event

    def end_event(self):
        return self.spec.end_event

    def context(self):
        return self.spec.context

    def all_nodes(self):
        return self.spec.objects
