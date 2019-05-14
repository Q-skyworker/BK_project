# -*- coding: utf-8 -*-

from django.dispatch import Signal


taskflow_started = Signal(providing_args=['username'])
taskflow_finished = Signal(providing_args=['username'])
