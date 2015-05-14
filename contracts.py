"""
Small module to allow some DBC in python.

Contracts can specify assertions on parameters, on relations between parameters, and the return value.
Assertions on parameters and return value are boolean functions that must be registered before the contract evaluation.
Assertions on relations between parameters instead are just any python expression.

Usage:

    import contracts

    contracts.new_contract('positive int', lambda n: isinstance(n) and n>0)
    @contracts.contract(a='positive int', b='positive int', _returns='positive int', _constraint='a<b')
    def f(a, b):
        return a+b

Assertion syntax:
  1. A basic assertion is just a reference to a contract defined with new_contract
  2. Assertions may be surrounded by [] to state the assertion is on all items of the enumerable
  3. They can also be preceded by 'name:' to state that the assertion is on a member
  4. It is possible to nest the two points before in any way
  5. Several assertions can be chained with ',', meaning they need all to be satisfied
  6. As well, '|' can be used to state alternative paths. This can't be used together with ','.

Example assertions:
  - p='positive int'                                p satisfies contract 'positive int'
  - p='[positive int]'                              p is a sequence of items all satisfying the contract 'positive int'
  - p='member:positive int'                         p is an object with a member satisfying the contract 'positive int'
  - p='[member:positive int]'                       p is a sequence of objects, all with a member satisfying the
                                                    contract 'positive int'
  - p='member1:positive int,member2:negative int'   p is an object, with member1 satisfying contract 'positive int' and
                                                    member2 satisfying contract 'negative int'
  - p='positive int|negative int'                   p satisfies any of contracts 'positive int' and 'negative int'
"""

import inspect
import re

from decorator import decorator


def contract(**assertion_list):
    # Create the assertion list...
    parameter_assertions = {}  # param_name -> ContractAssertion
    constraint = None
    returns = None
    for param_name in assertion_list.keys():
        if param_name == '_constraint':
            constraint = assertion_list[param_name]
        elif param_name == '_returns':
            returns = parse_assertion(assertion_list[param_name])
        else:
            parameter_assertions[param_name] = parse_assertion(assertion_list[param_name])

    def _contract(f, *args, **kwargs):
        # retrieve all parameters
        bound_parameters = inspect.getcallargs(f, *args, **kwargs)
        # bound: {'a': 1, 'b': 2}
        for param in bound_parameters.keys():
            if param in parameter_assertions.keys() and not parameter_assertions[param].check(bound_parameters[param]):
                raise ContractError("Broken contract for parameter %s in function %s" % (param, f.__name__))
        # Check general constraints
        if constraint is not None and not eval(constraint, bound_parameters):
            raise ContractError("Broken contract for general constraint '%s' in function %s" % (constraint, f.__name__))
        ret = f(*args, **kwargs)
        if returns is not None and not returns.check(ret):
            raise ContractError('Broken contract for return value of function %s' % f.__name__)
        return ret
    return decorator(_contract)


def new_contract(name, assertion):
    _defined_contracts[name] = assertion

_defined_contracts = {}


class ContractError(Exception):
    pass


class ContractParseError(Exception):
    pass


class ContractAssertion(object):
    def __init__(self, parsed_assertions, all_required):
        self.all_required = all_required
        self.assertions = parsed_assertions

    def check(self, param):
        check_assertions = all if self.all_required else any
        return check_assertions(a.check(param) for a in self.assertions)

    def count(self):
        return len(self.assertions)


class SimpleAssertion(object):
    def __init__(self, assertion):
        self.assertion = assertion

    def check(self, param):
        return self.assertion(param)


class ListAssertion(object):
    def __init__(self, inner_assertion):
        self.internal_assertion = inner_assertion

    def check(self, param):
        try:
            return all(self.internal_assertion.check(p) for p in param)
        except TypeError:
            return False


class MemberAssertion(object):
    def __init__(self, member_name, inner_assertion):
        self.member_name = member_name
        self.internal_assertion = inner_assertion

    def check(self, param):
        member = getattr(param, self.member_name)
        return self.internal_assertion.check(member)


def _parse_single_assertion(assertion_text):
    # List
    match = re.match(r'\[(.*)\]', assertion_text)
    if match:
        inner_assertion = _parse_single_assertion(match.groups()[0])
        return ListAssertion(inner_assertion)
    # Member
    match = re.match(r'(.*):(.*)', assertion_text)
    if match:
        inner_assertion = _parse_single_assertion(match.groups()[1])
        return MemberAssertion(match.groups()[0], inner_assertion)
    # Simple
    return SimpleAssertion(_defined_contracts[assertion_text])


def parse_assertion(assertion):
    assert(isinstance(assertion, str))
    # Multiple assertions
    if ',' in assertion and '|' in assertion:
        raise ContractParseError("Cannot use operators ',' and '|' in the same contract assertion")
    separator_char = '|' if '|' in assertion else ','
    assertions = [assertion.strip() for assertion in assertion.split(separator_char)]
    parsed_assertions = [_parse_single_assertion(assertion_text) for assertion_text in assertions]
    return ContractAssertion(parsed_assertions, separator_char == ',')

