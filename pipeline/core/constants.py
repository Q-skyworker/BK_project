# -*- coding: utf-8 -*-


class PipelineElement(object):
    ServiceActivity = 'ServiceActivity'
    SubProcess = 'SubProcess'
    ExclusiveGateway = 'ExclusiveGateway'
    ParallelGateway = 'ParallelGateway'
    ConvergeGateway = 'ConvergeGateway'
    EmptyStartEvent = 'EmptyStartEvent'
    EmptyEndEvent = 'EmptyEndEvent'

    pipeline = 'pipeline'
    start_event = 'start_event'
    end_event = 'end_event'
    activities = 'activities'
    flows = 'flows'
    gateways = 'gateways'
    constants = 'constants'
    incoming = 'incoming'
    outgoing = 'outgoing'
    source = 'source'
    target = 'target'

    location = 'location'
    line = 'line'


PE = PipelineElement()
