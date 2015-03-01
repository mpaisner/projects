
ITEM = "Get_Item"
FIELD = "Access_Field"

class Accessor:
	
	def __init__(self, stateName, *vals):
		self.stateName = stateName
		try:
			for accessType, arg in vals:
				if accessType not in [ITEM, FIELD] or not isinstance(arg, (float, int, long, basestring, Accessor, Call)):
					raise Exception("Accessor pairs must be of the form (ACCESSOR_TYPE, ACCESSOR_ARG) and args must be strings, numbers, function calls, or accessors. Got " + str((accessType, arg)))
				if accessType == FIELD and not isinstance(arg, basestring):
					raise Exception("FIELD access args must be strings, got type " + str(type(arg)))
		except TypeError:
			raise Exception("Accessor args must be of the form (ACCESSOR_TYPE, ACCESSOR_ARG), got " + str(vals))
		self.vals = vals
	
	def write(self, info):
		s = self.stateName
		for accessType, arg in self.vals:
			if accessType == ITEM:
				s += "["
				if isinstance(arg, basestring):
					s += "'" + arg + "'"
				elif isinstance(arg, Accessor):
					s += arg.write(info)
				else:
					s += str(arg)
				s += "]"
			elif accessType == FIELD:
				s += "." + arg
		return s

class EQUALS:
	
	def __init__(self, arg1, arg2):
		self.arg1 = arg1
		self.arg2 = arg2
		if not hasattr(arg1, "write") and hasattr(arg2, "write"):
			raise Exception("Arguments to equals must have write() method")
	
	def write(self, info):
		return "(" + self.arg1.write(info) + ") == (" + self.arg2.write(info) + ")"

class AND:
	
	def __init__(self, arg1, arg2):
		self.arg1 = arg1
		self.arg2 = arg2
		if not hasattr(arg1, "write") and hasattr(arg2, "write"):
			raise Exception("Arguments to and must have write() method")
	
	def write(self, info):
		return "(" + self.arg1.write(info) + ") and (" + self.arg2.write(info) + ")"

class OR:
	
	def __init__(self, arg1, arg2):
		self.arg1 = arg1
		self.arg2 = arg2
		if not hasattr(arg1, "write") and hasattr(arg2, "write"):
			raise Exception("Arguments to or must have write() method")
	
	def write(self, info):
		return "(" + self.arg1.write(info) + ") or (" + self.arg2.write(info) + ")"

class Conditional:
	
	def __init__(self, condition, cmd, elseCmd = None):
		self.condition = condition
		self.cmd = cmd
		self.elseCmd = elseCmd
	
	def write(self, info):
		s = "if " + self.condition.write(info) + ":"
		info['tabs'] += 1
		s += "\n" + "\t" * info["tabs"]
		s += self.cmd.write(info)
		info['tabs'] -= 1
		s += "\n" + "\t" * info["tabs"]
		if self.elseCmd:
			if isinstance(self.elseCmd, Conditional):
				s += "el"
				s += self.elseCmd.write(info)
			else:
				s += "else:"
				info['tabs'] += 1
				s += "\n" + "\t" * info["tabs"]
				s += self.elseCmd.write(info)
				info['tabs'] -= 1
				s += "\n" + "\t" * info["tabs"]
		return s

class PRINT:
	
	def __init__(self, arg):
		self.arg = arg
	
	def write(self, info):
		if hasattr(self.arg, "write"):
			return "print(" + self.arg.write(info) + ")"
		else:
			return "print('" + str(self.arg) + "')"

class Call:
	
	def __init__(self, functionName, *args):
		self.functionName = functionName
		self.args = args
	
	def write(self, info):
		if hasattr(self.functionName, "write"):
			s = self.functionName.write(info)
		else:
			s = str(self.functionName)
		s += "("
		for arg in self.args:
			if hasattr(arg, "write"):
				s += arg.write(info)
			else:
				s += str(arg)
			s += ", "
		if self.args:
			s = s[:-2]
		s += ")"
		return s

class Method:
	
	def __init__(self, name, argNames, body):
		self.name = name
		self.argNames = argNames
		self.body = body
	
	def write(self, info):
		s = "def " + self.name + "("
		for name in self.argNames:
			s += name + ", "
		if self.argNames:
			s = s[:-2]
		s += "):"
		info['tabs'] += 1
		s += "\n" + "\t" * info["tabs"]
		s += self.body.write(info)
		info['tabs'] -= 1
		s += "\n" + "\t" * info["tabs"]
		return s

class Comment:
	
	def __init__(self, txt, wrapChars = None):
		self.lines = txt.split("\n")
		if wrapChars:		
			newLines = []
			for line in self.lines:
				while len(line) > wrapChars:
					newLines.append(line[:wrapChars])
					line = line[wrapChars:]
				newLines.append(line)
			self.lines = newLines
	
	def write(self, info):
		if len(self.lines) <= 1:
			s = "#"
		else:
			s = "'''"
		for line in self.lines:
			s += line + "\n" + "\t" * info['tabs']
		if len(self.lines) > 1:
			s += "'''\n" + "\t" * info['tabs']
		return s

class Chunk:
	
	def __init__(self, *subChunks):
		self.subChunks = subChunks
	
	def write(self, info):
		return "".join([chunk.write(info) for chunk in self.subChunks])

def simpleTest():
	a1 = Accessor("s", (ITEM, "args"), (ITEM, 1))
	a2 = Accessor("s", (ITEM, "args"), (ITEM, 2))
	a3 = Accessor("s", (ITEM, "args"), (ITEM, 3))
	
	check = OR(EQUALS(Call("abs", a2), a1), EQUALS(a2, a3))
	
	c = Conditional(check, PRINT("True!"), PRINT("False!"))
	
	m = Method("test_method", ['s'], c)
	
	call = Call("test_method", Accessor('s'))
	
	chunk = Chunk(m, call)
	
	info = {"tabs": 0}
	
	s = {"args": [1, 1, -1, 2]}
	
	print chunk.write(info)
	exec(chunk.write(info))

simpleTest()

