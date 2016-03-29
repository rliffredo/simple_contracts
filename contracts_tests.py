import sys
from unittest import TestCase

from contracts import SimpleAssertion, SequenceAssertion, MemberAssertion, parse_assertion, ContractParseError, \
    new_contract, ContractError, contract

import contracts


class ParseTest(TestCase):
    @staticmethod
    def _always_true(x):
        return True

    def setUp(self):
        new_contract("test assertion", ParseTest._always_true)

    def check_nested_assertions(self, assertion, assertion_types):
        self.assertIsInstance(assertion, assertion_types[0])
        if assertion_types[1:]:
            self.check_nested_assertions(assertion.internal_assertion, assertion_types[1:])
        else:
            self.assertEqual(assertion.assertion, ParseTest._always_true)

    def test_simple(self):
        res = parse_assertion("test assertion")
        self.assertEqual(res.count(), 1)
        self.check_nested_assertions(res.assertions[0], [SimpleAssertion])

    def test_list(self):
        res = parse_assertion("[test assertion]")
        self.assertEqual(res.count(), 1)
        self.check_nested_assertions(res.assertions[0], [SequenceAssertion, SimpleAssertion])

    def test_member(self):
        res = parse_assertion("member:test assertion")
        self.assertEqual(res.count(), 1)
        self.check_nested_assertions(res.assertions[0], [MemberAssertion, SimpleAssertion])

    def test_member_in_list(self):
        res = parse_assertion("[member:test assertion]")
        self.assertEqual(res.count(), 1)
        self.check_nested_assertions(res.assertions[0], [SequenceAssertion, MemberAssertion,
                                                         SimpleAssertion])

    def test_list_in_member(self):
        res = parse_assertion("member:[test assertion]")
        self.assertEqual(res.count(), 1)
        self.check_nested_assertions(res.assertions[0], [MemberAssertion, SequenceAssertion,
                                                         SimpleAssertion])

    def test_multiple_and_simple(self):
        res = parse_assertion("test assertion, test assertion")
        self.assertEqual(res.count(), 2)
        self.assertTrue(res.all_required)
        self.check_nested_assertions(res.assertions[0], [SimpleAssertion])
        self.check_nested_assertions(res.assertions[1], [SimpleAssertion])

    def test_multiple_and_complex(self):
        res = parse_assertion("[member:test assertion], member:[test assertion]")
        self.assertEqual(res.count(), 2)
        self.assertTrue(res.all_required)
        self.check_nested_assertions(res.assertions[0], [SequenceAssertion, MemberAssertion,
                                                         SimpleAssertion])
        self.check_nested_assertions(res.assertions[1], [MemberAssertion, SequenceAssertion,
                                                         SimpleAssertion])

    def test_multiple_or_simple(self):
        res = parse_assertion("test assertion|test assertion")
        self.assertEqual(res.count(), 2)
        self.assertFalse(res.all_required)
        self.check_nested_assertions(res.assertions[0], [SimpleAssertion])
        self.check_nested_assertions(res.assertions[1], [SimpleAssertion])

    def test_multiple_or_complex(self):
        res = parse_assertion("[member:test assertion]|member:[test assertion]")
        self.assertEqual(res.count(), 2)
        self.assertFalse(res.all_required)
        self.check_nested_assertions(res.assertions[0], [SequenceAssertion, MemberAssertion,
                                                         SimpleAssertion])
        self.check_nested_assertions(res.assertions[1], [MemberAssertion, SequenceAssertion,
                                                         SimpleAssertion])

    def test_cannot_do_and_or(self):
        self.assertRaises(ContractParseError, parse_assertion, "test assertion,test assertion|test assertion")


