from funcs import *

basecosts = [1.0 for i in range(100)]
solbase = DiscreteFunction(basecosts)
exponent = 1.2
expeffect = ExpReducePercentCostChange(0, ["base exponent"], 1, 0, exponent, False, 100)
solbase.add_effect(expeffect)
#print solbase.calc_costs()

def get_output(unitcosts, input):
	output = 0
	while output < len(unitcosts) and input > unitcosts[output]:
		input -= unitcosts[output]
		output += 1
	return output + input / unitcosts[output]

def normalize(vector, total = 1.0):
	valsSum = sum(vector)
	return [val * total / valsSum for val in vector]

#if endpad is near 0 (i.e. not much higher than 0), values nearest the present will be much more important. In contrast, if baseval is high, the weights will be more evenly distributed.
def get_time_weights(length, endpad, baseval):
	weights = [baseval + 1.0 / (length + endpad - i) for i in range(length)]
	return normalize(weights)

weights = get_time_weights(100, 10, 0.02)

def calc_sol(history, weights, currentSOLOut, ratio = 0.25):
	if len(history) >= len(weights):
		history = history[-len(weights):]
	else:
		weights = normalize(weights[-len(history):])
	old = sum([data * weight for data, weight in zip(history, weights)])
	return ratio * currentSOLOut + (1 - ratio) * old

print calc_sol([i for i in range(100)], weights, 60)
print get_output(solbase.calc_costs(), 100)

history = [20]
spending = 200
for i in range(10):
	if spending == 200:
		spending = 350
	else:
		spending = 350
	for x in range(10):
		history.append(calc_sol(history, weights, get_output(solbase.calc_costs(), spending), 0.25))
print history