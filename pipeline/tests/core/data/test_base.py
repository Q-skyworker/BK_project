# -*- coding: utf-8 -*-
import unittest

from pipeline.core.data.base import DataObject
from pipeline.core.flow.activity import Activity
from pipeline import exceptions


class TestData(unittest.TestCase):

    def test_data_object(self):
        inputs = {'args': '1', 'kwargs': {'1': 1, '2': 2}}

        self.assertRaises(exceptions.DataTypeErrorException, DataObject, None)

        data_object = DataObject(inputs)
        self.assertIsInstance(data_object, DataObject)

        self.assertEqual(data_object.get_inputs(), inputs)
        self.assertEqual(data_object.get_outputs(), {})

        self.assertEqual(data_object.get_one_of_inputs('args'), '1')
        self.assertIsNone(data_object.get_one_of_outputs('args'))

        self.assertRaises(exceptions.DataTypeErrorException,
                          data_object.reset_outputs, None)
        self.assertTrue(data_object.reset_outputs({'a': str}))

