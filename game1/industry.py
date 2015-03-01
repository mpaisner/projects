import math

#to opitimize, create a way to generate next value given last value.
class Effect:
	
	def __init__(self, precedence, tags, func, start = 0, end = float("inf")):
		self.precedence = precedence
		self.tags = tags
		self.func = func
		self.start = start
		self.end = end
	
	def apply(self, val, i):
		return self.func(val, i)

class Function:
	
	def __init__(self, baseval = 1):
		self.startval = baseval
		self.effects = []
	
	def add_effect(self, neweffect):
		i = 0
		for effect in self.effects:
			if effect.precedence <= neweffect.precedence:
				i += 1
			else:
				break
		self.effects.insert(i, neweffect)
		return i
	
	def calc_cost(self, i):
		res = self.startval
		for effect in self.effects:
			if effect.start <= i and effect.end > i:
				res = effect.apply(res, i)
		return res
	
	def __getitem__(self, i):
		return self.calc_cost(i)
	
def get_result(function, input, startval):
	if function[int(startval)] * (math.ceil(startval) - startval) < input:
		output = int(math.ceil(startval))
		input -= function[int(startval)] * (math.ceil(startval) - startval)
	else: #not enough production to reach the next full unit
		return startval + input / function[int(startval)]
	while input > function[output]:
		input -= function[output]
		output += 1
	return output + input / function[output]

#cost funcs:
#base:
BASE_INCREASE = 0.001
BASE_INCREASE_EFFECT = Effect(1, ['base increase'], (lambda x, i: x + (BASE_INCREASE * i)))

f = Function()
f.add_effect(BASE_INCREASE_EFFECT)
for val in [0, 5, 10, 20, 50, 1000]:
	print f[val]

print get_result(f, 150, 10.2)

#next: land use (how land effects industry functions)