from try3 import *
from stuff import *

CarX = Atom("Car", [Variable("x")])
streetLeftX = Atom("streetLeft", [Variable("x")])
streetRightX = Atom("streetRight", [Variable("x")])
heardX = Atom("heard", [Variable("x")])
useHearing = Expression(CONDITIONAL, [heardX, Expression(OR, [streetLeftX, streetRightX])])


crossSafely = SimpleAction([

