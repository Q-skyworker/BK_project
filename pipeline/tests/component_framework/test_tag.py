from django.test import TestCase

from pipeline.component_framework import tag
from pipeline.exceptions import AttributeMissingError, AttributeValidationError


class TagForTest(tag.Tag):
    type = 'start'

    def required_attributes(self):
        return ['a', 'b', 'c']

    def validate_attributes(self):
        if self.attributes['a'] != 'a':
            return False, 'error'
        return True, ''


class TestTag(TestCase):
    def test_required_attributes(self):
        kwargs = {
            'tag_code': 'cc_host_ip',
            'name': 'IP',
            'index': 1,
            'could_be_hooked': True,
            'attributes': {
                'a': 'a',
                'b': 'b'
            }
        }
        self.assertRaises(AttributeMissingError, TagForTest, **kwargs)
        kwargs['attributes']['c'] = 'c'
        TagForTest(**kwargs)

    def test_validate_attributes(self):
        kwargs = {
            'tag_code': 'cc_host_ip',
            'name': 'IP',
            'index': 1,
            'could_be_hooked': True,
            'attributes': {
                'a': 'b',
                'b': 'b',
                'c': 'c'
            }
        }
        self.assertRaises(AttributeValidationError, TagForTest, **kwargs)
        kwargs['attributes']['a'] = 'a'
        TagForTest(**kwargs)
