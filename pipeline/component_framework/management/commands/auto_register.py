# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.component import Component
from pipeline.component_framework.models import ComponentModel


class Command(BaseCommand):
    def handle(self, *args, **options):

        for component_code, component_cls in ComponentLibrary.components.iteritems():

            if isinstance(component_cls, type) and issubclass(component_cls, Component):

                # not register ignored component
                ignore = getattr(component_cls, '__register_ignore__', False)
                if ignore:
                    continue

                ComponentModel.objects.get_or_create(
                    code=component_cls.code,
                    defaults={
                        'name': component_cls.name,
                        'status': __debug__,
                    }
                )
