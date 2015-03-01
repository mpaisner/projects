import pygame, math, sys, random, images

from pygame.locals import *
pygame.font.init()

class WorldMap:
	
	'''
	class that defines the underlying visual structure of the world - oceans, continents, province borders. This class is responsible for providing the "background" image on which units will be drawn. Redrawing this image is expensive; therefore it will only be done when necessary. For example, when a province changes hands, the pixels of that province will be redrawn.
	'''
	
	def __init__(self, size, borders, provinceAreas, colorMap, borderColor, oceanColor):
		'''
		input provinceAreas should be {loc: province}. Stored values are {province: set{locs}}.
		'''
		self.provinceAreas = {}
		self.map = pygame.Surface(size)
		pixArray = pygame.PixelArray(self.map)
		for x in range(size[0]):
			for y in range(size[1]):
				if (x, y) in borders:
					pixArray[x, y] = borderColor
				elif (x, y) in provinceAreas:
					province = provinceAreas[(x, y)]
					if province not in colorMap:
						raise Exception("province color not specified: " + province.name)
					pixArray[x, y] = colorMap[province]
					if province not in self.provinceAreas:
						self.provinceAreas[province] = set()
					self.provinceAreas[province].add((x, y))
				else:
					pixArray[x, y] = oceanColor
		del pixArray
		self.armyLocs = {province: random.choice(self.provinceAreas[province]) for province in self.provinceAreas}
	
	def setColor(self, province, color):
		pixArray = pygame.PixelArray(self.map)
		for loc in self.provinceAreas[province]:
			pixArray[loc[0], loc[1]] = color
		del pixArray
	
	def getColor(self, province):
		pixArray = pygame.PixelArray(self.map)
		for loc in self.provinceAreas[province]:
			color = pixArray[loc[0], loc[1]]
			del pixArray
			return color
	
	def chooseArmyLocs(self, imgSize):
		pass
		
class ArmyDraw:
	
	defColor = (0, 0, 0)
	
	def __init__(self, worldmap, imgSize = None, img = None):
		self.map = worldmap
		self.imgSize = imgSize
		self.img = img
	
	def chooseFontColor(self, bkgColor):
		perceptiveLuminance = 1 - ( 0.299 * color.r + 0.587 * color.g + 0.114 * color.b) / 255
		if perceptiveLuminance < 0.5:
			#bright - use dark colored font
			fontColor = pygame.Color(0, 0, 0)
		else:
			#dark - use bright font
			fontColor = pygame.Color(255, 255, 255)
		return fontColor
	
	def drawArmies(self, surface, armyCounts, colorMap):
		'''
		Both armyCounts and colorMap take Provinces as keys
		'''
		font = pygame.font.SysFont('helvetica', 16)
		for province in armyCounts:
			fontColor = self.chooseFontColor(colorMap[province])
			text = str(armyCounts[province])
			fontSurf = font.render(text, False, fontColor)
			desiredLoc = self.map.armyLocs[province]
			
			#make sure not blitting off edge of surface. Still might be if surface is too small; in this case just fail.
			blitLoc = (max(0, min(surface.get_width() - fontSurf.get_width(), desiredLoc[0] -  fontSurf.get_width() / 2)), max(0, min(surface.get_height() - fontSurf.get_height(), desiredLoc[1] -  fontSurf.get_height() / 2)))
			
			surface.blit(fontSurf, blitLoc)
		