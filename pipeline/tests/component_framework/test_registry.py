from django.test import TestCase

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from pipeline.component_framework.library import ComponentLibrary


class TestRegistry(TestCase):
    def test_component(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = 'name'
            code = 'code'
            bound_service = TestService

        self.assertEqual(ComponentLibrary.components['code'], TestComponent)

    def test_get_component(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = 'name'
            code = 'code'
            bound_service = TestService

            def clean_execute_data(self, context):
                pass

            def outputs_format(self):
                pass

        self.assertEqual(ComponentLibrary.get_component('code', {}).__class__, TestComponent)
