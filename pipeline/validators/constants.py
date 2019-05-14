# -*- coding: utf-8 -*-
MAX_IN = 1000
MAX_OUT = 1000
FLOW_NODES_WITHOUT_STARTEVENT = [
    "ServiceActivity",
    "SubProcess",
    "ExclusiveGateway",
    "ParallelGateway",
    "ConvergeGateway",
    "EmptyEndEvent",
]

# rules of activity graph
ACTIVITY_RULES = {
    "EmptyStartEvent": {
        "min_in": 0,
        "max_in": 0,
        "min_out": 1,
        "max_out": 1,
        "allowed_out": ["ServiceActivity", "ExclusiveGateway", "ParallelGateway", "EmptyEndEvent", "SubProcess"]
    },
    "EmptyEndEvent": {
        "min_in": 1,
        "max_in": MAX_IN,
        "min_out": 0,
        "max_out": 0,
        "allowed_out": []
    },
    "ServiceActivity": {
        "min_in": 1,
        "max_in": 1,
        "min_out": 1,
        "max_out": 1,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT
    },
    "ExclusiveGateway": {
        "min_in": 1,
        "max_in": 1,
        "min_out": 2,
        "max_out": MAX_OUT,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT
    },
    "ParallelGateway": {
        "min_in": 1,
        "max_in": 1,
        "min_out": 2,
        "max_out": MAX_OUT,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT
    },
    "ConvergeGateway": {
        "min_in": 2,
        "max_in": MAX_OUT,
        "min_out": 1,
        "max_out": 1,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT

    },
    "SubProcess": {
        "min_in": 1,
        "max_in": 1,
        "min_out": 1,
        "max_out": 1,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT
    }
}
