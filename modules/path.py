import heapq

#world must have methods:
	#get_neighbors(loc, unit)
	#move_cost(start, neighbor, unit)
def get_path(world, start, goal, unit):
	queue = []
	visited = {start: None} #current, previous
	cur = (0, start, None) #cost, loc, from
	while cur and cur[1] != goal:
		for neighbor in world.get_neighbors(cur[1], unit):
			heapq.heappush(queue, (cur[0] + world.move_cost(cur[1], neighbor, unit), neighbor, cur[1]))
		if not queue:
			break
		next = heapq.heappop(queue)
		while next[1] in visited:
			if not queue:
				next = None
				break
			next = heapq.heappop(queue)
		visited[next[1]] = next[2]
		cur = next
	if cur[1] == goal:
		pathreversed = []
		cur = cur[1]
		while visited[cur]:
			pathreversed.append(cur)
			cur = visited[cur]
		#pathreversed.append(cur) #this would add the start location to path
		pathreversed.reverse()
		return pathreversed
	return None

#world must have methods:
	#get_neighbors(loc, unit)
	#move_cost(start, neighbor, unit)
#heuristic must be a method (loc, goal) -> val
def get_path_h(world, start, goal, unit, heuristic):
	queue = []
	visited = {start: None} #current, previous
	cur = (heuristic(start, goal), start, None) #cost, loc, from
	while cur and cur[1] != goal:
		for neighbor in world.get_neighbors(cur[1], unit):
			heapq.heappush(queue, (cur[0] + world.move_cost(cur[1], neighbor, unit) - heuristic(cur[1], goal) + heuristic(neighbor, goal), neighbor, cur[1]))
		if not queue:
			break
		next = heapq.heappop(queue)
		while next[1] in visited:
			if not queue:
				next = None
				break
			next = heapq.heappop(queue)
		visited[next[1]] = next[2]
		cur = next
	if cur[1] == goal:
		pathreversed = []
		cur = cur[1]
		while visited[cur]:
			pathreversed.append(cur)
			cur = visited[cur]
		#pathreversed.append(cur) #this would add the start location to path
		pathreversed.reverse()
		return pathreversed
	return None

'''
Basic tests:

class World:
	
	def __init__(self):
		self.neighbors = {}
	
	def get_neighbors(self, loc, unit):
		if loc in self.neighbors:
			return self.neighbors[loc].keys()
		return []
	
	def move_cost(self, start, neighbor, unit):
		return self.neighbors[start][neighbor]

w = World()
w.neighbors = {"one": {"two": 2, "three": 4}, "two": {"three": 1.8}}
print get_path(w, "one", "three", None)

def testh(start, goal):
	if start == "one":
		return 2
	if start == "two":
		return 1
	else:
		return 0

print get_path_h(w, "one", "three", None, testh)

'''