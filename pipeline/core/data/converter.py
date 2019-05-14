# -*- coding: utf-8 -*-
from pipeline import exceptions
from pipeline.core.data.var import (PlainVariable,
                                    SpliceVariable,
                                    Variable)
from pipeline.core.data import library


def get_variable(key, info, context, pipeline_data):
    if isinstance(info['value'], Variable):
        variable = info['value']
    else:
        if info.get('type', 'plain') == 'plain':
            variable = PlainVariable(key, info['value'])
        elif info['type'] == 'splice':
            variable = SpliceVariable(key, info['value'], context)
        elif info['type'] == 'lazy':
            variable = library.VariableLibrary.get_var_class(info['source_tag'].split('.')[0])(
                key, info['value'], context, pipeline_data)
        else:
            raise exceptions.DataTypeErrorException(
                'Unknown type: %s, which should be one of [plain, splice, lazy]' % info['type']
            )
    return variable
