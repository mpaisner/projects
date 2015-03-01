TRUE = 0
FALSE = 1
UNBOUND = 2
UNKNOWN = 3


class Variable:
	
	def __init__(self, value = None):
		self.value = None
	
	def mapping(self, map):
		if self in map:
			return new Variable(map[self])


