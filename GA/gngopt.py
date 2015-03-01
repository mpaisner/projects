import math, random

def euclidian_distance(v1, v2):
	assert len(v1) == len(v2)
	total = 0.0
	for i in range(len(v1)):
		total += (v1[i] - v2[i]) ** 2
	return math.sqrt(total)

def distance(v1, v2):
	return euclidian_distance(v1, v2)

class Node:
	
	stableupdates = 30
	
	def __init__(self, location):
		self.location = location
		self.error = 0.0
		self.errordev = 0.0 #total deviation from average error
		self.updates = 1
		self.age = 1
	
	def range(self, numdeviations = 1.8):
		rang = (self.error / self.updates) + math.sqrt((self.errordev / self.updates)) * numdeviations
		if self.updates < self.stableupdates:
			rang *= (self.stableupdates / self.updates) ** (0.1)
		return rang
	
	def update_error(self, dist):
		self.updates += 1
		self.error += dist
		self.errordev += ((self.error / self.updates) - dist) ** 2		
	
	def move_towards(self, v):
		assert len(v) == len(self.location)
		learnrate = 1 / self.updates
		for i in range(len(v)):
			self.location[i] += learnrate * (v[i] - self.location[i])
	
	def update(self, v, dist):
		self.move_towards(v)
		self.update_error(dist)
	
	#other should be removed from net elsewhere
	def combine(self, other):	
		small = self.updates < self.stableupdates or other.updates < other.stableupdates
		dist = distance(self.location, other.location)
		updateratio = 1.0 * self.updates / (other.updates + self.updates)
		learnrate = 1 - updateratio
		for i in range(len(self.location)):
			self.location[i] += learnrate * (other.location[i] - self.location[i])
		newerror = self.error + other.error + (other.updates * dist * updateratio + self.updates * dist * learnrate) / 2
		self.errordev = (self.errordev + other.errordev) * (newerror / (self.error + other.error)) ** 2
		self.error = newerror
		self.updates += other.updates
		self.age = max(self.age, other.age)
		return small
		
	
	def __str__(self):
		dim = min(8, len(self.location))
		s = "["
		for i in range(dim):
			s += str(round(self.location[i], 2)) + " "
		s = s[:-1] + "]"
		return s

