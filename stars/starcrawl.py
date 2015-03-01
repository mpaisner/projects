

class SpaceLoc:
	
	error = 0.00001
	maxX = 1000
	maxY = 1000
	
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def loc(self):
		return (self.x, self.y)
		
	def __eq__(self, other):
		return abs(self.x - other.x) < self.error and abs(self.y - other.y) < self.error
	
	def __ne__(self, other):
		return not self == other
		
	#comparisons depend on magnitude of manhattan dist from 0.
	def __lt__(self, other):
		return self != other and self.x + self.y < other.x + other.y

	def __le__(self, other):
		return self == other or self.x + self.y < other.x + other.y
		
	def __gt__(self, other):
		return not self <= other
	
	def __ge__(self, other):
		return not self < other
		
class Galaxy:
	
	def __init__(self, size):
		self.size = size
		self.objects = {}
	
	def create_object(self, object, loc):
		self.objects[object] = SpaceLoc(loc[0], loc[1])
	
	def loc(self, pos):
		return SpaceLoc(pos[0], pos[1])
	
	def get_shift(self, start, dest, magnitude = None):
		if start == dest:
			return (0, 0)
		if not magnitude:
			magnitude = self.size[0] + self.size[1]
		shift = (dest.x - start.x, dest.y - start.y)
		fraction = min(1, magnitude / sqrt(shift[0] * shift[0] + shift[1] * shift[1]))
		return (shift[0] * fraction, shift[1] * fraction)		
	
	def get_end(self, start, shift):
		return SpaceLoc(start.x + shift[0], start.y + shift[1])
	
	def dest(self, object, shift):
		if object not in self.objects:
			raise Exception("Trying to calculate a shift for a nonexistent object")
		return get_end(self.objects[object], shift)
	
	def get_move(self, object, dest, magnitude):
		if object not in self.objects:
			raise Exception("Trying to calculate a move for a nonexistent object")
		start = self.objects[object]
		return get_end(start, get_shift(start, dest, magnitude))
	
	#moving to an object rather than location
	def get_move_to(self, object, target, magnitude):
		if target not in self.objects:
			raise Exception("Trying to calculate a move to a nonexistent object")
		return self.get_move(object, self.objects[target], magnitude)
	
	def in_galaxy(self, spaceloc):
		return spaceloc.x >= 0 and spaceloc.y >= 0 and spaceloc.x < self.size[0] and spaceloc.y < self.size[1]
	
	def fit_to_galaxy(self, spaceloc):
		if self._in_galaxy(spaceloc):
			return SpaceLoc(spaceloc.x, spaceloc.y)
		return SpaceLoc(min(max(spaceloc.x, 0), self.size[0] - SpaceLoc.error), min(max(spaceloc.y, 0), self.size[1] - SpaceLoc.error))
	
	#dest should be a SpaceLoc
	def move_to(self, object, dest):	
		self.objects[object] = dest

def is_moving(item):
	return hasattr(item, "dest") and item[dest]

