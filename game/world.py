import pygame, pics
from pygame.locals import *

class World:

	def __init__(self, mapGen, squareSize = 30):
		self.squareSize = squareSize
		self.map = mapGen.generate()
		self.image = self.gen_image(self.squareSize)
		self.groups = []
	
	def road(self, x, y):
		return self.map.has_road(x, y)
	
	def terrain(self, x, y):
		return self.map.get_terrain(x, y)
	
	def city(self, x, y):
		return self.map.get_city(x, y)
	
	def site(self, x, y):
		return self.map.get_site(x, y)
	
	def gen_image(self, squareSize): #simple to start
		image = pygame.Surface((self.map.width * squareSize, self.map.height * squareSize), flags=pygame.SRCALPHA)
		for x in range(self.map.width):
			for y in range(self.map.height):
				image.blit(pygame.transform.smoothscale(pics.get_image(self.terrain(x, y)), (squareSize, squareSize)), (x * squareSize, y * squareSize))
		return image
	
				

class Map:
	
	#each square is (terrain, road?, site/city)
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.squares = []
		for x in range(width):
			self.squares.append([])
			for y in range(height):
				self.squares[x].append(("ocean", False, None))
	
	def get_city(self, x, y):
		if self.squares[x][y][0] == "city":
			return self.squares[x][y][2]
		return None
	
	def get_terrain(self, x, y):
		return self.squares[x][y][0]
	
	def has_road(self, x, y):
		return self.squares[x][y][1]
	
	def get_site(self, x, y):
		if self.squares[x][y][0] != "city":
			return self.squares[x][y][2]
		return None

class BaseMapGen:
	
	def __init__(self):
		pass
	
	def generate(self):
		map = Map(100, 100)
		map.squares[10][10] = (("grassland", False, None))
		return map