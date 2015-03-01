import pygame, eventp, gui
from pygame.locals import *

'''
The is a module intended to be used with other game modules.
Its purpose is to allow a territory-based world map which can perform pathfinding, turn generation, etc, while maintaining a drawable surface.
'''

class Terr:
	
	def __init__(self, name, color):
		self.name = name
		self.color = color
	
	def get_color(self):
		return self.color

class World:
	
	#all provinces, including default, must have a get_color() method.
	def __init__(self, size, default, border):
		self.size = size
		self.width = size[0]
		self.height = size[1]
		self.offset = (0, 0)
		self.default = default
		self.border = border
		self.changed = True
		
		self.map = []
		for x in range(self.width):
			self.map.append([])
			for y in range(self.height):
				self.map[x].append(default)
		self.provinces = {default: True}
		self.surface = pygame.Surface((self.width, self.height))
		self.surface.fill(default.get_color())
	
	def get_surface(self):
		self.changed = False
		return self.surface
	
	def top_left(self):
		return (-self.offset[0], -self.offset[1])
	
	def in_map(self, loc):
		return loc[0] >= 0 and loc[1] >= 0 and loc[0] < self.width and loc[1] < self.height
	
	def scroll(self, change):
		self.offset = self.adjusted_point(change)
	
	def set(self, loc, terr):
		if self.in_map(loc):
			self.map[loc[0]][loc[1]] = terr
			self.surface.set_at(loc, terr.get_color())
			self.changed = True
	
	#given window rect, return world rect
	def adjusted_rect(self, rect):
		return pygame.Rect(rect.x - self.offset[0], rect.y + self.offset[y], rect.width, rect.height)
	
	#given window point, return world point
	def adjusted_point(self, point):
		return (point[0] + self.offset[0], point[1] + self.offset[1])
	
	def has_changed(self):
		return self.changed
	
	#if 1 or more endpoints outside map, will draw all points on line in map.
	def draw_line(self, start, end, terr):
		if start[0] > end[0]: #x is always increasing
			temp = start
			start = end
			end = start
		startx, starty = start
		endx, endy = end
		if abs(endx - startx) > abs(endy - starty): #greater change in x
			xinc = 1
			if endy == starty:
				yinc = 0
			else:
				yinc = (endy - starty) / (endx - startx)
		else: #greater change in y or equal
			yinc = 1
			if start == end:
				xinc = 1
			else: #delta-y must be > 0
				xinc = (endx - startx) / (endy - starty)
		self.set(start, terr)
		cur = start
		while abs(cur[0] - startx) < abs(endx - startx) or abs(cur[1] - starty) < abs(endy - starty): #change is less than expected change
			cur = (cur[0] + xinc, cur[1] + yinc)
			self.set(cur, terr)
	
	def fill(self, loc, terr):
		if not self.get(loc) or self.get(loc) == self.border:
			return
		queue = [loc]
		seen = {loc: True}
		while queue:
			next = queue.pop(0)
			for delta in [-1, 1]:
				p1 = (next[0] + delta, next[1])
				if p1 not in seen and self.get(p1) and self.get(p1) != self.border:
					queue.append(p1)
					seen[p1] = True
				p2 = (next[0], next[1] + delta)
				if p2 not in seen and self.get(p2) and self.get(p2) != self.border:
					queue.append(p2)
					seen[p2] = True
		for coord in seen:
			self.set(coord, terr)
	
	def move_dir(self, loc, dir):
		if dir == 0: return (loc[0], loc[1] - 1)
		elif dir == 1: return (loc[0] + 1, loc[1])
		elif dir == 2: return (loc[0], loc[1] + 1)
		elif dir == 3: return (loc[0] - 1, loc[1])
	
	def turn_left(self, dir):
		return (dir - 1) % 4
	def turn_right(self, dir):
		return (dir + 1) % 4
	
	#borderfill assumes no territories contained in each other
	def border_fill(self, loc, terr):
		if not self.get(loc) or self.get(loc) == self.border:
			return
		cur = loc
		while self.get(cur) and self.get(cur) != self.border:
			cur = (cur[0], cur[1] + 1) #set cur to first border above start
		borders = {}
		cur = (cur[0], cur[1] + 1) #cur is first square below border.
		start = cur
		dir = 0 #0, 1, 2, 3 = N, E, S, W
		while True:
			next = self.move_dir(cur, dir)
			if start == cur and next[0] in borders and next[1] in borders[next[0]]:
				break
			if not self.get(next) or self.get(next) == self.border:
				if next[0] not in borders:
					borders[next[0]] = {}
				borders[next[0]][next[1]] = True
				dir = self.turn_right(dir)
			else: #square to fill
				cur = next
				dir = self.turn_left(dir)
		for x in borders:
			keys = sorted(borders[x].keys())
			i = 1
			lasty = keys[0]
			while True:
				self.draw_line((x, lasty), (x, keys[i]))
				if i + 2 >= len(keys):
					break
				lasty = keys[i + 1]
				i += 2
		
pygame.init()
screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
ocean = Terr("ocean", (0, 120, 255))
border = Terr("border", (200, 200, 0))
world = World((2000, 2000), ocean, border)
info = gui.GUI((324, 768))
mapsize = (screen.get_size()[0] - info.size[0], screen.get_size()[1] - info.size[1])
info.add_mode_button("Draw Border", "border", (20, 50))
info.add_mode_button("Regular Fill", "fill", (120, 50))
info.add_mode_button("Border Fill", "bfill", (220, 50))
info.add_mode_display("Mode: [mode]", (120, 120))
info.modedisplay.textcolor = (255, 255, 255)
#next: put in add border/fill commands based on mode, on mouse click.

while 1:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit(0)
		if event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] >= 700:
			info.click(event.button, (event.pos[0] - 700, event.pos[1]))
		scroll = eventp.scroll_event(world.offset, world.size, mapsize, event)
		if scroll: world.scroll(scroll)
	if world.has_changed():
		screen.blit(world.get_surface(), world.top_left())
		pygame.display.flip()
		print "world"
	if info.has_changed():
		screen.blit(info.draw(), (700, 0))
		pygame.display.flip()
		print "info"
	