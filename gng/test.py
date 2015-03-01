import gng, random

patterns = {0.4: [3, 2, 0, 0], 0.01: [-1, 0, 4, 0], 0.8: [1, 0, 0, -5]}
	
#simple test method; only reads three decimals of probability
def sample_patterns_const_var(patterns, times, variance):
	choices = []
	for prob, pattern in patterns.items():
		choices += [pattern] * int(prob * 1000)
	sample = []
	for n in range(times):
		chc = random.choice(choices)
		item = []
		for i in range(len(chc)):
			item.append(random.gauss(chc[i], variance))
		sample.append(item)
	return sample
			
net = gng.GNG(4)
sample = sample_patterns_const_var(patterns, 1000, 0.1)

'''
s = ""
for item in sample:
	s += " ("
	for val in item:
		s += str(round(val, 1)) + " "
	s = s[:-1] + ")"
print s
'''
net.maximumAge = 50
for item in sample:
	net.update(item)
for node in net.nodes:
	print node, node.error