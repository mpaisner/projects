import math, heapq

class Node:
	
	def __init__(self, loc):
		self.loc = loc
		self.dim = len(self.loc)
	
	def distance(self, other):
		assert self.dim == other.dim
		dist = 0
		for i in range(self.dim):
			dist += (self.loc[i] - other.loc[i]) ** 2
		return math.sqrt(dist)

class Edge:
	
	def __init__(self, node1, node2, weight = 1, directed = False):
		self.nodes = (node1, node2)
		self.weight = weight
		self.directed = directed
	
	

class SpatialGraph:
	
	def __init__(self, dim = None):
		self.nodes = set()
		self.dim = dim
	
	def add_node(self, node):
		if self.dim and node.dim != self.dim:
			raise Exception("Wrong input node dimension")
		if not self.dim:
			self.dim = node.dim
		self.nodes.add(node)
	
	def calc_all_distances(self):
		self.distances = {}
		for node1 in self.nodes:
			self.distances[node1] = {}
			for node2 in self.nodes:
				if node1 == node2:
					self.distances[node1][node2] = 0
				elif node2 in self.distances and node1 in self.distances[node2]:
					self.distances[node1][node2] = self.distances[node2][node1]
				else:
					self.distances[node1][node2] = node1.distance(node2)
	
	def mst(self):
		self.calc_all_distances()
		for 
	
	
	