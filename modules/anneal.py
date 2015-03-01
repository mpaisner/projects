import random, math

def keep_change(oldEnergy, newEnergy):
	if newEnergy <= oldEnergy:
		return True
	return False	
	#prob = oldEnergy / (newEnergy + oldEnergy)
	#return random.random() < prob

keep_change(50.0, 60.0)
keep_change(60.0, 50.0)
keep_change(10.0, 0.0)
keep_change(0.0, 10.0)

def sim_anneal(nodes, labels, nFunc, energyFunc, checkTurns = 10, numStable = 5):
	minEnergy = float('inf')
	timesEnergyStable = 0
	i = 0
	while True:
		nodei = random.randrange(len(nodes))
		node = nodes[nodei]
		oldEnergy = energyFunc(nFunc(node, nodes))
		oldLabel = node.label
		node.label = random.choice([label for label in labels if label != oldLabel])
		newEnergy = energyFunc(nFunc(node, nodes))
		if not keep_change(oldEnergy, newEnergy):
			node.label = oldLabel
		if i % checkTurns == 0:
			print "calculating energy for iteration", str(i) + ":",
			totEnergy = 0
			for node in nodes:
				totEnergy += energyFunc(nFunc(node, nodes))
			print round(totEnergy, 3)
			if totEnergy < minEnergy:
				minEnergy = totEnergy
				timesEnergyStable = 0
			else:
				timesEnergyStable += 1
				if timesEnergyStable >= numStable:
					break
		i += 1

nFunc = lambda node, nodes: [n for n in nodes if n.x == node.x]
labels = ["low", "high"]

class Node:
	
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.label = random.choice(labels)

nodes = [Node(x, y) for x in range(5) for y in range(5)]

energyFunc = lambda neighborhood: sum([abs(node.x - 1) if node.label == "low" else abs(node.x - 3) for node in neighborhood])

sim_anneal(nodes, labels, nFunc, energyFunc)
for node in nodes:
	print node.x, node.y, ":", node.label
		