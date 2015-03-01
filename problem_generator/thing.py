
class Thing:
	
	#parents is a list
	'''
	essentially, everything is something else, but with exceptions. To wit:
	-For each parent, 4 types of exceptions
		(1) Attributes of the parent this type lacks
		(2) Attributes of this type the parent lacks
		(3) Atrributes of the parent this type may or may not have
		(4) Attributes of this type the parent may or may not have
	Examples:
		(1) Parent: Squirrel
			This type: Albino Squirrel
			Attribute: color = brown
		(2) As above, color = white
		(3) Parent = Town
			This type = Small town
			Attribute = Has hospital
		(4) As above, attribute = population is small
	
	Also, a parent may be used to represent relations that are not strictly hereditary. For example (using simplified attributes):
	
	Thing convicted_thief = Thing([#parent == person])
	convicted_thief.add_attribute(parent = person, type = 4, attr = "in_jail")
	convicted_thief.add_attribute(parent = person, type = 4, attr = "steals")
	Thing convicted_murderer = Thing([convicted_thief])
	convicted_murderer.add_attribute(parent = convicted_thief, type = 3, attr = "steals")
	convicted_murderer.add_attribute(parent = convicted_thief, type = 4, attr = "kills")
	
	'''
	def __init__(self, parents):
		self.parents = parents
		self.exceptions = {}
		for parent in parents:
	
	
class Action:
	
	'''
	All actions are descendants of one of the basic action types. Basic types:
		(1) Move(start, end)
			-generic version requires nothing and can move into any Thing that is capable of containing it, or near any Thing at all. By default, the first option will take precedence where possible.
		
		(2) Build(thing)
			-generic builds in current location and requires nothing. Unlike move, cannot be instantiated directly - the type of buildable object must be chosen.
	
	Actions can require resources and have side effects.
	'''