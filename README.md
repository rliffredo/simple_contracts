# Simple Contracts

Small module to allow some DBC in python.

Contracts can specify assertions on parameters, on relations between parameters, and the return value.
Assertions on parameters and return value are boolean functions that must be registered before the contract evaluation.
Assertions on relations between parameters instead are just any python expression.

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
  3. They can also be preceded by 'name:' to state that the assertion is on a member
  4. It is possible to nest the two points before in any way
  5. Several assertions can be chained with ',', meaning they need all to be satisfied
  6. As well, '|' can be used to state alternative paths. This can't be used together with ','.

Example assertions:
  - `p='positive int'`  
    p  satisfies contract 'positive int'
  - `p='[positive int]'`  
    p is a sequence of items all satisfying the contract 'positive int'
  - `p='member:positive int'`  
    p is an object with a member satisfying the contract 'positive int'
  - `p='[member:positive int]'`  
    p is a sequence of objects, all with a member satisfying the contract 'positive int'
  - `p='member1:positive int,member2:negative int'`  
    p is an object, with member1 satisfying contract 'positive int' and member2 satisfying
    contract 'negative int'
  - `p='positive int|negative int'`  
    p satisfies any of contracts 'positive int' and 'negative int'