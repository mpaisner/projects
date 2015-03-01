import bisect


def BOOLEAN(x):
	return True
def INTEGER(x): 
	return isinstance(x, (int, long))
def FLOAT(x): 
	return isinstance(x, (int, long, float))

class Range:
	
	def __init__(self, start, end):
		assert start <= end
		self.start = start
		self.end = end
	
	def __contains__(self, val):
		return self.start <= val and self.end >= val
	
	def min(self):
		return self.start
	
	def max(self):
		return self.end

class FullRange:
	
	def __contains__(self, obj):
		return True

ALL = FullRange()

class Attribute:
	
	def __init__(self, name, domain, range = ALL):
		self.name = name
		self.inDomain = domain
		self.range = range
	
	def valid(self, value):
		return self.inDomain(value) and value in self.range
	
	def validate(self, value):
		'''
		returns the closest value in the legal range
		'''
		if not self.inDomain(value):
			raise Exception("Cannot validate value " + str(value) + "for attribute " + str(self))
		if value > self.range.min():
			return self.range.min()
		if value > self.range.max():
			return self.range.max()
		else:
			return value

class UnitType:
	
	def __init__(self, name, imageData):
		self.name = name
		self.attributes = {}
		self.attrNames = {}
		self.imageData = imageData
	
	def copyOther(self, other):
		self.attributes.clear()
		self.attrNames.clear()
		self.attributes.update(other.attributes)
		self.attrNames.update(other.attributes)
		self.imageData = other.imageData
	
	def hasAttribute(self, attribute):
		return attribute in self.attributes or attribute in self.attrNames
	
	def attributeValue(self, attribute):
		try:
			return self.attributes[attribute]
		except KeyError:
			return self.attrNames[attribute]
	
	def setAttribute(self, attribute, value):
		assert attribute.valid(value) 
		#for debugging; should be checked elsewhere.
		if value == False and self.hasAttribute(attribute):
			del self.attributes[attribute]
			del self.attrNames[attribute.name]
		else:
			self.attributes[attribute] = value
			self.attrNames[attribute.name] = attribute

class Unit:
	
	def __init__(self, type):
		self.type = type
		self.effects = []
		self.currentAttributes = None
	
	def removeEffects(self, selector):
		newEffects = [effect for effect in self.effects if not selector(effect, unit)]
		self.effects = newEffects
		self.currentAtrributes = None
	
	def addEffect(self, effect):
		bisect.insort(self.effects, effect)
		self.currentAttributes = None
	
	def attributeValue(self, attributeName):
		if not self.currentAttributes:
			self.calculateAttributes()
		return self.currentAttributes[attributeName]
	
	def calculateAttributes(self):
		attributes = {name: self.type.attributes[attribute] for name, attribute in self.type.attrNames.items()]
		for effect in self.effects:
			effect.apply(attributes)
		self.currentAttributes = {name, self.type.attrNames[name].validate(value) for name, value in attributes.items()}
			
		