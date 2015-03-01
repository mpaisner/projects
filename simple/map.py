import pygame, sys, random, territory, pickle, gameinfo
from pygame.locals import *

class Border:
	
	def __init__(self):
		self.neighbors = [None, None]
	
	def get_neighbor(self, BR = True):
		if BR: #bottom/right
			return self.neighbors[1]
		else:
			return self.neighbors[0]
	
	def set_neighbor(self, neighbor, BR = True):
		if BR: #bottom/right
			self.neighbors[1] = neighbor
		else:
			self.neighbors[0] = neighbor
		
class Map:
	
	squaresize = 5
	oceancolor = (0, 40, 200)
	
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.right_borders = []
		self.down_borders = []
		self.continents = {}
		self.territories = {}
		self.centers = {}
		for x in range(self.width):
			self.right_borders.append({})
			self.down_borders.append({})
			top = Border()
			top.set_neighbor("ocean")
			#middle = Border()
			#middle.set_neighbor("weird_ocean")
			#middle.set_neighbor("ocean", False)
			bottom = Border()
			bottom.set_neighbor("ocean", False)
			self.right_borders[x][0] = top
			#self.right_borders[x][height / 2] = middle
			self.right_borders[x][height] = bottom
		self.right_borders.append({})
		self.down_borders.append({}) #so can have borders on far right
		for y in range(self.height):
			left = Border()
			left.set_neighbor("ocean")
			right = Border()
			right.set_neighbor("ocean", False)
			self.down_borders[0][y] = left
			self.down_borders[width][y] = right
		
	def draw_noarg(self):
		new = pygame.Surface((self.squaresize * (self.width), self.squaresize * (self.height)))
		new.convert_alpha()
		for x in range(len(self.down_borders)):
			keys = self.right_borders[x].keys()
			keys.sort()
			for y, ynext in zip(keys, keys[1:]):
				if self.right_borders[x][y].get_neighbor() == "ocean":
					color = self.oceancolor
				else:
					color = self.right_borders[x][y].get_neighbor().color
				new.fill(color, (self.squaresize * x, self.squaresize * y, self.squaresize * (x + 1), self.squaresize * ynext))
				pygame.draw.line(new, (0, 0, 0), (self.squaresize * x, self.squaresize * y), (self.squaresize * (x + 1), self.squaresize * y))
			for y in self.down_borders[x]:
				pygame.draw.line(new, (0, 0, 0), (self.squaresize * x, self.squaresize * y), (self.squaresize * x, self.squaresize * (y + 1)))
		for terr in self.centers:
			font = pygame.font.Font(None, 30)
			new.blit(font.render(str(terr.units), True, terr.player.color), (self.centers[terr][0] * self.squaresize, self.centers[terr][1] * self.squaresize))
		return new
	
	def draw(self, colormap):
		new = pygame.Surface((self.squaresize * (self.width), self.squaresize * (self.height)))
		new.convert_alpha()
		for x in range(len(self.down_borders)):
			keys = self.right_borders[x].keys()
			keys.sort()
			for y, ynext in zip(keys, keys[1:]):
				color = colormap[self.right_borders[x][y].get_neighbor()]
				new.fill(color, (self.squaresize * x, self.squaresize * y, self.squaresize * (x + 1), self.squaresize * ynext))
				pygame.draw.line(new, (0, 0, 0), (self.squaresize * x, self.squaresize * y), (self.squaresize * (x + 1), self.squaresize * y))
			for y in self.down_borders[x]:
				pygame.draw.line(new, (0, 0, 0), (self.squaresize * x, self.squaresize * y), (self.squaresize * x, self.squaresize * (y + 1)))
		return new
	
	def next_border_up(self, x, y):
		if x <= 0 or x > self.width or y < 0 or y > self.height:
			return None
		if y == 0: 
			return self.right_borders[x][y]
		borders = self.right_borders[x].keys()
		minmax = 0
		for border in borders:
			if border < y and border > minmax:
				minmax = border
		return self.right_borders[x][minmax]
	
	def next_border_down(self, x, y):
		if x <= 0 or x > self.width or y < 0 or y > self.height:
			return None
		if y == self.height: 
			return self.right_borders[x][y]
		borders = self.right_borders[x].keys()
		minmax = self.height
		for border in borders:
			if border > y and border < minmax:
				minmax = border
		return self.right_borders[x][minmax]
	
	def in_map(self, point):
		return not (point[0] < 0 or point[0] >= self.width or point[1] < 0 or point[1] >= self.height)
	
	def fill_column(self, x, y, neighbor):
		self.next_border_up(x, y).set_neighbor(neighbor)
		self.next_border_down(x, y).set_neighbor(neighbor, False)
	
	def gen_neighbor_pairs(self):
		pairs = {}
		for x in range(1, self.width):
			for y in self.right_borders[x]:
				if y != 0 and y != self.height:
					neighbor1 = self.right_borders[x][y].get_neighbor()
					neighbor2 = self.right_borders[x][y].get_neighbor(False)
					if neighbor1 != neighbor2:
						if neighbor1 not in pairs:
							pairs[neighbor1] = [neighbor2]
						elif neighbor2 not in pairs[neighbor1]:
							pairs[neighbor1].append(neighbor2)
						if neighbor2 not in pairs:
							pairs[neighbor2] = [neighbor1]
						elif neighbor1 not in pairs[neighbor2]:
							pairs[neighbor2].append(neighbor1)
			for y in self.down_borders[x]:
				if y != 0 and y != self.height:
					neighbor1 = self.next_border_up(x, y + 1).get_neighbor()
					neighbor2 = self.next_border_up(x - 1, y + 1).get_neighbor()
					if neighbor1 != neighbor2:
						if neighbor1 not in pairs:
							pairs[neighbor1] = [neighbor2]
						elif neighbor2 not in pairs[neighbor1]:
							pairs[neighbor1].append(neighbor2)
						if neighbor2 not in pairs:
							pairs[neighbor2] = [neighbor1]
						elif neighbor1 not in pairs[neighbor2]:
							pairs[neighbor2].append(neighbor1)
		return pairs
		
	def add_continent(self, continent):
		self.continents[continent.name] = continent
		for territory in continent.territories:
			self.add_territory(territory)
	
	def set_center(self, x, y):
		if self.in_map((x, y)):
			self.centers[self.next_border_up(x, y).get_neighbor()] = (x, y)
	
	def add_territory(self, territory):
		self.territories[territory.name] = territory
	
	def remove_useless_borders(self):
		for x in range(1, self.width):
			todel = []
			for y in self.right_borders[x]:
				if y != 0 and y != self.height:
					border = self.right_borders[x][y]
					if border.get_neighbor(False) == border.get_neighbor():
						todel.append((x,y))
			for x, y in todel:
				del self.right_borders[x][y]
			del todel[:]
			for y in self.down_borders[x]:
				if y != 0 and y != self.height:
					if self.next_border_up(x, y + 1).get_neighbor() == self.next_border_up(x - 1, y + 1).get_neighbor():
						todel.append((x, y))
			for x, y in todel:
				del self.down_borders[x][y]
	
	#this is not quite right, but works well enough
	def add_border(self, start, end):
		if not (self.in_map(start) and self.in_map(end)):
			return 
		x = start[0]
		y = start[1]
		if x == end[0]:
			for y in range(min(start[1], end[1]), max(start[1], end[1])):
				if y in self.down_borders[x]:
					continue
				newborder = Border()
				newborder.set_neighbor(self.next_border_up(x - 1, y + 1).get_neighbor(), False)
				newborder.set_neighbor(self.next_border_up(x, y + 1).get_neighbor())
				self.down_borders[x][y] = newborder
		else:
			xDir = (end[0] - start[0]) / abs(end[0] - start[0])
			yPerx = abs(1.0 * (end[1] - y) / (end[0] - x))
			yDir = None
			if yPerx > 0:
				yDir = (end[1] - start[1]) / abs(end[1] - start[1])
			yRemainder = 0
			while x != end[0]:
				if xDir < 0 and (yDir == None or yDir > 0):
					x += xDir
				yRemainder += yPerx
				while yRemainder > 0:
					if (xDir > 0 and yDir < 0) or (xDir < 0 and yDir > 0):
						y += yDir
					yRemainder -= 1
					if y not in self.down_borders[x]:
						down = Border()
						down.set_neighbor(self.next_border_up(x - 1, y + 1).get_neighbor(), False)
						down.set_neighbor(self.next_border_up(x, y + 1).get_neighbor())
						self.down_borders[x][y] = down
					if (xDir > 0 and yDir > 0) or (xDir < 0 and yDir < 0):
						y += yDir
				if y not in self.right_borders[x]:
					right = Border()
					right.set_neighbor(self.next_border_up(x, y).get_neighbor(), False)
					right.set_neighbor(self.next_border_up(x, y).get_neighbor())
					self.right_borders[x][y] = right
				if xDir > 0 or (yDir != None and yDir < 0):
					x += xDir
		
					

				

		
	
			