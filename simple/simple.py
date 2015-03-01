import pygame, sys
from pygame.locals import *

class Map:
	
	terrcolormap = {}
	rectsize = 5
	
	def __init__(self, width, height):
		self.map = []
		for x in range(width):
			self.map.append([])
			for y in range(height):
				self.map[x].append("ocean")
		self.terrcolormap["ocean"] = (0,0,255)
		self.borders = {}
		self.width = width
		self.height = height
		
	def set_square(self, x, y, territory):
		self.map[x][y] = territory
	
	def border_between(self, x1, y1, x2, y2):
		if abs(x1 - x2) + abs(y1 - y2) > 1 or (x1, y1) == (x2, y2) or any(val < 0 for val in (x1, x2, y1, y2)) or x1 >= self.width or x2 >= self.width or y1 >= self.height or y2 >= self.height:
			return True
		elif x1 - x2 == 1:
			return (x1, y1) in self.borders and (x1, y2) in self.borders
		elif x1 - x2 == -1:
			return (x2, y1) in self.borders and (x2, y2) in self.borders
		elif y1 - y2 == 1:
			return (x1, y1) in self.borders and (x2, y1) in self.borders
		elif y1 - y2 == -1:
			return (x1, y2) in self.borders and (x2, y2) in self.borders
		
	#returns (x1, x2, y1, y2) for bounding rect of fill area.	
	def fill(self, x, y, territory):
		queue = [(x / 5, y / 5)]
		tochange = {(x / 5, y / 5):True}
		while queue:
			next = queue.pop(0)
			for dif in [-1, 1]:
				if not self.border_between(next[0], next[1], next[0] + dif, next[1]) and (next[0] + dif, next[1]) not in tochange:
					queue.append((next[0] + dif, next[1]))
					tochange[(next[0] + dif, next[1])] = True
				if not self.border_between(next[0], next[1], next[0], next[1] + dif) and (next[0], next[1] + dif) not in tochange:
					queue.append((next[0], next[1] + dif))
					tochange[(next[0], next[1] + dif)] = True
		minmax = [self.width, 0, self.height, 0]
		for loc in tochange:
			self.map[loc[0]][loc[1]] = territory
			minmax[0] = min(minmax[0], loc[0])
			minmax[2] = max(minmax[2], loc[0])
			minmax[1] = min(minmax[1], loc[1])
			minmax[3] = max(minmax[3], loc[1])
		return minmax
	
	def set_color(self, terr, color):
		self.terrcolormap[terr] = color
	
	def add_borders(self, x1, x2, y1, y2):
		x1 = x1 / 5
		x2 = x2 / 5
		y1 = y1 / 5
		y2 = y2 / 5
		y = y1
		x = x1
		if x2 - x1 == 0:
			ratio = sys.maxint
		else:
			ratio = (y2 - y1) / (x2 - x1)
		if x2 > x1:
			xinc = 1
		else: xinc = -1
		if y2 > y1:
			yinc = 1
		else: yinc = -1
		while 1:
			while abs((y - y1) * ratio) <= abs(x - x1):
				self.borders[(x, y)] = True
				y += yinc			
			if x == x2: break
			x += xinc
		
	def remove_extra_borders(self):
		for border in borders:
			terr = self.map[border[0], border[1]]
			if self.map[border[0] - 1, border[1]] != terr or self.map[border[0], border[1] - 1] != terr or self.map[border[0] - 1, border[1] - 1] != terr:
				self.borders.remove(border)
	
	def get_display(self):
		return self.get_display_piece(0, 0, self.width, self.height)
	
	def get_display_piece(self, x1, y1, x2, y2):
		display = pygame.Surface((self.rectsize * (x2 - x1), self.rectsize * (y2 - y1)))
		display.convert_alpha()
		for x in range(x1, x2):
			for y in range(y1, y2):
				print x, y, self.map[x][y]
				display.fill(self.terrcolormap[self.map[x][y]], (self.rectsize * x, self.rectsize * y, self.rectsize * (x + 1), self.rectsize * (y + 1)))
				if x < self.width - 1 and (x, y) in self.borders and (x + 1, y) in self.borders:
					pygame.draw.line(display, (0, 0, 0), (x * self.rectsize, y * self.rectsize), ((x + 1) * self.rectsize, y * self.rectsize))
		return display

scrollcoords = (0, 0)
pygame.init()
screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
map = Map(100, 100)
screen.blit(map.get_display(), scrollcoords)
currentterr = 0

#buttons: L = 1, wheel = 2, R = 3
terrnames = ["ocean", "Kamchatka", "Alaska", "Peru"]
for terr in range(1, len(terrnames)):
	map.set_color(terrnames[terr], (terr * 60, terr * 60, terr * 60))
			

while 1:
	changearea = (0, 0, 0, 0)
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE: sys.exit(0)
			if event.key == K_SPACE: 
				currentterr = (currentterr + 1) % len(terrnames)
				print map.terrcolormap[terrnames[currentterr]]
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 3:
				#not working
				changearea = map.fill(event.pos[0], event.pos[1], terrnames[currentterr])
			elif event.button == 2:
				currentterr = (currentterr + 1) % len(terrnames)
		elif event.type == pygame.MOUSEMOTION:
			if event.buttons[0] == 1:
				map.add_borders(event.pos[0], event.pos[0] - event.rel[0], event.pos[1], event.pos[1] - event.rel[1])
	if changearea != (0, 0, 0, 0): print changearea
	screen.blit(map.get_display_piece(changearea[0], changearea[1], changearea[2], changearea[3]), (changearea[0], changearea[1]))
	pygame.display.flip()