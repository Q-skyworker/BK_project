import re
import copy
from abc import abstractmethod

from pipeline.core.data.context import OutputRef
from pipeline import exceptions
from pipeline.models import VariableModel
from pipeline.core.data import library


CONSTANT_EXP = r'\${[_a-zA-Z][_a-zA-Z0-9]*}'


def resolve_string(string, maps):
    for key, value in maps.iteritems():
        # exit loop when the value is no more a string
        if not isinstance(string, basestring):
            break
        if isinstance(value, (basestring, int, float, long)):
            string = string.replace(key, str(value))
        # value is not a string, check whether the ref is a direct reference
        elif string == key:
            string = value
        # can not reference a object in a string
        elif key in string:
            raise exceptions.ConstantReferenceException('Object Variable:%s cannot referred to %s'
                                                        % (key, string))
    return string


def resolve_data(data, maps):
    if isinstance(data, basestring):
        return resolve_string(data, maps)
    if isinstance(data, list):
        for index, item in enumerate(data):
            data[index] = resolve_data(copy.deepcopy(item), maps)
        return data
    if isinstance(data, tuple):
        ldata = ()
        for index, item in enumerate(data):
            ldata.append(resolve_data(copy.deepcopy(item)), maps)
        return ldata
    if isinstance(data, dict):
        for key, value in data.iteritems():
            data[key] = resolve_data(copy.deepcopy(value), maps)
        return data
    return data


def get_string_reference(pattern, string):
    return re.findall(pattern, string)


def get_data_reference(pattern, data):
    if isinstance(data, basestring):
        return get_string_reference(pattern, data)
    if isinstance(data, (list, tuple)):
        result = []
        for item in data:
            result.extend(get_data_reference(pattern, item))
        return result
    if isinstance(data, dict):
        result = []
        for __, value in data.iteritems():
            result.extend(get_data_reference(pattern, value))
        return result
    return []


class Variable(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @abstractmethod
    def get(self):
        pass


class PlainVariable(Variable):
    def __init__(self, name, value):
        super(PlainVariable, self).__init__(name, value)
        self.name = name
        self.value = value

    def get(self):
        return self.value


class SpliceVariable(Variable):

    def __init__(self, name, value, context):
        super(SpliceVariable, self).__init__(name, value)
        self._value = None
        self._build_reference(context)

    def get(self):
        if not self._value:
            self._resolve()
        return self._value

    def _build_reference(self, context):
        keys = get_data_reference(CONSTANT_EXP, self.value)
        refs = {}
        for key in keys:
            refs[key] = OutputRef(key, context)
        self._refs = refs

    def _resolve(self):
        maps = {}
        for key in self._refs:
            try:
                ref_val = self._refs[key].value
                if issubclass(ref_val.__class__, Variable):
                    ref_val = ref_val.get()
            except exceptions.ReferenceNotExistError:
                continue
            maps[key] = ref_val
        val = resolve_data(self.value, maps)

        self._value = val


class LazyVariableMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(LazyVariableMeta, cls).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, LazyVariableMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Create the class
        new_class = super_new(cls, name, bases, attrs)

        if not new_class.code:
            raise exceptions.ConstantReferenceException("LazyVariable %s: code can't be empty."
                                                        % new_class.__name__)

        obj, created = VariableModel.objects.get_or_create(code=new_class.code,
                                                           defaults={
                                                               'status': __debug__,
                                                           })
        if not created and not obj.status:
            obj.status = True
            obj.save()

        library.VariableLibrary.variables[new_class.code] = new_class

        return new_class


class LazyVariable(SpliceVariable):
    __metaclass__ = LazyVariableMeta

    def __init__(self, name, value, context, pipeline_data):
        super(LazyVariable, self).__init__(name, value, context)
        self.context = context
        self.pipeline_data = pipeline_data

    # variable reference resolve
    def get(self):
        self.value = super(LazyVariable, self).get()
        return self.get_value()

    # get real value by user code
    @abstractmethod
    def get_value(self):
        pass
