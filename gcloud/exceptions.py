# -*- coding: utf-8 -*-


class Unauthorized(Exception):
    pass


class Forbidden(Exception):
    pass


class NotFound(Exception):
    pass


class APIError(Exception):

    def __init__(self, system, api, message):
        self.system = system
        self.api = api
        self.message = message


class BadTaskOperation(Exception):
    pass


class BadResourceClass(Exception):
    pass
