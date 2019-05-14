# -*- coding: utf-8 -*-
from pipeline.exceptions import PipelineException


class PipelineEngineException(PipelineException):
    pass


class NodeNotExistException(PipelineEngineException):
    pass


class InvalidOperationException(PipelineEngineException):
    pass
