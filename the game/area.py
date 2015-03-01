
def locEquals(obj, area):
	return obj.loc == area

def locInSet(obj, area):
	return obj.loc in area.locs

def neighborMovement(unit, start, dest):
	if dest in start.neighbors:
		return 1
	return False

class Area:

	def __init__(self, name, containsFunction, movementFunction, imageData):
		self.name = name
		self.containsFunction = containsFunction
		self.movementFunction = movementFunction
		self.imageData = imageData
	
	def __contains__(self, object):
		return self.containsFunction(object, self)
	
	def moveCost(self, unit, dest):
		return self.movementFunc(unit, self, dest)

class RiskStyleArea(Area):
	
	def __init__(self, name, imageData):
		Area.__init__(name, locEquals, neighborMovement, imageData)
