# -*- coding: utf-8 -*-

import weakref
from abc import ABCMeta, abstractmethod

from pipeline.exceptions import InvalidOperationException


class FlowElement(object):
    __metaclass__ = ABCMeta

    def __init__(self, id, name=None):
        self.id = id
        self.name = name


class FlowNode(FlowElement):
    __metaclass__ = ABCMeta

    def __init__(self, id, name=None, data=None):
        super(FlowNode, self).__init__(id, name)
        self.incoming = SequenceFlowCollection()
        self.outgoing = SequenceFlowCollection()
        self.data = data

    @abstractmethod
    def next(self):
        """
        该节点的下一个节点，由子类来实现
        :return:
        """
        raise NotImplementedError()


class NodeWeakRef(object):
    def __init__(self):
        self._nodes = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        ref = self._nodes.get(instance)
        if not ref:
            return None
        return ref()

    def __set__(self, instance, value):
        if not __debug__ and not issubclass(value.__class__, FlowNode):
            raise TypeError('source and target must be a subclass of FlowNode.')
        self._nodes[instance] = weakref.ref(value)


class SequenceFlow(FlowElement):
    def __init__(self, id, source, target, is_default=False, name=None):
        super(SequenceFlow, self).__init__(id, name)
        self.source = NodeWeakRef()
        self.source = source
        self.target = NodeWeakRef()
        self.target = target
        self.is_default = is_default


class SequenceFlowCollection(object):
    def __init__(self, *flows):
        flow_dict = {}
        for flow in flows:
            flow_dict[flow.id] = flow

        self.flows = list(flows)
        self.flow_dict = flow_dict

    def get_flow(self, id):
        """
        获取 flow.id = id 的某个 flow
        :param id: flow id
        :return:
        """
        return self.flow_dict.get(id)

    def unique_one(self):
        """
        获取唯一的一个 flow，若当前集合内 flow 不只一条则抛出异常
        :return:
        """
        if len(self.flows) != 1:
            raise InvalidOperationException('this collection contains multiple flow, can not get unique one.')
        return self.flows[0]

    def is_empty(self):
        """
        当前集合是否为空
        :return:
        """
        return len(self.flows) == 0

    def default_flow(self):
        """
        获取当前集合中默认的 flow
        :return: 若存在默认的 flow 则返回，否则返回 None
        """
        for flow in self.flows:
            if flow.is_default:
                return flow
        return None

    def add_flow(self, flow):
        """
        向当前结合中添加一条 flow
        :param flow: 待添加的 flow
        :return:
        """
        self.flows.append(flow)
        self.flow_dict[flow.id] = flow

    def all_target_node(self):
        """
        返回当前集合中所有 flow 的 target
        :return:
        """
        nodes = []
        for flow in self.flows:
            nodes.append(flow.target)
        return nodes

    def all_source_node(self):
        """
        返回当前集合中所有 flow 的 source
        :return:
        """
        nodes = []
        for flow in self.flows:
            nodes.append(flow.source)
        return nodes
