import path

############################
####### Tech
############################


############################
####### TERRAIN
############################

class Terrain:
	
	def __init__(self, args):
		self.data = {}
		for key, val in args:
			self.data[key] = val
	

############################
####### UNITS
############################

class Unit:
	
	def __init__(self, moves, movetype):
		pass

############################
####### City
############################

#returns (food, shields, trade)
def apply_production_effects(effects, food, shields, trade):
	for effect in effects:
		if effect.type != "per_square_resource_change":
			raise Exception("invalid effect returned")

def get_square_production(city, square):
	food = square.terrain.get("food")
	shields = square.terrain.get("shields")
	trade = square.terrain.get("trade")
	food, shields, trade = apply_production_effects(city.get_square_effects(square), food, shields, trade))

class City:
	
	def __init__(self, args):
		def __init__(self, args):
		self.data = {}
		for key in args:
			self.data[key] = args[key]
	
	def set(self, args):
		for key in args:
			self.data[key] = args[key]
	
	def get(self, key):
		if key in self.data:
			return self.data[key]
		return []
	
	#returns all effects (building, gov, wonder, etc.) of a certain set of types operating in this city. Ordered by order of operation, so democracy trade goes before superhighway, for example.
	def get_effects(self, effecttypes):
		raise Exception("not implemented")
	
	#returns all effects that apply to a given square. This should check preconditions and only return applicable effects.
	def get_square_effects(self, square):
		raise Exception("not implemented")
	
	def in_radius(self, loc):
		cloc = self.data["loc"]
		xdif = abs(loc[0] - cloc[0])
		ydif = abs(loc[1] - cloc[1])
		return (xdif < 2 or ydif < 2) and xdif < 3 and ydif < 3

def build_city(world, player, loc, name):
	#worker starts off as entertainer, no default project. Set these.
	city = City({"name": name, "loc": loc, "player": player, "world": world, "pop": 1, "shields": 0, "food": 0, "project": None, "buildings": [], "workerlocs": [(-1, -1)], "supported units": []}

############################
####### 
############################


class Grid:
	
	def __init__(self, size, default):
		self.width = size[0]
		self.height = size[1]
		self.size = size
		self.squares = []
		for x in range(self.width):
			self.squares.append([])
			for y in range(self.height):
				self.squares[x].append(default)
		
	def contains(self, obj):
		for row in self.squares:
			for square in row:
				if square == obj:
					return True
		return False
	
	def in_grid(self, loc):
		return loc[0] in range(0, self.width) and loc[1] in range(0, self.height)
		
	def set(self, loc, val):
		if self.in_grid(loc):
			self.squares[loc[0]][loc[1]] = val
	
	#returns a rectangular region that intersects (not contains) all modified points. Returns None if no points are modified.
	def set_all(self, locs, val):
		x = (self.width - 1, 0)
		y = (self.height - 1, 0)
		for loc in locs:
			if self.in_grid(loc):
				x = (min(x[0], loc[0]), max(x[1], loc[0]))
				y = (min(x[0], loc[0]), max(x[1], loc[0]))
				self.set(loc, val)
		if x[0] <= x[1] and y[0] <= y[1]: #some loc in map has been set
			return ((x[0], y[0]), (x[1], y[1]))
		return None
	
	def get_first_true(self, func):
		for x in range(self.width):
			for y in range(self.height):
				if func(self.squares[x][y]):
					return (x, y)
	
	def get_all_true(self, func, area = None):
		if not area:
			area = (0, 0, self.width, self.height)
		locs = []
		for x in range(area[0], area[2]):
			for y in range(area[1], area[3]):
				if func(self.squares[x][y]):
					locs.append((x, y))
		return locs
	
	def manhattan(self, loc1, loc2):
		return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
	
	#assuming all moves are cost 1; all squares moveable.
	def move_dist(self, loc1, loc2):
		return max(abs(loc1[0] - loc2[0]), abs(loc1[1] - loc2[1]))
	
	def get_neighbors(self, loc):
		neighbors = []
		for x in range(loc[0] - 1, loc[0] + 2):
			for y in range(loc[1] - 1, loc[1] + 2):
				if x != 0 or y != 0: #not current square
					neighbors.append((x, y))
		return neighbors
	

class CivWorld:
	
	def __init__(self, data = {}):
		self.grid = []
	
	#change this function to differentiate units that move on various terrain types.
	def get_neighbors(self, loc, unit):
		neighbors = self.grid.get_neighbors()
		for neighbor in neighbors:
			#remove invalid move options
			pass
		return neighbors
	
	#define to allow pathfinding
	def move_cost(self, start, neighbor, unit):
		pass
		
	def shortest_path(self, start, end, unit):
		return path.get_path_h(self, start, end, unit, lambda loc1, loc2: max(abs(loc1[0] - loc2[0]), abs(loc1[1] - loc2[1])))
	