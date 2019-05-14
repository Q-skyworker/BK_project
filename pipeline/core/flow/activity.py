# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.base import FlowNode
from collections import namedtuple


def _empty_method(data, parent_data):
    return


class Activity(FlowNode):
    __metaclass__ = ABCMeta

    def __init__(self, id, name=None, data=None, failure_handler=None):
        super(Activity, self).__init__(id, name, data)
        self._failure_handler = failure_handler or _empty_method

    def next(self):
        return self.outgoing.unique_one().target

    def failure_handler(self, parent_data):
        return self._failure_handler(data=self.data, parent_data=parent_data)


class ServiceActivity(Activity):
    result_bit = '_result'

    def __init__(self, id, service, name=None, data=None, error_ignorable=False, failure_handler=None):
        super(ServiceActivity, self).__init__(id, name, data, failure_handler)
        self.service = service
        self.error_ignorable = error_ignorable

    def execute(self, parent_data):
        result = self.service.execute(self.data, parent_data)

        # set result
        self.set_result_bit(result)

        if self.error_ignorable:
            return True
        return result

    def set_result_bit(self, result):
        if result:
            self.data.set_outputs(self.result_bit, True)
        else:
            self.data.set_outputs(self.result_bit, False)

    def skip(self):
        self.set_result_bit(True)
        return True

    def ignore_error(self):
        self.set_result_bit(False)
        return True

    def clear_outputs(self):
        self.data.reset_outputs({})

    def need_schedule(self):
        return getattr(self.service, '__need_schedule__', False)

    def schedule(self, parent_data, callback_data=None):
        result = self.service.schedule(self.data, parent_data, callback_data)
        self.set_result_bit(result)

        if result is False:
            if self.error_ignorable:
                self.service.finish_schedule()
                return True

        return result

    def schedule_done(self):
        return getattr(self.service, '__schedule_finish__', False)

    def shell(self):
        shell = ServiceActivity(id=self.id, service=self.service, name=self.name, data=self.data,
                                error_ignorable=self.error_ignorable)
        return shell


class SubProcess(Activity):
    def __init__(self, id, pipeline, name=None):
        super(SubProcess, self).__init__(id, name, pipeline.data)
        self.pipeline = pipeline


class Service(object):
    __metaclass__ = ABCMeta

    OutputItem = namedtuple('OutputItem', 'name key type')
    interval = None
    _result_output = OutputItem(name=_(u'执行结果'), key='_result', type='bool')

    def __init__(self, name=None):
        self.name = name

    @abstractmethod
    def execute(self, data, parent_data):
        # get params from data
        pass

    @abstractmethod
    def outputs_format(self):
        pass

    def outputs(self):
        custom_format = self.outputs_format()
        assert isinstance(custom_format, list)
        custom_format.append(self._result_output)
        return custom_format

    def schedule(self, data, parent_data, callback_data=None):
        return True

    def finish_schedule(self):
        setattr(self, '__schedule_finish__', True)

    def is_schedule_finished(self):
        return getattr(self, '__schedule_finish__', False)


class AbstractIntervalGenerator(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1


class DefaultIntervalGenerator(AbstractIntervalGenerator):
    def next(self):
        super(DefaultIntervalGenerator, self).next()
        return self.count ** 2


class NullIntervalGenerator(AbstractIntervalGenerator):
    pass


class StaticIntervalGenerator(AbstractIntervalGenerator):
    def __init__(self, interval):
        super(StaticIntervalGenerator, self).__init__()
        self.interval = interval

    def next(self):
        super(StaticIntervalGenerator, self).next()
        return self.interval
