from pygame import *
from pygame.locals import *
import numbers

class Component:
	
	def __init__(self, **args):
		self.loc = (0, 0)
		self.updated = False
	
	def redraw(self, size):
		raise Exception("Must implement redraw")
	
	def paint(self, surface, rect):
		if not updated:
			self.redraw()
		surface.blit(self.surf, rect, (Rect(self.loc[0], self.loc[1], rect.width, rect.height)))
	
	def processClick(self, button, adjustedLocation):
		pass
	
	def processKeyPress(self, key):
		pass
	
	def getSize(self):
		raise Exception("must implement getSize")

class Label(Component):
	

class Location:
	
	TOP_LEFT = 0
	TOP = 1
	TOP_RIGHT = 2
	RIGHT = 3
	BOTTOM_RIGHT = 4
	BOTTOM = 5
	BOTTOM_LEFT = 6
	LEFT = 7
	CENTER = 8
	ORIENTATIONS = {Location.TOP_LEFT, Location.TOP, Location.TOP_RIGHT, Location.RIGHT, Location.BOTTOM_RIGHT, Location.BOTTOM, Location.BOTTOM_LEFT, Location.LEFT, Location.CENTER}
	
	def __init__(self, loc, tieTo = Location.TOP_LEFT):
		if not (loc in Location.ORIENTATIONS or (len(loc) == 2 and isinstance(loc[0], numbers.Number) and isinstance(loc[0], numbers.Number))):
			raise Exception("loc arg must be an orientation or a point")
		self.loc = loc
		if not (tieTo in Location.ORIENTATIONS or (len(tieTo) == 2 and isinstance(tieTo[0], numbers.Number) and isinstance(tieTo[0], numbers.Number))):
			raise Exception("tieTo arg must be an orientation or a point")
		self.tieTo = tieTo
	
	def getCoords(self, containerSize, loc):
		'''
		return coords corresponding to this location in a container. For example, TOP_LEFT is (0, 0); RIGHT is container.width
		'''
		if len(loc) == 2:
			return loc #assumed to be an actual location
		elif loc == Location.TOP_LEFT:
			return (0, 0)
		elif loc == Location.TOP:
			return (containerSize[0] / 2, 0)
		elif loc == Location.TOP_RIGHT:
			return (containerSize[0], 0)
		elif loc == Location.RIGHT:
			return (containerSize[0], containerSize[1] / 2)
		elif loc == Location.BOTTOM_RIGHT:
			return (containerSize[0], containerSize[1])
		elif loc == Location.BOTTOM:
			return (containerSize[0] / 2, containerSize[1])
		elif loc == Location.BOTTOM_LEFT:
			return (0, containerSize[1])
		elif loc == Location.LEFT:
			return (0, containerSize[1] / 2)
		elif loc == Location.CENTER:
			return (containerSize[0] / 2, containerSize[1] / 2)
	
	def getTopLeft(self, containerSize, componentSize):
		coords = self.getCoords(containerSize, self.loc)
		if len(tieTo) == 2:
			return (coords[0] - tieTo[0], coords[1] - tieTo[1])
		elif tieTo == Location.TOP_LEFT:
			return coords
		elif tieTo == Location.TOP:
			return (coords[0] - componentSize[0] / 2, coords[1])
		elif tieTo == Location.TOP_RIGHT:
			return (coords[0] - componentSize[0], coords[1])
		elif tieTo == Location.RIGHT:
			return (coords[0] - componentSize[0], coords[1] - componentSize[1] / 2)
		elif tieTo == Location.BOTTOM_RIGHT:
			return (coords[0] - componentSize[0], coords[1] - componentSize[1])
		elif tieTo == Location.BOTTOM:
			return (coords[0] - componentSize[0] / 2, coords[1] - componentSize[1])
		elif tieTo == Location.BOTTOM_LEFT:
			return (coords[0], coords[1] - componentSize[1])
		elif tieTo == Location.LEFT:
			return (coords[0], coords[1] - componentSize[1] / 2)
		elif tieTo == Location.CENTER:
			return (coords[0] - componentSize[0] / 2, coords[1] - componentSize[1] / 2)

class Container(Component):
	
	def __init__(self, **args):
		self.loc = (0, 0)
		self.updated = False
		self.childOrientations = {}
		self.childPositions = {}
	
	def add(self, component, location):
		self.childOrientations[component] = location
	
	def 


Component(one = "hello")



def testComponent(component):
	
	pygame.init()
	screen = pygame.display.set_mode((500, 500), DOUBLEBUF | RESIZABLE)