class GNG:
	
	def __init__(self):
		self.nodes = []
		self.age = 0
		self.minupdates = 2
		self.combinefreq = 100
		self.ubercombinefreq = 3000
		self.combinemultiplier = 1.2
		self.numdeviations = 2.0
		self.smallupdates = 0
		self.largeupdates = 0
		self.storevalues = True
		self.values = []
		self.maxnodesforubercombine = 12
		self.maxnodes = 20
	
	def closest_node(self, v, exclude = []):
		mindist = float("inf")
		closest = None
		for node in self.nodes:
			if node in exclude:
				continue
			dist = distance(node.location, v)
			if dist < mindist:
				mindist = dist
				closest = node
		return closest, mindist

	def max_error_node(self, nodeset = None):
		if not nodeset:
			nodeset = self.nodes
		maxErrorNode = None
		maxError = float("-inf")
		for node in nodeset:
			if node.error > maxError:
				maxErrorNode = node
				maxError = node.error
		return maxErrorNode
	
	def consolidate(self):
		nodes = {node : True for node in self.nodes}
		while nodes:
			node = random.choice(nodes.keys())
			close, closedist = self.closest_node(node.location, [node])
			if node in nodes:
				del nodes[node]
			if not close:
				continue
			if max(close.range(self.numdeviations), node.range(self.numdeviations)) * self.combinemultiplier > closedist:
				#print "combining"
				#print node, node.updates, node.age, round(node.range(self.numdeviations), 2), round(closedist, 2)
				#print close, close.updates, close.age, round(close.range(self.numdeviations), 2), round(closedist, 2)
				if node.combine(close):
					self.smallupdates += 1
				else:
					self.largeupdates += 1
				self.nodes.remove(close)
				if close in nodes:
					del nodes[close]
				#print node, node.updates, node.age, round(node.range(self.numdeviations), 2), round(closedist, 2)
				#print
	
	def get_error_if_combined(self, node1, node2, data):
		node1weight = 1.0 * node1.updates / (node2.updates + node1.updates)
		node2weight = 1 - node1weight
		meannode = Node(map(lambda x: x[0] * node1weight + x[1] * node2weight, zip(node1.location, node2.location)))
		totalerror = 0
		totalerror2 = 0
		for val in data:
			closest, dist = self.closest_node(val)
			if closest in [node1, node2]:
				totalerror += dist
				totalerror2 += distance(meannode.location, val)
		return totalerror, totalerror2
	
	def uber_consolidate(self):
		x = 0
		print len(self.values[-self.ubercombinefreq * 2:]), len(self.nodes)
		while x < len(self.nodes):
			if x % 10 == 0:
				print x, "nodes done"
			if self.nodes[x].updates < self.minupdates:
				x += 1
				continue
			miny = None
			minerr = float("inf")
			y = 0
			while y < len(self.nodes):
				
				if x == y or self.nodes[y].updates < self.minupdates:
					y += 1
					continue
				error1, error2 = self.get_error_if_combined(self.nodes[x], self.nodes[y], self.values[-self.ubercombinefreq * 2:])
				if error1 * 1.5 > error2:
					if error2 < minerr:
						minerr = error2
						miny = y
				y += 1
			if miny:
				print "combining", self.nodes[x], self.nodes[miny]
				self.nodes[x].combine(self.nodes[miny])
				self.nodes.pop(miny)
			if not miny or miny > x:
				x += 1	
		print len(self.nodes)
					
	def cleanup(self):
		while True:
			numnodes = len(self.nodes)
			self.uber_consolidate()
			if len(self.nodes) == numnodes:
				break
	
	def cleanup_old(self):
		i = 0
		while i < len(self.nodes):
			if self.nodes[i].age < self.age % self.combinefreq:
				print "removed node in cleanup"
				self.nodes.pop(i)
			else:
				i += 1	
	
	def update(self, v):
		if self.storevalues:
			self.values.append(v)
		self.age += 1
		if len(self.nodes) < 1:
			self.nodes.append(Node(v))
			return
		closest, dist = self.closest_node(v)
		
		#decide if v is too far from closest node
		if closest.updates >= self.minupdates and dist > closest.range(self.numdeviations):
			print closest.range(4), closest.range(2), closest.updates
			self.nodes.append(Node(v))
			return
		
		#update closest node if v belongs to it
		closest.update(v, dist)
		
		#update node ages
		for node in self.nodes:
			node.age += 1
		
		#combine close nodes
		if self.age % self.combinefreq == 0:
			self.consolidate()
			if len(self.nodes) > self.maxnodes:
				self.numdeviations += 1.1
				print self.numdeviations
		if self.age % self.ubercombinefreq == 0 and len(self.nodes) <= self.maxnodesforubercombine:
			pass#self.uber_consolidate()
	
	#calibrates net to likely produce one node from vect set
	def calibrate(self, vects, likelihood = 0.99, increment = 0.05, lasthigh = False, numtests = 10):
		print self.numdeviations
		nummultiplenodes = 0
		for i in range(numtests):
			shuffledvects = list(vects)
			random.shuffle(shuffledvects)
			net = GNG()
			net.combinefreq = self.combinefreq
			net.combinemultiplier = self.combinemultiplier
			net.numdeviations = self.numdeviations
			for vect in shuffledvects:
				net.update(vect)
			net.consolidate()
			net.cleanup()
			if len(net.nodes) > 1:
				nummultiplenodes += 1
			if nummultiplenodes > numtests * (1 - likelihood):
				self.numdeviations += increment
				if not lasthigh:
					self.calibrate(vects, likelihood, increment, False, numtests)
				return #if last numdeviations was high enough, return that value, since current one is too low.
		self.numdeviations -= increment
		self.calibrate(vects, likelihood, increment, True, numtests)
					

def rand_vect(means, devs):
	vect = []
	for mean, dev in zip(means, devs):
		vect.append(mean + (random.random() - 0.5) * dev)
	return vect

'''
vals = [[0, 1, 2], [0, 1, 2], [2, 1, 2], [2, 1, 2]]
	
net = GNG()

for val in vals:
	net.update(val)

print net.get_error_if_combined(net.nodes[0], net.nodes[1], vals)

data = [rand_vect([0,1,2], [0.5, 0.2, 0.3]) for i in range(500)]
data += [rand_vect([2,1,2], [0.5, 0.2, 0.3]) for i in range(500)]
print net.get_error_if_combined(net.nodes[0], net.nodes[1], data)	

#middata = [rand_vect([1,1,2], [0.5, 0.2, 0.3]) for i in range(1000)]
#print net.get_error_if_combined(net.nodes[0], net.nodes[1], middata)


for i in range(23000):
	net.update(rand_vect([0,1,2], [0.5, 0.2, 0.3]))
#for i in range(1500):
	#net.update(rand_vect([1,1,2], [0.5, 0.2, 0.3]))
for i in range(3300):
	net.update(rand_vect([0,1,2], [0.5, 0.2, 0.3]))
for i in range(3500):
	net.update(rand_vect([1,1,2], [0.5, 0.2, 0.3]))
for i in range(3500):
	net.update(rand_vect([1,1,3], [0.5, 0.2, 0.3]))


for node1 in net.nodes:
	for node2 in net.nodes:
		if node1 != node2:
			print node1, node2
			print net.get_error_if_combined(node1, node2, [rand_vect([0.5,1,2], [0.5, 0.2, 0.3]) for i in range(1000)])
			print net.get_error_if_combined(node1, node2, [rand_vect([0,1,2], [0.5, 0.2, 0.3]) for i in range(1000)])
			print
	
net.cleanup()


for node in net.nodes:
	closest, dist = net.closest_node(node.location, [node])
	print node, node.updates, node.age, round(node.range(), 2), round(dist, 2)
'''