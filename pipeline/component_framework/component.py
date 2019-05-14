# -*- coding: utf-8 -*-

from pipeline.core.data.base import DataObject
from pipeline.core.data.converter import get_variable
from pipeline.exceptions import ComponentDataLackException
from pipeline.component_framework.base import ComponentMeta


class Component(object):
    __metaclass__ = ComponentMeta

    def __init__(self, data_dict):
        self.data_dict = data_dict

    @classmethod
    def outputs_format(cls):
        outputs = cls.bound_service().outputs()
        outputs = map(lambda oi: oi._asdict(), outputs)
        return outputs

    def clean_execute_data(self, context):
        return self.data_dict

    def data_for_execution(self, context, pipeline_data):
        data_dict = self.clean_execute_data(context)
        inputs = {}

        for key, tag_info in data_dict.iteritems():
            if tag_info is None:
                raise ComponentDataLackException('Lack of inputs: %s' % key)

            inputs[key] = get_variable(key, tag_info, context, pipeline_data)

        return DataObject(inputs)

    def service(self):
        return self.bound_service()
