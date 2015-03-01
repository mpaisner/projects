import pygame, math, sys, random, drawing

from pygame.locals import *
pygame.font.init()

DEFAULT_SIZE = (300, 300)

class Province:
	
	def __init__(self, name):
		self.name = name

def getTestWorld():
	size = DEFAULT_SIZE
	borders = {(x, y) for x in range(300) for y in range(300) }
	provinces = [Province(str(i)) for i in range(16)]
	borders = set()
	provinceAreas = {}
	for x in range(300):
		for y in range(300):
			if (x > 0 and x % 50 == 0) or (y > 0 and y % 50 == 0):
				borders.add((x, y))
			elif x >= 50 and y >= 50 and x < 250 and y < 250:
				i = (x-50) / 50 + 4 * ((y-50) / 50)
				provinceAreas[(x, y)] = provinces[i]
	colorMap = {provinces[i] : pygame.Color((i * 20) % 255, abs(255 - i * 20) % 255, (2 ** i) % 255) for i in range(16)}
	borderColor = pygame.Color('black')
	oceanColor = pygame.Color('blue')
	return drawing.WorldMap(size, borders, provinceAreas, colorMap, borderColor, oceanColor), provinces

if __name__ == "__main__":
	
	pygame.init()
	screen = pygame.display.set_mode(DEFAULT_SIZE, DOUBLEBUF | RESIZABLE)
	updates = 0
	updated = True
	world, provinces = getTestWorld()
	armyDrawer = drawing.ArmyDraw(world, None, None)
	
	screen.blit(world.map, (0, 0))
	savedColor = None
	
	clock = pygame.time.Clock()
	
	while 1:
		msElapsed = clock.tick(20)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == K_SPACE:
					print "oy", updates
					if updates > 0 and updates < 17:
						world.setColor(provinces[updates - 1], savedColor)
						updated = True
						if updates == 16:
							updates += 1
					if updates < 16:
						savedColor = world.getColor(provinces[updates])
						world.setColor(provinces[updates], pygame.Color('red'))
						updated = True
						updates += 1
						
		if updated:
			screen.blit(world.map, (0, 0))
			pygame.display.flip()
			updated = False
					