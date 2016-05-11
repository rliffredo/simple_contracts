"""
Basic contracts for general usage:
  - None: fails if parameter is None
  - bool, number, string: fails if parameter is not of the desired type
  - any date: fails if the parameter is not a date (in IronPython, also System.Date)
  - any datetime: fails if the parameter is not a datetime (in IronPython, also System.DateTime)
  - string with text: fails if the parameter is not a string, or if it is an empty string
  - not empty: fails if the parameter is not a container, or the container is empty
  - sorted: fails if the parameter is not a container (or a string!) or its content is not sorted.

See unit tests for more details about the contract meanings.
"""

from datetime import datetime, date
from numbers import Number
from contracts import new_contract
from itertools import tee

try:
    from itertools import izip
except ImportError:
    izip = zip  # In python 3 and above, zip will return an iterator


def pairwise(iterable):
    """
    itertools recipe used for 'sorted' contract
    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def setup():
    # Empty
    new_contract('None', lambda x: x is None)
    new_contract('not None', lambda x: x is not None)
    new_contract('not empty', lambda x: len(x) > 0)
    # Basic types
    new_contract('bool', lambda x: isinstance(x, bool))
    new_contract('number', lambda x: isinstance(x, Number))
    new_contract('string', lambda x: isinstance(x, str))
    new_contract('string with text', lambda x: isinstance(x, str) and len(x.strip()) > 0)
    # Date/time
    new_contract('date', lambda dt: isinstance(dt, date))
    new_contract('datetime', lambda dt: isinstance(dt, datetime))
    try:
        # IronPython-specific contracts
        # noinspection PyUnresolvedReferences
        from System import DateTime
        new_contract('any date',
                     lambda d: isinstance(d, date) or (isinstance(d, DateTime) and d.Hour == d.Minute == d.Second == 0))
        new_contract('any datetime', lambda dt: isinstance(dt, datetime) or isinstance(dt, DateTime))
    except ImportError:
        new_contract('any date', lambda dt: isinstance(dt, date))
        new_contract('any datetime', lambda dt: isinstance(dt, datetime))
    # Others
    new_contract('sorted', lambda l: all((x <= y for x, y in pairwise(l))))
