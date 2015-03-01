import pygame
from pygame.locals import *

class Map:

	def __init__(self, size):
		self.width = size[0]
		self.height = size[1]
		self.squares = []
		self.pixels = pygame.Surface((self.width, self.height))
		self.pixels.convert_alpha()
		self.colormap = {"ocean": (25, 120, 200)}
		for x in range(size[0]):
			self.squares.append([])
			for y in range(size[1]):
				self.squares[x].append("ocean")
				self.pixels.set_at((x, y), (25, 120, 200))
	
	def in_map(self, loc):
		return loc[0] >= 0 and loc[1] >= 0 and loc[0] < self.width and loc[1] < self.height
	
	def set(self, loc, val):
		if self.in_map(loc):
			self.squares[loc[0]][loc[1]] = val
			self.pixels.set_at(loc, self.colormap[val])
	
	def get(self, loc):
		if self.in_map(loc):
			return self.squares[loc[0]][loc[1]]
		return None
	
	def add_terr(self, terr, color):
		self.colormap[terr] = color
	
	def fill(self, loc, val):
		queue = [loc]
		seen = {}
		while queue:
			next = queue.pop(0)
			if next in seen or not self.get(next) or self.get(next) == "border":
				continue
			seen[next] = True
			for delta in [-1, 1]:
				p1 = (next[0] + delta, next[1])
				if p1 not in seen:
					queue.append(p1)
				p2 = (next[0], next[1] + delta)
				if p2 not in seen:
					queue.append(p2)
		for coord in seen:
			self.set(coord, val)
	
	def trim(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.get((x, y)) != "border":
					continue
				locs = ((x - 1, y), (x + 1, y), (x, y + 1), (x, y - 1))
				val = None
				for loc in locs:
					if self.in_map(loc):
						if self.get(loc) != "border":
							if val and val != self.get(loc):
								val = None
								break
							val = self.get(loc)
				if val:
					self.set((x, y), val)
	
	def add_neighbors(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.get((x, y)) != "border":
					continue
				locs = ((x - 1, y), (x + 1, y), (x, y + 1), (x, y - 1))
				terrs = []
				for loc in locs:
					if self.in_map(loc):
						terr = self.get(loc)
						if terr != "border" and terr != "ocean":
							terrs.append(terr)
				for terr in terrs:
					for other in terrs:
						if terr != other and other not in terr.neighbors:
							terr.add_neighbor(other)
	
def draw_line(map, terr, pos, rel):
	xinc = 1.0 * rel[0] / max(abs(rel[0]), abs(rel[1]))
	yinc = 1.0 * rel[1] / max(abs(rel[0]), abs(rel[1]))
	cur = (pos[0] - rel[0], pos[1] - rel[1])
	while (xinc != 0 and abs(cur[0] - pos[0]) > abs(xinc) / 2) or (yinc != 0 and abs(cur[1] - pos[1]) > abs(yinc) / 2):
		map.set((int(round(cur[0], 0)), int(round(cur[1], 0))), terr)
		cur = (cur[0] + xinc, cur[1] + yinc)
	map.set((int(round(cur[0], 0)), int(round(cur[1], 0))), terr) #this should get pos


