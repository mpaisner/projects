class SegmentedMemory:
	
	def __init__(self):
		self.exact = {}
		self.sameArgs = {}
		self.samePreds = {}
		self.individualPred = {}
		self.individualArg = {}
	
	def addFact(self, fact):
		exact = hash(fact)
		if exact in self.exact:
			self.exact[exact].append(fact)
		else:
			self.exact[exact] = [fact]
		sameArgs = fact.sameArgsHash()
		if sameArgs in self.sameArgs:
			self.sameArgs[sameArgs].append(fact)
		else:
			self.sameArgs[sameArgs] = [fact]
		samePreds = fact.samePredsHash()
		if samePreds in self.samePreds:
			self.samePreds[samePreds].append(fact)
		else:
			self.samePreds[samePreds] = [fact]
		for pred in fact.predicates():
			predHash = hash(pred)
			if predHash in self.individualPred:
				self.individualPred[predHash].append(fact)
			else:
				self.individualPred[predHash] = [fact]
		for arg in fact.arguments():
			argHash = hash(arg)
			if arg in self.individualArg:
				self.individualArg[arg].append(fact)
			else:
				self.individualArg[arg] = [fact]