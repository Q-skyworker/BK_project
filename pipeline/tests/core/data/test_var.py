from django.test import TestCase
from pipeline.core.data import var, context, base
from pipeline import exceptions


class TestPlainVariable(TestCase):
    def test_get(self):
        pv = var.PlainVariable('name', 'value')
        self.assertEqual(pv.get(), 'value')


class TestSpliceVariable(TestCase):
    def setUp(self):
        act_outputs = {
            'act_id_1': {
                'output_1': '${gk_1_1}',
                'output_2': '${gk_1_2}'
            },
            'act_id_2': {
                'output_1': '${gk_2_1}'
            }
        }
        self.context = context.Context(act_outputs)

        class Activity(object):
            pass

        act_1 = Activity()
        act_1.id = 'act_id_1'
        data_1 = base.DataObject({})
        data_1.set_outputs('output_1', 'value_1_1')
        data_1.set_outputs('output_2', 'value_1_2')
        act_1.data = data_1
        self.act_1 = act_1

        self.context_1 = context.Context({})
        self.context_1.variables['${grandparent_key}'] = 'grandparent_value'

    def test_get(self):
        sv = var.SpliceVariable(name='name', value='${gk_1_1}_${gk_1_2}_${key_not_exist}', context=self.context)
        self.context.extract_output(self.act_1)
        self.assertEqual(sv.get(), 'value_1_1_value_1_2_${key_not_exist}')

    def test_object_get(self):
        value = {
            'key1': ['${gk_1_1}_test1', '${gk_1_2}_test2'],
            'key2': {
                'key2_1': '${gk_1_1}_${gk_1_2}_${key_not_exist}'
            }
        }
        sv = var.SpliceVariable(name='name', value=value, context=self.context)
        self.context.extract_output(self.act_1)
        test_value = {
            'key1': ['value_1_1_test1', 'value_1_2_test2'],
            'key2': {
                'key2_1': 'value_1_1_value_1_2_${key_not_exist}'
            }
        }
        self.assertEqual(sv.get(), test_value)


class TestLazyVariable(TestCase):
    def test_init(self):
        class Var(var.LazyVariable):
            code = 'var'
            ref_names = ['k1', 'k2', 'k3']

            def get(self):
                pass

        self.assertRaises(AssertionError, Var, 'name', 'not a dict')
        self.assertRaises(exceptions.InsufficientVariableError, Var, 'name', {'k1': 'v1', 'k2': 'v2'})
        v = Var('name', {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'})
        self.assertEqual(v.k1, 'v1')
        self.assertEqual(v.k2, 'v2')
        self.assertEqual(v.k3, 'v3')
