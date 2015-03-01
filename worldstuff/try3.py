ATOM = 0
CONDITIONAL = 1
OR = 2
AND = 3
XOR = 4
NOT = 5
VAR = 6
ITEM = 7
FORALL = 8
EXISTS = 9

class Expression:
	
	type = "expression"
	ATOM = 0
	CONDITIONAL = 1
	OR = 2
	AND = 3
	XOR = 4
	NOT = 5
	VAR = 6
	ITEM = 7
	
	def __init__(self, kind, args, beliefLevel = 3, duration = None):
		self.kind = kind
		self.args = args
		self.beliefLevel = beliefLevel
		self.duration = duration
	
	def all_atoms(self):
		atoms = []
		for arg in self.args:
			atoms += arg.all_atoms()
		return atoms
	
	def replace(self, var, value):
		newExpr = Expression(self.kind, self.args, self.beliefLevel, self.duration)
		if newExpr.kind == newExpr.ATOM:
			return newExpr #Atom classes should handle this
		elif newExpr.kind != newExpr.NOT:
			newExpr.args[1] = newExpr.args[1].replace(var, value)
		newExpr.args[0] = newExpr.args[0].replace(var, value)
		return newExpr
	
	def __getitem__(self, val):
		return self.args[val]
	
	def same_belief(self, other):
		if type(self) != type(other) or self.kind != other.kind or len(self.args) != len(other.args):
			return False
		for i in range(len(self.args)):
			if not self.args[i].same_belief(other.args[i]):
				return False
		return True
	
	def evaluate(self, agent):		
		evalleft = self[0].evaluate(agent)
		if self.kind != self.NOT:
			evalright = self[1].evaluate(agent)
			
		if self.kind == self.CONDITIONAL:
			return max(1 - evalleft, evalleft * evalright)
		elif self.kind == self.OR:
			return max(evalleft, evalright)
		elif self.kind == self.AND:
			return evalleft * evalright
		elif self.kind == self.XOR:
			return max(evalleft * (1 - evalright), evalright * (1 - evalleft))
		elif self.kind == self.NOT:
			return 1 - evalleft
	
	def get_keys(self):
		keys = []
		for item in self.args:
			keys += item.get_keys()
		return list(set(keys))

class Atom(Expression):
	
	kind = ATOM
	
	def __init__(self, predicate, args, beliefLevel = 3, duration = None):
		self.predicate = predicate
		self.args = args
		self.beliefLevel = beliefLevel
		self.duration = duration
	
	def all_atoms(self):
		return [self]
	
	def evaluate(self, agent):
		return agent.evaluate_atom(self)
	
	def replace(self, var, value):
		newAtom = Atom(self.predicate, self.args, self.beliefLevel, self.duration)
		newAtom.args = [arg.replace(var, value) for arg in self.args]
		return newAtom
	
	def same_belief(self, other):
		if type(self) != type(other) or self.kind != other.kind or self.predicate != other.predicate or len(self.args) != len(other.args):
			return False
		varDict = {}
		for i in range(len(self.args)):
			if type(self.args[i]) != type(other.args[i]) or self.args[i].kind != other.args[i].kind:
				return False
			if self.args[i].kind == VAR:
				if self.args[i].id in varDict:
					if varDict[self.args[i].id] != other.args[i].id:
						return False
				else:
					varDict[self.args[i].id] = other.args[i].id
			elif self.args[i].kind == ITEM:
				if self.args[i].inst != other.args[i].inst:
					return False
			elif self.args[i].kind in (FORALL, EXISTS):
				if self.args[i].id in varDict:
					if varDict[self.args[i].id] != other.args[i].id:
						return False
				else:
					varDict[self.args[i].id] = other.args[i].id
		if not varDict:
			return True #in case of 0-arg predicates
		return varDict		
	
	def get_keys():
		keys = [self.predicate]
		for arg in self.args:
			if arg.kind == Expression.ITEM:
				keys.append(arg.inst)
		return keys
	
	def __str__(self):
		s = self.predicate + "("
		for arg in self.args:
			s += str(arg) + ", "
		if self.args:
			s = s[:-2]
		return s + ")"
			
class Variable:
	
	kind = VAR
	
	def __init__(self, id):
		self.id = id
	
	def replace(self, var, value):
		if self.id == var:
			return Item(value)
		return self
	
	def __str__(self):
		return self.id

class Item:
	
	kind = ITEM
	
	def __init__(self, inst):
		self.inst = inst
	
	def replace(self, var, value):
		return self
	
	def __eq__(self, other):
		return self.inst == other.inst
		
	def __str__(self):
		return str(self.inst)

class QuantifiedVar:
	
	def __init__(self, kind, id):
		assert kind == FORALL or kind == EXISTS
		self.kind = kind
		self.id = id
	
	def replace(self, var, value, isVar=False):
		if self.id == var:
			if isVar:
				return QuantifiedVar(self.kind, value)
			return Item(value)
		return self
	
	def __eq__(self, other):
		return type(self) == type(other) and self.kind == other.kind and self.id == other.id
	
	def __str__(self):
		return self.id