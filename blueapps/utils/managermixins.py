# -*- coding: utf-8 -*-

from django.core.exceptions import FieldError
from django.db.models import Count


class ClassificationCountMixin(object):

    def get_choices_fields(self):
        all_fields = self.model._meta.get_fields()
        choices_fields = []
        for field in all_fields:
            if getattr(field, 'choices', None):
                choices_fields.append(field.name)
        return choices_fields

    def get_choices(self, field):
        choices_fields = self.get_choices_fields()
        if field not in choices_fields:
            raise FieldError('Unsupported filed:%s, which should be CharField with property choices')
        return getattr(self.model._meta.get_field(field), 'choices')

    def classified_count(self, conditions=None, field=None):
        queryset = self.all()
        if conditions:
            queryset = self.filter(**conditions)
        total = queryset.count()
        if field is None:
            return {'total': total, 'groups': []}

        choices = self.get_choices(field)
        queryset = queryset.values(field).annotate(value=Count(field)).order_by()
        values = {item[field]: item['value'] for item in queryset}
        groups = []
        for code, name in choices:
            groups.append({
                'code': code,
                'name': name,
                'value': values.get(code, 0)
            })
        return total, groups
