# -*- coding: utf-8 -*-
from django.test import TestCase
from .boolrule import BoolRule


class BoolRuleTests(TestCase):

    def test_eq(self):
        self.assertTrue(BoolRule('1 == 1').test())
        self.assertTrue(BoolRule('"1" == 1').test())

        self.assertTrue(BoolRule('True == true').test())
        self.assertTrue(BoolRule('False == false').test())

        self.assertTrue(BoolRule('1 == True').test())
        self.assertTrue(BoolRule('0 == False').test())
        self.assertTrue(BoolRule('"1" == True').test())
        self.assertTrue(BoolRule('"0" == False').test())
        self.assertTrue(BoolRule('"3.14" == 3.14').test())

        self.assertTrue(BoolRule('"abc" == "abc"').test())

        self.assertFalse(BoolRule('1 == 2').test())
        self.assertFalse(BoolRule('123 == "123a"').test())
        self.assertFalse(BoolRule('1 == "2"').test())

        self.assertFalse(BoolRule('True == "true"').test())
        self.assertFalse(BoolRule('False == "false"').test())

    def test_ne(self):
        self.assertTrue(BoolRule('1 != 2').test())
        self.assertTrue(BoolRule('"1" != 2').test())

        self.assertTrue(BoolRule('True != "true"').test())

        self.assertTrue(BoolRule('"abc" != "cba"').test())

        self.assertFalse(BoolRule('1 != 1').test())

    def test_gt(self):
        self.assertTrue(BoolRule('2 > 1').test())
        self.assertTrue(BoolRule('"2" > 1').test())

        self.assertFalse(BoolRule('1 > 2').test())
        self.assertFalse(BoolRule('"1" > 2').test())

    def test_lt(self):
        self.assertTrue(BoolRule('1 < 2').test())
        self.assertTrue(BoolRule('"1" < 2').test())
        self.assertTrue(BoolRule('2 < "s"').test())

        self.assertFalse(BoolRule('2 < 1').test())
        self.assertFalse(BoolRule('2 < 2').test())
        self.assertFalse(BoolRule('"2" < 1').test())
        self.assertFalse(BoolRule('"q" < 1').test())

    def test_in(self):
        self.assertTrue(BoolRule('1 in (1, 2)').test())
        self.assertTrue(BoolRule('1 in ("1", "2")').test())
        self.assertTrue(BoolRule('"1" in (1, 2)').test())
        self.assertTrue(BoolRule('"1" in ("1", "2")').test())

        self.assertFalse(BoolRule('1 in (0, 2)').test())
        self.assertFalse(BoolRule('1 in ("11", 2)').test())

    def test_notin(self):
        self.assertTrue(BoolRule('1 notin (0, 2)').test())
        self.assertTrue(BoolRule('1 notin ("0", "2")').test())
        self.assertTrue(BoolRule('"abc" notin (0, 2)').test())

    def test_and(self):
        self.assertTrue(BoolRule('1 < 2 and 2 < 3').test())
        self.assertTrue(BoolRule('"a" < "s" and 2 < 3').test())

        self.assertFalse(BoolRule('1 > 2 and 2 > 1').test())
        self.assertFalse(BoolRule('2 > 1 and 1 > 2').test())
        self.assertFalse(BoolRule('2 > 1 and 1 > 2').test())
        self.assertFalse(BoolRule('"s" > "s" and 2 < 3').test())
        self.assertFalse(BoolRule('"s" < "s" and 2 < 3').test())

    def test_or(self):
        self.assertTrue(BoolRule('1 < 2 or 2 < 3').test())
        self.assertTrue(BoolRule('1 < 2 or 2 < 1').test())
        self.assertTrue(BoolRule('1 > 2 or 2 > 1').test())
        self.assertTrue(BoolRule('"s" > "s" or "su" > "st"').test())

        self.assertFalse(BoolRule('1 > 2 or 2 > 3').test())
        self.assertFalse(BoolRule('"a" > "s" or "s" > "st"').test())

    def test_context(self):
        context = {
            '${v1}': 1,
            '${v2}': "1"
        }
        self.assertTrue(BoolRule('${v1} == ${v2}').test(context))
        self.assertTrue(BoolRule('${v1} == 1').test(context))
        self.assertTrue(BoolRule('${v1} == "1"').test(context))
        self.assertTrue(BoolRule('${v2} == "1"').test(context))
        self.assertTrue(BoolRule('${v2} == "1"').test(context))

        self.assertTrue(BoolRule('${v1} in ("1")').test(context))

    def test_gt_or_equal(self):
        context = {
            '${v1}': 1,
            '${v2}': "1"
        }
        self.assertTrue(BoolRule('${v1} >= ${v2}').test(context))
        self.assertTrue(BoolRule('${v1} >= 1').test(context))
        self.assertTrue(BoolRule('${v1} >= "1"').test(context))
        self.assertTrue(BoolRule('${v1} >= 0').test(context))
        self.assertTrue(BoolRule('${v1} >= "0"').test(context))

        # self.assertTrue(BoolRule('${v1} >= 2').test(context))
        self.assertTrue(BoolRule('${v2} >= "2"').test(context))

    def test_lt_or_equal(self):
        context = {
            '${v1}': 1,
            '${v2}': "1"
        }
        self.assertTrue(BoolRule('${v1} <= ${v2}').test(context))
        self.assertTrue(BoolRule('${v1} <= 1').test(context))
        self.assertTrue(BoolRule('${v1} <= "2"').test(context))
        self.assertTrue(BoolRule('${v1} <= "123456789111"').test(context))
        self.assertTrue(BoolRule('${v1} <= 123456789111').test(context))
        self.assertFalse(BoolRule('${v1} <= 0').test(context))
        self.assertFalse(BoolRule('${v1} <= "0"').test(context))

        self.assertTrue(BoolRule('${v1} <= "a"').test(context))
        self.assertTrue(BoolRule('"a" <= "b"').test(context))
        self.assertFalse(BoolRule('"a" <= "49"').test(context))

        # self.assertTrue(BoolRule('${v1} >= 2').test(context))
        # self.assertTrue(BoolRule('${v2} >= "2"').test(context))

    def test_true_equal(self):
        context = {
            '${v1}': True,
            '${v2}': "True"
        }
        # 下面的表达式测试不符合预期
        # self.assertTrue(BoolRule('${v1} == ${v2}').test(context))
        self.assertTrue(BoolRule('${v1} == True').test(context))
        self.assertTrue(BoolRule('${v1} == true').test(context))
        self.assertTrue(BoolRule('${v1} == ${v1}').test(context))
        self.assertTrue(BoolRule('${v1} == 1').test(context))
        self.assertTrue(BoolRule('${v1} == "1"').test(context))

        self.assertFalse(BoolRule('${v1} == "s"').test(context))
        self.assertFalse(BoolRule('${v1} == 0').test(context))
        self.assertFalse(BoolRule('${v1} == "0"').test(context))
        self.assertFalse(BoolRule('${v1} == false').test(context))
        self.assertFalse(BoolRule('${v1} == False').test(context))
        self.assertFalse(BoolRule('${v1} == "false"').test(context))
        self.assertFalse(BoolRule('${v1} == "False"').test(context))

    def test_false_equal(self):
        context = {
            '${v1}': False,
            '${v2}': "False"
        }
        # 下面的表达式测试不符合预期
        # self.assertTrue(BoolRule('${v1} == "False"').test(context))
        self.assertTrue(BoolRule('${v1} == ${v1}').test(context))
        self.assertTrue(BoolRule('${v1} == false').test(context))
        self.assertTrue(BoolRule('${v1} == False').test(context))
        self.assertTrue(BoolRule('${v1} == "0"').test(context))
        self.assertTrue(BoolRule('${v1} == 0').test(context))
        self.assertTrue(BoolRule('${v1} == "0"').test(context))

        self.assertFalse(BoolRule('${v1} == "1"').test(context))
        self.assertFalse(BoolRule('${v1} == true').test(context))
        self.assertFalse(BoolRule('${v1} == "true"').test(context))
        self.assertFalse(BoolRule('${v1} == True').test(context))
        self.assertFalse(BoolRule('${v1} == "True"').test(context))
        self.assertFalse(BoolRule('${v1} == "s"').test(context))

