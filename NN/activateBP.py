import math, nn

#requires neuron.s to be logistic "slope"
def logistic_activation(self, inVal):
	return 1 / (1 + math.exp(-self.s * inVal))
	