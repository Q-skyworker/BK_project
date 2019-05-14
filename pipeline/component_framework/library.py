# -*- coding: utf-8 -*-
from pipeline.exceptions import ComponentNotExistException


class ComponentLibrary(object):
    components = {}

    def __new__(cls, *args, **kwargs):
        if "component_code" not in kwargs:
            component_code = args[0]
        else:
            component_code = kwargs["component_code"]
        if component_code not in cls.components:
            raise ComponentNotExistException('component %s does not exist.' %
                                             component_code)
        return cls.components[component_code]

    @classmethod
    def get_component_class(cls, component_code):
        return cls.components.get(component_code)

    @classmethod
    def get_component(cls, component_code, data_dict):
        return cls.get_component_class(component_code)(data_dict)
