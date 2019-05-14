# -*- coding: utf-8 -*-


class PipelineException(Exception):
    pass


class FlowTypeError(PipelineException):
    pass


class InvalidOperationException(PipelineException):
    pass


class ConditionExhaustedException(PipelineException):
    pass


class EvaluationException(PipelineException):
    pass


class NodeNotExistException(PipelineException):
    pass


class SourceKeyException(NodeNotExistException):
    pass


class VariableHydrateException(PipelineException):
    pass


class ParserException(PipelineException):
    pass


class ParserWebTreeException(ParserException):
    pass

#
# data exception
#


class DataException(PipelineException):
    pass


class DataInitException(DataException):
    pass


class DataAttrException(DataException):
    pass


class DataTypeErrorException(DataException):
    pass


class ConvergeMatchError(DataException):
    def __init__(self, gateway_id, *args):
        self.gateway_id = gateway_id
        super(ConvergeMatchError, self).__init__(*args)


#
# component exception
#

class ComponentException(PipelineException):
    pass


class ComponentDataFormatException(ComponentException):
    pass


class ComponentNotExistException(ComponentException):
    pass


class ComponentDataLackException(ComponentDataFormatException):
    pass


#
# tag exception
#

class PipelineError(StandardError):
    pass


class TagError(PipelineError):
    pass


class AttributeMissingError(TagError):
    pass


class AttributeValidationError(TagError):
    pass


#
# constant exception
#
class ConstantException(PipelineException):
    pass


class ConstantNotExistException(ConstantException):
    pass


class ConstantReferenceException(ConstantException):
    pass


#
# context exception
#
class ContextError(PipelineError):
    pass


class ReferenceNotExistError(ContextError):
    pass


class InsufficientVariableError(ContextError):
    pass
