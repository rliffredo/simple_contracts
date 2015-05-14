from datetime import datetime, date

from contracts import new_contract

new_contract('None', lambda x: x is None)
new_contract('bool', lambda x: isinstance(x, bool))
new_contract('string', lambda x: isinstance(x, str))
new_contract('string with text', lambda x: isinstance(x, str) and len(x) > 0)
new_contract('not empty', lambda x: len(x) > 0)


# noinspection PyBroadException
try:
    # IronPython-specific contracts
    from System import DateTime
    new_contract('any date', lambda dt: isinstance(dt, date) or (isinstance(dt, DateTime) and dt.Hour == dt.Minute == dt.Second == 0))
    new_contract('any datetime', lambda dt: isinstance(dt, datetime) or isinstance(dt, DateTime))
except:
    new_contract('any date', lambda dt: isinstance(dt, date))
    new_contract('any datetime', lambda dt: isinstance(dt, datetime))
