# Simple Contracts

Small module to allow some DBC in python _and_ IronPython.  
Tested on Python 3.4, as well as IronPython 2.7.6.

Contracts can specify assertions on parameters, on relations between parameters, and the return value.
Assertions on parameters and return value are boolean functions that must be registered before the contract evaluation.
Assertions on relations between parameters instead are just any python expression.
Contracts can be turned off, for instance to improve performance on a final release. Note that there are no performance
tests now about the impact of the contracts, in both cases (enabled and disabled).

Usage:

````python
import contracts

contracts.new_contract('positive int', lambda n: isinstance(n, int) and n>0)
@contracts.contract(a='positive int', b='positive int', _returns='positive int', _constraint='a<b')
def f(a, b):
    return a+b
````

Assertion syntax:
  1. A basic assertion is just a reference to a contract defined with new_contract
  2. Assertions may be surrounded by [] to state the assertion is on all items of the enumerable
  3. Assertions may be surrounded by {} to state the assertion is on all the values of a mapping
  3. They can also be preceded by 'name:' to state that the assertion is on a member
  4. It is possible to nest the two points before in any way
  5. Several assertions can be chained with ',', meaning they need all to be satisfied
  6. As well, '|' can be used to state alternative paths. This can't be used together with ','
  7. It is possible to pass a callable, with signature x  -> Bool, which will be simply called with the parameter and
     will return the assertion result.

Example assertions:
  - `p='positive int'`  
    p  satisfies contract 'positive int'
  - `p='[positive int]'`
    p is a sequence of items all satisfying the contract 'positive int', or is a mapping with all keys satisfying the
    same contract
  - `p='{positive int}'`
    p is a mapping with all values satisfying the contract 'positive int'
  - `p='member:positive int'`  
    p is an object with a member satisfying the contract 'positive int'
  - `p='[member:positive int]'`  
    p is a sequence of objects, all with a member satisfying the contract 'positive int'
  - `p='member1:positive int,member2:negative int'`  
    p is an object, with member1 satisfying contract 'positive int' and member2 satisfying
    contract 'negative int'
  - `p='positive int|negative int'`  
    p satisfies any of contracts 'positive int' and 'negative int'

## Basic contracts
There are already available some basic contracts:
  - `not none`: fails if parameter is None
  - `bool`, `number`, `string`: they all fail if parameter is not of the desired type
  - `any date`: fails if the parameter is not a date (in IronPython, also System.Date)
  - `any datetime`: fails if the parameter is not a datetime (in IronPython, also System.DateTime)
  - `string with text`: fails if the parameter is not a string, or if it is an empty string
  - `not empty`: fails if the parameter is not a container, or the container is empty
  - `sorted`: fails if the parameter is not a container (or a string!) or its content is not sorted.
