import pygame, random, sys, eventp
from pygame.locals import *

class Star:
	
	def __init__(self, image, rect):
		self.image = image
		if hasattr(rect, "colliderect"):
			self.rect = rect
		elif hasattr(rect, "__len__"):
			if len(rect) == 2:
				self.rect = pygame.Rect(rect[0], rect[1])
			elif len(rect) == 4:
				self.rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
			else:
				raise Exception("Invalid input rect")
		else:
			raise Exception("Invalid input rect")

class Starmap:

	def __init__(self, size, stars = []):
		self.stars = {}
		self.size = size
		self.width = size[0]
		self.height = size[1]
		self.offset = (0, 0)
		for star in stars:
			self.stars[star] = True
	
	def add_star(self, star):
		self.stars[star] = True
	
	def delete_star(self, star):
		if star in self.stars:
			del self.stars[star]
	
	def adjusted_rect(self, rect):
		return pygame.Rect(rect.x - self.offset[0], rect.y + self.offset[y], rect.width, rect.height)
	
	def adjusted_point(self, point):
		return (point[0] + self.offset[0], point[1] + self.offset[1])
	
	def get_stars_in_rect(self, rect, adjust = True):
		if adjust:
			rect = self.adjusted_rect(rect)
		stars = []
		for star in self.stars:
			if rect.colliderect(star.rect):
				stars.append(star)
		return stars
	
	def get_star(self, loc, adjust = True):
		if adjust:
			loc = self.adjusted_point(loc)
		for star in self.stars:
			if star.rect.collidepoint(loc):
				return star
		return None
	
	def is_legal(self):
		maprect = pygame.Rect((0, 0), self.size)
		for star1 in self.stars:
			for star2 in self.stars:
				if star1 != star2 and star1.rect.colliderect(star2.rect):
					return False #do any stars overlap?
			if not maprect.contains(star1.rect):
				return False
		return True


class StarmapDrawer:
	
	def __init__(self, starmap, bkgcolor = (0, 0, 0)):
		self.starmap = starmap
		self.bkgcolor = bkgcolor
		self.repaint()
	
	def scroll(self, change):
		self.starmap.offset = self.starmap.adjusted_point(change)
	
	def top_left(self):
		return (-self.starmap.offset[0], -self.starmap.offset[1])
	
	def repaint(self, rect=None, adjusted = False):
		if not rect:
			self.surface = pygame.Surface((self.starmap.width, self.starmap.height))
			rect = self.surface.get_rect()
		self.surface.fill(self.bkgcolor, rect)
		for star in self.starmap.get_stars_in_rect(rect, adjusted):
			self.surface.blit(star.image, star.rect)
	
	#should be given window coords - adjusted automatically so long as "scroll" is called.
	def get_selected_star(self, loc):
		return self.starmap.get_star(loc)
	
	def get_map_size(self):
		return self.starmap.size

def gen_random_map(size, starsize, numstars):
	map = Starmap(size)
	redstar = pygame.image.load("./redstar.jpg")
	redstar = pygame.transform.scale(redstar, (starsize, starsize))
	while numstars > 0:
		x = random.random() * (size[0] - 2 * starsize) + starsize
		y = random.random() * (size[1] - 2 * starsize) + starsize
		star = Star(redstar, pygame.Rect(x, y, starsize, starsize))
		map.add_star(star)
		numstars -= 1
	return map

pygame.init()
map = gen_random_map((2000, 2000), 20, 50)
drawer = StarmapDrawer(map)

eventp.set_selection_mode(2)

screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
screen.blit(drawer.surface, drawer.top_left())
pygame.display.flip()
changed = (True, None)
while 1:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit(0)
		scroll = eventp.scroll_event(drawer.starmap.offset, drawer.get_map_size(), screen.get_size(), event)
		selected = eventp.select_event(drawer.starmap.offset, drawer.starmap.get_star, event)
		if selected and selected[0] != None:
			print selected
		if scroll:
			drawer.scroll(scroll)
			changed = (True, None)
	if changed[0]:
		drawer.repaint(changed[1])
		screen.blit(drawer.surface, drawer.top_left())
		pygame.display.flip()
		
	