# -*- coding: utf-8 -*-
import zlib

try:
    import cPickle as pickle
except Exception:
    import pickle

from django.db import models
from django.utils.translation import ugettext_lazy as _


class IOField(models.BinaryField):
    def __init__(self, compress_level=6, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        value = super(IOField, self).get_prep_value(value)
        return zlib.compress(pickle.dumps(value), self.compress_level)

    def to_python(self, value):
        value = super(IOField, self).to_python(value)
        return pickle.loads(zlib.decompress(value))

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)


class SignalManager(models.Manager):
    def dump(self, module_path, signal_name, kwargs):
        self.create(module_path=module_path, name=signal_name, kwargs=kwargs)


class Signal(models.Model):
    module_path = models.TextField(_(u"信号模块名"))
    name = models.CharField(_(u"信号属性名"), max_length=64)
    kwargs = IOField(verbose_name=_(u"信号参数"))

    objects = SignalManager()
