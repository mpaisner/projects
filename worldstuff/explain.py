from try3 import Expression

class AbstractArg:
	
	def __init__(self, name, fields):
		self.name = name
		self.fields = fields
		if self.fields.__class__.__name__ == "str":
			self.fields = [self.fields]
	
	def valid(self, instance):
		for field in self.fields:
			if not hasattr(instance, field):
				return False
		return True

class Atom(Expression):
	
	#initial args should be [AbstractArg,...]
	#fields is [attribute to reference,...]
	#func is a function that takes a list of field values as inputs and returns a boolean (or value between 0 and 1, in continuous-valued mode)
	def __init__(self, args, fields, func):
		self.kind = self.ATOM
		self.args = args
		self.fields = fields
		self.func = func
	
	def evaluate(self):
		for arg in self.args:
			if arg.__class__ == AbstractArg:
				raise Exception("Cannot evaluate atom with abstract arg " + arg.name)
		inputs = []
		for i in range(len(self.args)):
			inputs.append(getattr(self.args[i], self.fields[i]))
		return self.func(inputs)
	
	def valid(self, val, arg):
		if arg.__class__ == AbstractArg: #abstract to concrete
			return arg.valid(val)
		else: #concrete to abstract
			return val.valid(arg)
	
	def replace_var(self, var, value):
		newAtom = Atom(self.args, self.fields, self.func)
		for arg in newAtom.args:
			if arg == var:
				if not newAtom.valid(value, arg):
					raise Exception("variable replacement of different type: " + str(arg) + " to " + str(value))
		for i in range(len(newAtom.args)):
			if newAtom.args[i] == var:
				newAtom.args[i] = value
		return newAtom

class Result:
	
	#the changed arg/field are assumed to be the first ones in the lists
	def __init__(self, args, fields, func):
		self.args = args
		self.fields = fields
		assert len(args) == len(fields)
		self.func = func
	
	def valid(self, val, arg):
		if arg.__class__ == AbstractArg: #abstract to concrete
			return arg.valid(val)
		else: #concrete to abstract
			return val.valid(arg)
	
	def replace_var(self, var, value):
		newRes = Result(self.args, self.fields, self.func)
		for arg in newRes.args:
			if arg == var:
				if not newRes.valid(value, arg):
					raise Exception("variable replacement of different type: " + str(arg) + " to " + str(value))
		for i in range(len(newRes.args)):
			if newRes.args[i] == var:
				newRes.args[i] = value
		return newRes
	
	def apply(self):
		for arg in self.args:
			if arg.__class__ == AbstractArg:
				raise Exception("Cannot apply result with abstract arg " + arg.name)
		setattr(self.args[0], self.fields[0], self.func([getattr(self.args[i], self.fields[i]) for i in range(len(self.args))]))

class Action:
	
	#args should be AbstractArgs
	#preconds should be Expressions
	#results should be Results (duh)
	def __init__(self, name, args, preconds, results):
		self.name
		self.args = args
		self.preconds = preconds
		self.results = results
	
	def valid(self, val, arg):
		if arg.__class__ == AbstractArg: #abstract to concrete
			return arg.valid(val)
		else: #concrete to abstract
			return val.valid(arg)
	
	def replace_var(self, var, value):
		newAction = Action(self.name, self.args, self.preconds, self.results)
		for arg in newAction.args:
			if arg == var:
				if not newAction.valid(value, arg):
					raise Exception("variable replacement of different type: " + str(arg) + " to " + str(value))
		for i in range(len(newAction.args)):
			if newAction.args[i] == var:
				newAction.args[i] = value
		self.preconds = [precond.replace_var(var, value) for precond in self.preconds]
		self.results = [result.replace_var(var, value) for result in self.results]

def find_accessors(str, start = 0):
	i = start
	accessors = []
	while str.find(".", i + 1) > 0:
		 curr = []
		 i = str.find(".", i + 1)
		 begin = i - 1
		 while str[begin].isalnum():
		 	begin -= 1
		 begin += 1
		 current.append(begin, i)

def parse_precond(precond, actionArgs):
	i = -1
	args = []
	fields = []
	for arg in actionArgs:
		while precond.find(arg.name + ".", i + 1) >= 0:
			i = precond.find(arg.name + ".", i + 1)
			accessStr = arg.name + "."
			print accessStr
			if i != 0 and precond[i - 1].isalnum():
				continue
			while i + len(accessStr) < len(precond) and precond[i + len(accessStr)].isalnum():
				accessStr += precond[i + len(accessStr)]
			fieldname = accessStr.split(".")[1]
			args.append(arg)
			fields.append(fieldname)
			precond = precond.replace(accessStr, "inputs[" + str(len(args) - 1) + "]")
	func = lambda inputs: eval(precond)
	return Atom(args, fields, func)

def parse_result(result, actionargs):
	i = -1
	args = []
	fields = []
	try:
		first, rest = result.split("=")
		argname, attrname = first.strip().split(".")
		for arg in actionargs:
			if arg.name == argname:
				args.append(arg)
				fields.append(attrname)
				break
		if not args:
			raise Exception()	
	except Exception:
		raise Exception("Error reading result signature: " + result)
	for arg in actionargs:
		while rest.find(arg.name + ".", i + 1) >= 0:
			i = rest.find(arg.name + ".", i + 1)
			accessStr = arg.name + "."
			print accessStr
			if i != 0 and rest[i - 1].isalnum():
				continue
			while i + len(accessStr) < len(rest) and rest[i + len(accessStr)].isalnum():
				accessStr += rest[i + len(accessStr)]
			fieldname = accessStr.split(".")[1]
			args.append(arg)
			fields.append(fieldname)
			rest = rest.replace(accessStr, "inputs[" + str(len(args) - 1) + "]")
	func = lambda inputs: eval(rest)
	return Result(args, fields, func)

slot = AbstractArg("slot", "type")
item = AbstractArg("item", ["slottype", "size"])	

class SwordSlot:
	
	type = "sword"

class Sword:
	
	slottype = "spear"
	size = 3
	
precond = parse_precond("slot.type == item.slottype", [slot, item])
sword = Sword()
slotInst = SwordSlot()
print precond.args
instance = precond.replace_var(slot, slotInst).replace_var(item, sword)
print instance.args
print instance.evaluate()

result = parse_result("item.size = item.size + 3", [item])
print result.args
rInst = result.replace_var(item, sword)
print rInst.args[0].size
rInst.apply()
print rInst.args[0].size

def create_action(name, argnames, fields, body):
	args = []
	for i in range(argnames):
		args.append(AbstractArg(argnames[i], fields[i]))
'''
Action - Equip(person, item, slot):
	precond: slot.type == item.slottype
	precond: not slot.item
	precond: canUse(person, item)
	precond: has(person, item)
	precond: ~equipped(person, item)
	result - person.equippedItems = person.equippedItems + [item]
	result - inSlot(slot, item)
	result - ~empty(slot)

Action - Remove(person, item, slot):
	precond - inSlot(slot, item)
	precond - equipped(person, item)
	result - ~equipped(person, item)
	result - ~inSlot(slot, item)
	result - empty(slot)

Action - Take(person, item):
	precond - nearby(person, item)
	result - if 
	result - has(person, item)

Action - Buy(buyer, seller, item):
	precond

Action - remove

Person 1:
	has(money, 10)
	wants(money, 
'''