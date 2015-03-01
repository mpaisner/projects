import random

class Atom:
	
	def __init__(self, predicate, quantifiers, *args):
		self.predicate = predicate
		self.quantifiers = quantifiers
		self.args = [arg for arg in args]
	
	def copy(self):
		return Atom(self.predicate, self.quantifiers, *self.args)

	def replace(self, old, new):
		copy = self.copy()
		copy.args = [arg if arg != old else new for arg in self.args]
		copy.quantifiers = {quantifier for quantifier in copy.quantifiers if quantifier.var != old}
		return copy
	
	def replaceAll(self, vals):
		copy = self.copy()
		copy.args = [arg if arg not in vals else vals[arg] for arg in copy.args]
		copy.quantifiers = {quantifier for quantifier in copy.quantifiers if quantifier.var not in vals}
		return copy
	
	def __eq__(self, other):
		if isinstance(other, Atom):
			return self.predicate == other.predicate and self.args == other.args
		elif isinstance(other, And):
			return self == other.expr1 or self == other.expr2
		return False
	
	def __hash__(self):
		return hash((self.predicate, tuple(self.args)))
	
	def trueAssignments(self, objects, kb, n):
		gen = InstanceGenerator(self, objects)
		trues = set()
		for i in range(n):
			if not gen.hasNext():
				break
			next = gen.next()
			if next in kb:
				trues.add(next)
		return trues
		
	def allTrue(self, objects, kb, n):
		gen = InstanceGenerator(self, objects)
		for i in range(n):
			if not gen.hasNext():
				break
			next = gen.next()
			if next not in kb:
				return False
		return True
	
	def someTrue(self, objects, kb, n):
		gen = InstanceGenerator(self, objects)
		for i in range(n):
			if not gen.hasNext():
				break
			next = gen.next()
			if next in kb:
				return True
		return False
	
	def shortstr(self):
		s = str(self.predicate) + "("
		for arg in self.args:
			s += str(arg) + ", "
		if self.args:
			s = s[:-2]
		s += ")"
		return s
	
	def __str__(self):
		s = ""
		for quantifier in self.quantifiers:
			s += str(quantifier) + " "
		if self.quantifiers:
			s += ": "
		s += self.shortstr()
		return s

UNIVERSAL = 0
EXISTENTIAL = 1

class Quantifier:
	
	def __init__(self, var, type):
		self.var = var
		self.type = type
	
	def __str__(self):
		if self.type == UNIVERSAL:
			s = "for all "
		elif self.type == EXISTENTIAL:
			s = "exists "
		s += str(self.var)
		return s

class And:
	
	def __init__(self, quantifiers, arg1, arg2):
		self.quantifiers = quantifiers
		self.arg1 = arg1
		self.arg2 = arg2
	
	def replace(self, old, new):
		return And({quantifier for quantifier in self.quantifiers if quantifier.var != old}, self.arg1.replace(old, new), self.arg2.replace(old, new))
	
	def replaceAll(self, vals):
		return And({quantifier for quantifier in self.quantifiers if quantifier.var not in vals}, self.arg1.replaceAll(vals), self.arg2.replaceAll(vals))
	
	def shortstr(self):
		return self.arg1.shortstr() + " & " + self.arg2.shortstr()
	
	def __str__(self):
		s = ""
		for quantifier in self.quantifiers:
			s += str(quantifier) + " "
		if self.quantifiers:
			s += ": "
		s += self.shortstr()
		return s
		

class Conditional:
	
	def __init__(self, quantifiers, arg1, arg2):
		self.quantifiers = quantifiers
		self.condition = arg1
		self.consequent = arg2

	def replace(self, old, new):
		return Conditional({quantifier for quantifier in self.quantifiers if quantifier.var != old}, self.condition.replace(old, new), self.consequent.replace(old, new))
	
	def replaceAll(self, vals):
		return Conditional({quantifier for quantifier in self.quantifiers if quantifier.var not in vals}, self.condition.replaceAll(vals), self.consequent.replaceAll(vals))
	
	def shortstr(self):
		return self.condition.shortstr() + " -> " + self.consequent.shortstr()
	
	def __str__(self):
		s = ""
		for quantifier in self.quantifiers:
			s += str(quantifier) + " "
		if self.quantifiers:
			s += ": "
		s += self.shortstr()
		return s

class InstanceGenerator:
	
	MAX_GUESSES = 10000
	
	def __init__(self, expr, objects):
		self.expr = expr
		self.objects = objects
		self.guesses = 0
	
	def hasNext(self):
		return len(self.objects) > 0 and self.guesses < self.MAX_GUESSES
	
	def next(self):
		self.guesses += 1
		vals = {quantifier.var: random.choice(self.objects) for quantifier in self.expr.quantifiers}
		return self.expr.replaceAll(vals)

exprshort = Atom("dog", {Quantifier('x', EXISTENTIAL)}, 'x')
trues = exprshort.trueAssignments(['fido', 'dave', 'doug', 'bark', 'rob'], [Atom("dog", set(), 'fido'), Atom("dog", set(), 'bark')], 50)

print [str(true) for true in trues]
sys.exit()

expr1 = And(set(), Atom("dog", {Quantifier('x', EXISTENTIAL)}, 'x'), Conditional({Quantifier('y', UNIVERSAL)}, Atom("dog", set(), 'y'), Atom("furry", set(), 'y')))

print expr1
gen = InstanceGenerator(expr1, ["rex", "clyde", "john", "fido"])

def checkTruth(expr, objects, kb, n):
	gen = InstanceGenerator(expr, objects)
	
	for i in range(n):
		if not gen.hasNext():
			return False
		next = gen.next()

for i in range(10):
	if gen.hasNext():
		print gen.next()


	