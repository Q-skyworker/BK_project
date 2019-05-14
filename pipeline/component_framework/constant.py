# -*- coding: utf-8 -*-
import copy

from pipeline.exceptions import ConstantNotExistException, ConstantReferenceException
from pipeline.core.data.var import CONSTANT_EXP, get_data_reference, resolve_data
from pipeline.utils.graph import Graph


class ConstantPool(object):

    def __init__(self, pool, lazy=False):
        assert isinstance(pool, dict)
        self.raw_pool = pool
        self.pool = None

        if not lazy:
            self.resolve()

    def resolve(self):
        if self.pool:
            return

        refs = self.get_reference_info()

        nodes = refs.keys()
        flows = []
        for node in nodes:
            for ref in refs[node]:
                if ref in nodes:
                    flows.append([node, ref])
        graph = Graph(nodes, flows)
        # circle reference check
        trace = graph.get_cycle()
        if trace:
            raise ConstantReferenceException('Exist circle reference between constants: %s' % '->'.join(trace))

        # resolve the constants reference
        pool = {}
        temp_pool = copy.deepcopy(self.raw_pool)
        # get those constants which are referenced only(not refer other constants)
        referenced_only = ConstantPool._get_referenced_only(temp_pool)
        while temp_pool:
            for ref in referenced_only:
                value = temp_pool[ref]['value']

                # resolve those constants which reference the 'ref'
                for key, info in temp_pool.iteritems():
                    temp_pool[key]['value'] = resolve_data(info['value'], {ref: value})

                pool[ref] = temp_pool[ref]
                temp_pool.pop(ref)
            referenced_only = ConstantPool._get_referenced_only(temp_pool)

        self.pool = pool

    @staticmethod
    def _get_referenced_only(pool):
        referenced_only = []
        for key, info in pool.iteritems():
            reference = [c for c in get_data_reference(CONSTANT_EXP, info['value']) if c in pool]
            if not reference:
                referenced_only.append(key)
        return referenced_only

    def get_reference_info(self, strict=True):
        refs = {}
        for key, info in self.raw_pool.iteritems():
            ref = [c for c in get_data_reference(CONSTANT_EXP, info['value']) if not strict or c in self.raw_pool]
            refs[key] = ref
        return refs

    def resolve_constant(self, constant):
        if not self.pool:
            self.resolve()

        if constant not in self.pool:
            raise ConstantNotExistException('constant %s not exist.' % constant)
        return self.pool[constant]['value']

    def resolve_value(self, val):
        if not self.pool:
            self.resolve()

        maps = {key: self.pool[key]['value'] for key in self.pool}

        return resolve_data(val, maps)
