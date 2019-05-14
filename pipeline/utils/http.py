# -*- coding: utf-8 -*-
import json
import logging

import requests

logger = logging.getLogger('root')


def http_post_request(url, data=None, json=None, **kwargs):
    response = requests.post(url, data=data, json=json, **kwargs)
    if response.status_code == 200:
        try:
            content_dict = json.loads(response.content)
            return content_dict
        except Exception as e:
            message = 'the format of HTTP request result is valid: %s' % e
            logger.exception(message)
            return {'result': False, 'code': 1, 'message': message}
    message = u"HTTP request failed，Http status code is：%s" % response.status_code
    logger.error(message)
    return {'result': False, 'code': response.status_code, 'message': message}


def http_get_request(url, params=None, **kwargs):
    response = requests.get(url, params=params, **kwargs)
    if response.status_code == 200:
        try:
            content_dict = json.loads(response.content)
            return content_dict
        except Exception as e:
            message = 'the format of HTTP request result is valid: %s' % e
            logger.exception(message)
            return {'result': False, 'code': 1, 'message': message}
    message = u"HTTP request failed，Http status code is：%s" % response.status_code
    logger.error(message)
    return {'result': False, 'code': response.status_code, 'message': message}
