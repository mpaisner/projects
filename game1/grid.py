import random

default_territories = [str(i) for i in range(200)]
INORDER = 0
RANDOM = 1

class PossessionGrid:
	
	def __init__(self, width, height):
		self.grid = [[None for u in range(height)] for i in range(width)]
		self.width = width
		self.height = height
		
	def __getitem__(self, val):
		try:
			return self.grid[val]
		except TypeError:
			return self.grid[val[0]][val[1]]
	
	def __setitem__(self, index, val):
		try:
			self.grid[index[0]][index[1]] = val
		except TypeError:
			self.grid[index] = val
	
	def __contains__(self, loc):
		try:
			self[loc]
			return True
		except IndexError:
			return False
	
	def all_vals(self):
		vals = set()
		for row in self.grid:
			for val in row:
				vals.add(val)
		return vals
	
	def open(self, square):
		return not self[square]
	
	def next_open_square(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.open((x, y)):
					return (x, y)
		return None
	
	def adjacent_squares(self, square):
		x, y = square
		squares = [(x + i, y) for i in [-1, 1]] + [(x, y + i) for i in [-1, 1]]
		return set([square for square in squares if square[0] >= 0 and square[1] >= 0 and square[0] < self.width and square[1] < self.height])
	
	def open_adjacent_squares(self, square):
		adjacent = self.adjacent_squares(square)
		return set([square for square in adjacent if self.open(square)])
	
	def average_size(self):
		return float(self.width * self.height) / len(self.all_vals())

def next_name(names, namechoice):
	if namechoice == RANDOM:
		i = random.randrange(len(names))
	elif namechoice == INORDER:
		i = 0
	return names.pop(i)

def random_territory_grid(width, height, avesquares, stdev, terrnames = default_territories, namechoice = INORDER):
	names = list(terrnames)	
	grid = PossessionGrid(width, height)
	
	square = grid.next_open_square()
	while square:
		numsquares = int(round(random.gauss(avesquares, stdev)))
		adjacentsquares = grid.open_adjacent_squares(square)
		name = next_name(names, namechoice)
		grid[square] = name
		while numsquares > 0 and adjacentsquares:
			next = random.choice(list(adjacentsquares))
			grid[next] = name
			adjacentsquares.update(grid.open_adjacent_squares(next))
			numsquares -= 1
		square = grid.next_open_square()
	return grid

#grid = random_territory_grid(10, 10, 4, 1)
#print grid.all_vals()
#print grid.average_size()
#print grid[0]