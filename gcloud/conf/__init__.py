# -*- coding: utf-8 -*-
import datetime
import decimal
import uuid
import json

from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import is_aware
from django.conf import settings as django_settings

from gcloud.conf import default_settings


class GcloudSettings(object):

    def __getattr__(self, key):
        if hasattr(django_settings, key):
            return getattr(django_settings, key)

        if hasattr(default_settings, key):
            return getattr(default_settings, key)

        raise AttributeError('Settings object has no attribute %s' % key)


settings = GcloudSettings()


def default(self, o):
    # See "Date Time String Format" in the ECMA-262 specification.
    if isinstance(o, Promise):
        return force_text(o)
    elif isinstance(o, datetime.datetime):
        r = o.isoformat()
        if o.microsecond:
            r = r[:23] + r[26:]
        if r.endswith('+00:00'):
            r = r[:-6] + 'Z'
        return r
    elif isinstance(o, datetime.date):
        return o.isoformat()
    elif isinstance(o, datetime.time):
        if is_aware(o):
            raise ValueError("JSON can't represent timezone-aware times.")
        r = o.isoformat()
        if o.microsecond:
            r = r[:12]
        return r
    elif isinstance(o, decimal.Decimal):
        return str(o)
    elif isinstance(o, uuid.UUID):
        return str(o)
    else:
        try:
            return super(DjangoJSONEncoder, self).default(o)
        except TypeError as e:
            return str(o)


DjangoJSONEncoder.default = default


def dumps(obj, cls=None, **kwargs):
    if not cls:
        cls = DjangoJSONEncoder
    return json._dumps(obj, cls=cls, **kwargs)


json._dumps = json.dumps
json.dumps = dumps
