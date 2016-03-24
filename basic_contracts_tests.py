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
        def tnotnone(param):
            pass
        self.assertRaises(ContractError, tnotnone, None)
        tnotnone(1)
        tnotnone(False)
        tnotnone('')
        tnotnone('abc')
        tnotnone([])
        tnotnone([1, 2, 3])

    def test_none(self):
        @contract(param='None')
        def tnone(param):
            pass
        self.assertRaises(ContractError, tnone, 1)
        tnone(None)

    def test_bool(self):
        @contract(param='bool')
        def tbool(param):
            pass
        self.assertRaises(ContractError, tbool, None)
        self.assertRaises(ContractError, tbool, 1)
        tbool(True)
        tbool(False)

    def test_string(self):
        @contract(param='string')
        def tstring(param):
            pass
        self.assertRaises(ContractError, tstring, None)
        self.assertRaises(ContractError, tstring, 1)
        self.assertRaises(ContractError, tstring, [1])
        tstring('foobar')
        tstring('')

    def test_string_with_text(self):
        @contract(param='string with text')
        def tstringtext(param):
            pass
        self.assertRaises(ContractError, tstringtext, None)
        self.assertRaises(ContractError, tstringtext, 1)
        self.assertRaises(ContractError, tstringtext, [1])
        self.assertRaises(ContractError, tstringtext, '')
        tstringtext('foobar')

    def test_not_empty(self):
        @contract(param='not empty')
        def tnotempty(param):
            pass
        self.assertRaises(ContractError, tnotempty, None)
        self.assertRaises(ContractError, tnotempty, 1)
        self.assertRaises(ContractError, tnotempty, '')
        tnotempty('foobar')
        tnotempty([1])

    def test_sorted_list(self):
        @contract(param='sorted')
        def tsorted(param):
            pass
        self.assertRaises(ContractError, tsorted, None)
        self.assertRaises(ContractError, tsorted, 1)
        self.assertRaises(ContractError, tsorted, [2, 1])
        tsorted('')
        tsorted('abc')
        tsorted([])
        tsorted([1, 2, 3])

    def test_any_date(self):
        @contract(param='any date')
        def tanydate(param):
            pass
        self.assertRaises(ContractError, tanydate, None)
        self.assertRaises(ContractError, tanydate, 1)
        self.assertRaises(ContractError, tanydate, '')
        self.assertRaises(ContractError, tanydate, [1])
        tanydate(datetime.now())
        tanydate(date.today())

    def test_any_datetime(self):
        @contract(param='any datetime')
        def tanydatetime(param):
            pass
        self.assertRaises(ContractError, tanydatetime, None)
        self.assertRaises(ContractError, tanydatetime, 1)
        self.assertRaises(ContractError, tanydatetime, '')
        self.assertRaises(ContractError, tanydatetime, [1])
        self.assertRaises(ContractError, tanydatetime, date.today())
        tanydatetime(datetime.now())
