class Path:
	
	def __init__(self, stops, cost):
		self.stops = stops
		self.cost = cost
	
	def extend(self, dest, cost):
		return Path(self.stops + [dest], self.cost + cost)
	
	def __len__(self):
		if self.cost != float("inf"):
			return len(self.stops)
		return self.cost

class TransportCosts:
	
	def __init__(self, territories, knowncosts):
		self.territories = set(territories)
		for start in knowncosts:
			for dest in knowncosts[start]:
				knowncosts[start][dest] = Path([start, dest], knowncosts[start][dest])
		self.allpaths = self.dijkstra(territories, knowncosts)
	
	def dijkstra(self, territories, knowncosts):
		allpaths = {}
		for territory in territories:
			paths = {}
			open = [(0, Path([territory], 0))]
			while open and len(paths) < len(territories):
				cost, nextpath = heapq.heappop(open)
				terr = nextpath.stops[-1]
				if terr in paths:
					continue
				paths[terr] = nextpath
				for dest, path in knowncosts[terr].items():
					newpath = nextpath.extend(dest, path.cost)
					heapq.heappush(open, (newpath.cost, newpath))
			for terr in territories:
				if terr not in paths:
					infpath = Path([territory], 0)
					paths[terr] = infpath.extend(terr, float("inf"))
			allpaths[territory] = paths
		return allpaths
	
	def paths_from(self, source):
		return self.allpaths[source]
	
	def cost(self, source, dest):
		return self.allpaths[source][dest].cost
	
	def route(self, source, dest):
		return self.allpaths[source][dest].stops
	
	#rather than counting only direct paths, for efficiency, might keep old paths under certain conditions.
	def direct_paths(self):
		allpaths = {}
		for start in self.territories:
			allpaths[start] = {}
			for dest in self.territories:
				if len(self.allpaths[start][dest]) == 2:
					allpaths[start][dest] = self.allpaths[start][dest]
		return allpaths
	
	#maybe make more efficient later
	def update(self, newcosts):
		for start in newcosts:
			for dest in newcosts[start]:
				newcosts[start][dest] = Path([start, dest], newcosts[start][dest])
		costs = self.direct_paths()
		for start in newcosts:
			costs[start].update(newcosts[start])
		self.allpaths = self.dijkstra(territories, costs)