class ParseActionTest(TestCase):
    def setUp(self):
        new_contract("always true", lambda x: True)
        new_contract("always false", lambda x: False)
        new_contract("pass-through", lambda x: x)

    def test_no_parameter(self):
        res = parse_assertion("always true")
        self.assertTrue(res.check(None))
        res = parse_assertion("always false")
        self.assertFalse(res.check(None))
        res = parse_assertion("[always true]")
        self.assertTrue(res.check([None, None]))
        res = parse_assertion("index:always true")
        self.assertTrue(res.check(""))

    def test_with_param(self):
        res = parse_assertion("[pass-through]")
        self.assertTrue(res.check([True]))
        res = parse_assertion("real:pass-through")
        self.assertTrue(res.check(True))
        res = parse_assertion("[pass-through],[real:pass-through]")
        self.assertTrue(res.check([True]))

    def test_and(self):
        self.assertTrue(parse_assertion("always true,always true").check(None))
        self.assertFalse(parse_assertion("always true,always false").check(None))
        self.assertFalse(parse_assertion("always false,always true").check(None))
        self.assertFalse(parse_assertion("always false,always false").check(None))

    def test_or(self):
        self.assertTrue(parse_assertion("always true|always true").check(None))
        self.assertTrue(parse_assertion("always true|always false").check(None))
        self.assertTrue(parse_assertion("always false|always true").check(None))
        self.assertFalse(parse_assertion("always false|always false").check(None))

    def test_list(self):
        self.assertTrue(parse_assertion("[always true]").check([]))
        self.assertTrue(parse_assertion("[always false]").check([]))
        self.assertFalse(parse_assertion("[always true]").check(None))
        self.assertFalse(parse_assertion("[always true]").check(1))
        self.assertTrue(parse_assertion("[always true]|always true").check(None))
        self.assertFalse(parse_assertion("[always true],always true").check(None))


class IronPythonSpecificTest(TestCase):
    def setUp(self):
        new_contract("always true", lambda x: True)
        self.ironpython = getattr(sys, 'subversion', [None])[0] == 'IronPython'

    def test_enumerable_as_list(self):
        if not self.ironpython:
            return
        from System.Collections.Generic import List
        self.assertTrue(parse_assertion("[always true]").check(List[int]()))


class CheckContractTest(TestCase):
    def setUp(self):
        def f():
            raise Exception("Unstable contract")

        new_contract("int", lambda x: isinstance(x, int))
        new_contract("not empty", lambda x: len(x) > 0)
        new_contract("unstable", lambda x: f())

    def test_single_parameter(self):
        @contract(a='int')
        def f(a):
            return a

        self.assertEqual(f(1), 1)
        self.assertRaises(ContractError, f, 'a')

    def test_exceptions_in_contract(self):
        @contract(a='not empty')
        def f(a):
            return a

        @contract(a='unstable')
        def g(a):
            return a

        self.assertRaises(TypeError, f)
        self.assertRaises(ContractError, f, None)
        self.assertRaises(ContractError, g, None)

    def test_multi_parameters(self):
        @contract(a='int', b='int')
        def f(a, b):
            return a + b

        self.assertEqual(f(1, 2), 3)
        self.assertRaises(ContractError, f, 'a', 'b')
        self.assertRaises(ContractError, f, 1, 'b')
        self.assertRaises(ContractError, f, 'a', 1)

    def test_half_parameters(self):
        @contract(a='int')
        def f(a, b):
            return str(a) + str(b)

        self.assertEqual(f(1, 2), '12')
        self.assertEqual(f(1, 'abc'), '1abc')
        self.assertRaises(ContractError, f, 'a', 'b')
        self.assertRaises(ContractError, f, 'a', 1)

    def test_return_value(self):
        @contract(_returns='int')
        def f(a):
            return a

        self.assertEqual(f(1), 1)
        self.assertRaises(ContractError, f, 'a')

    def test_constraint(self):
        @contract(_constraint='a<b')
        def f(a, b):
            return a + b

        self.assertEqual(f(1, 2), 3)
        self.assertRaises(ContractError, f, 2, 1)

    def test_disabled(self):

        @contract(a='int')
        def f(a):
            return a

        contracts.enabled = False
        self.assertEqual(f(1), 1)
        self.assertEqual(f('a'), 'a')

        contracts.enabled = True
        self.assertEqual(f(1), 1)
        self.assertRaises(ContractError, f, 'a')

    def test_stringlist(self):
        """
        Special case: a string is a sequence; and therefore might still pass
        the "sequence" test.
        """
        new_contract('string', lambda x: isinstance(x, str))
        @contract(a='[string]')
        def f(a):
            return a

        self.assertRaises(ContractError, f, 'a')
        self.assertRaises(ContractError, f, 1)
        self.assertRaises(ContractError, f, {1: 1})
        self.assertRaises(ContractError, f, [1])
        self.assertEqual(f(['a']), ['a'])
        self.assertEqual(f(['a', '']), ['a', ''])
        self.assertEqual(f([]), [])
