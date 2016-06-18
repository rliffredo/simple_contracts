from datetime import date, datetime
from unittest import TestCase
from contracts import contract, ContractError
import basic_contracts


# noinspection PyUnusedLocal
class BasicTests(TestCase):

    def setUp(self):
        basic_contracts.setup()

    def test_not_none(self):
        @contract(param='not None')
        def t_not_none(param):
            pass
        self.assertRaises(ContractError, t_not_none, None)
        t_not_none(1)
        t_not_none(False)
        t_not_none('')
        t_not_none('abc')
        t_not_none([])
        t_not_none([1, 2, 3])

    def test_none(self):
        @contract(param='None')
        def t_none(param):
            pass
        self.assertRaises(ContractError, t_none, 1)
        t_none(None)

    def test_bool(self):
        @contract(param='bool')
        def t_bool(param):
            pass
        self.assertRaises(ContractError, t_bool, None)
        self.assertRaises(ContractError, t_bool, 1)
        t_bool(True)
        t_bool(False)

    def test_string(self):
        @contract(param='string')
        def t_string(param):
            pass
        self.assertRaises(ContractError, t_string, None)
        self.assertRaises(ContractError, t_string, 1)
        self.assertRaises(ContractError, t_string, [1])
        t_string('foobar')
        t_string('')

    def test_string_with_text(self):
        @contract(param='string with text')
        def t_string_text(param):
            pass
        self.assertRaises(ContractError, t_string_text, None)
        self.assertRaises(ContractError, t_string_text, 1)
        self.assertRaises(ContractError, t_string_text, [1])
        self.assertRaises(ContractError, t_string_text, '')
        t_string_text('foobar')

    def test_not_empty(self):
        @contract(param='not empty')
        def t_not_empty(param):
            pass
        self.assertRaises(ContractError, t_not_empty, None)
        self.assertRaises(ContractError, t_not_empty, 1)
        self.assertRaises(ContractError, t_not_empty, '')
        t_not_empty('foobar')
        t_not_empty([1])

    def test_sorted_list(self):
        @contract(param='sorted')
        def t_sorted(param):
            pass
        self.assertRaises(ContractError, t_sorted, None)
        self.assertRaises(ContractError, t_sorted, 1)
        self.assertRaises(ContractError, t_sorted, [2, 1])
        t_sorted('')
        t_sorted('abc')
        t_sorted([])
        t_sorted([1, 2, 3])

    def test_any_date(self):
        @contract(param='any date')
        def t_any_date(param):
            pass
        self.assertRaises(ContractError, t_any_date, None)
        self.assertRaises(ContractError, t_any_date, 1)
        self.assertRaises(ContractError, t_any_date, '')
        self.assertRaises(ContractError, t_any_date, [1])
        t_any_date(datetime.now())
        t_any_date(date.today())

    def test_any_datetime(self):
        @contract(param='any datetime')
        def t_any_datetime(param):
            pass
        self.assertRaises(ContractError, t_any_datetime, None)
        self.assertRaises(ContractError, t_any_datetime, 1)
        self.assertRaises(ContractError, t_any_datetime, '')
        self.assertRaises(ContractError, t_any_datetime, [1])
        self.assertRaises(ContractError, t_any_datetime, date.today())
        t_any_datetime(datetime.now())
