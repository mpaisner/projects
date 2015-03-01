#distinguish between dif types: 1) Exception, 2) Addition
class Thing:
	
	def __init__(self, parents, difsets):
		if len(parents) != len(difsets):
			raise Exception("Invalid construct")
		self.classes = {}
		index = 0
		for parent in parents:
			self.classes[parent] = difsets[index]
			index += 1

class Trait:
	
	def __init__(self, type, args):
		self.type = type
		self.args = args

OBJECT = Thing([], [])

#simple to start - needs to be adjusted to really make sense
def difference(first, second):
	if first == second:
		return 0
	difs = []
	if first == OBJECT:
		for parent in second.classes:
			dif = difference(first, parent)
			for dif1 in second.classes[parent]:
				dif += 1
			difs.append(dif)
	elif second == OBJECT:
		for parent in first.classes:
			dif = difference(second, parent)
			for dif1 in first.classes[parent]:
				dif += 1
			difs.append(dif)
	else: #neither is a base OBJECT
		for parent1 in first.classes:
			for parent2 in second.classes:
				dif = difference(parent1, parent2)	
				for dif1 in first.classes[parent1]:
					if dif1 not in second.classes[parent2]:
						dif += 1
				for dif2 in second.classes[parent2]:
					if dif2 not in first.classes[parent1]:
						dif += 1
				difs.append(dif)
	print difs, first.classes, second.classes
	return min(difs)

#properties and things
alive = Trait("capability", ["live"])
microscopic = Trait("size", ["microscopic"])
livingThing = Thing([OBJECT], [[alive]])
cell = Thing([livingThing], [[microscopic]])
hasCells = Trait("hasQuantity", [cell, "many"])
complexOrganism = Thing([livingThing], [[hasCells]])
photosynthesis = Trait("capabiliy", ["photosynthesis"])
plant = Thing([complexOrganism], [[photosynthesis]])
animal = Thing([complexOrganism], [[]])

print difference(complexOrganism, cell)
#need to find closest common ancestor, rather than haphazard current method.