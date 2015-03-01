#neuron.s must be defined as value of sigmoid slope
def logistic_learn_ol(self, other, args):
	#if first weight, calculate delta
	if "delta calculated" not in self.learnData:
		error = (self.learnData["predicted"] - self.activation)
		fPrime = self.activation * (1 - self.activation) * self.s
		self.learnData["delta"] = error * fPrime
		self.learnData["delta calculated"] = True
	change = args["learn rate"] * self.learnData["delta"] * other.activation
	#print self.name, other.name, "act", other.activation, "change", change
	return change

def logistic_learn_hl(self, other, args):
	#if first weight, calculate delta
	if "delta calculated" not in self.learnData:
		error = 0
		for neuron in args["last layer"].neurons:
			if self in neuron.weightV and "delta calculated" in neuron.learnData:
				error += neuron.weightV[self] * neuron.learnData["delta"]
		fPrime = self.activation * (1 - self.activation) * self.s
		self.learnData["delta"] = error * fPrime
		self.learnData["delta calculated"] = True
	change = args["learn rate"] * self.learnData["delta"] * other.activation
	return change

def clean(self):
	if "delta calculated" in self.learnData:
		del self.learnData["delta calculated"]