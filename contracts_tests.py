
from unittest import TestCase

from contracts import SimpleAssertion, ListAssertion, MemberAssertion, parse_assertion, ContractParseError, new_contract, ContractError, contract


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
        self.check_nested_assertions(res.assertions[0], [ListAssertion, SimpleAssertion])

    def test_member(self):
        res = parse_assertion("member:test assertion")
        self.assertEqual(res.count(), 1)
        self.check_nested_assertions(res.assertions[0], [MemberAssertion, SimpleAssertion])

    def test_member_in_list(self):
        res = parse_assertion("[member:test assertion]")
        self.assertEqual(res.count(), 1)
        self.check_nested_assertions(res.assertions[0], [ListAssertion, MemberAssertion,
                                                         SimpleAssertion])

    def test_list_in_member(self):
        res = parse_assertion("member:[test assertion]")
        self.assertEqual(res.count(), 1)
        self.check_nested_assertions(res.assertions[0], [MemberAssertion, ListAssertion,
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
        self.check_nested_assertions(res.assertions[0], [ListAssertion, MemberAssertion,
                                                         SimpleAssertion])
        self.check_nested_assertions(res.assertions[1], [MemberAssertion, ListAssertion,
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
        self.check_nested_assertions(res.assertions[0], [ListAssertion, MemberAssertion,
                                                         SimpleAssertion])
        self.check_nested_assertions(res.assertions[1], [MemberAssertion, ListAssertion,
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
        self.assertFalse(parse_assertion("[always true]").check(None))
        self.assertFalse(parse_assertion("[always true]").check(1))
        self.assertTrue(parse_assertion("[always true]|always true").check(None))
        self.assertFalse(parse_assertion("[always true],always true").check(None))


class CheckContractTest(TestCase):
    def setUp(self):
        new_contract("int", lambda x: isinstance(x, int))

    def test_single_parameter(self):

        @contract(a='int')
        def f(a):
            return a

        self.assertRaises(TypeError, f)
        self.assertEqual(f(1), 1)
        self.assertRaises(ContractError, f, 'a')

    def test_multi_parameters(self):

        @contract(a='int', b='int')
        def f(a, b):
            return a+b

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
            return a+b

        self.assertEqual(f(1, 2), 3)
        self.assertRaises(ContractError, f, 2, 1)
