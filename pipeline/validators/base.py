# -*- coding: utf-8 -*-
from jsonschema import Draft4Validator

from pipeline import exceptions
from pipeline.validators.schemas import WEB_PIPELINE_SCHEMA
from pipeline.validators.utils import validate_graph_connection, validate_graph_cycle, validate_converge_gateway


def validate_web_pipeline_tree(web_pipeline_tree):
    valid = Draft4Validator(WEB_PIPELINE_SCHEMA)
    errors = []
    for error in sorted(valid.iter_errors(web_pipeline_tree), key=str):
        errors.append('%s: %s' % ('->'.join(error.absolute_path), error.message))
    if errors:
        raise exceptions.ParserWebTreeException(','.join(errors))


def validate_pipeline_tree(pipeline_tree):
    check_connection = validate_graph_connection(pipeline_tree)
    if not check_connection['result']:
        raise exceptions.ParserWebTreeException(check_connection['message'])

    check_cycle = validate_graph_cycle(pipeline_tree)
    if not check_cycle['result']:
        raise exceptions.ParserWebTreeException(check_cycle['message'])

    validate_converge_gateway(pipeline_tree)
