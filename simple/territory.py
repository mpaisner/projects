import random
DICE_VAL = 6


class Territory:
	
	def __init__(self, name):
		self.name = name
		self.units = 0
		self.player = None
		self.neighbors = []
	
	def add_neighbor(self, neighbor):
		self.neighbors.append(neighbor)
	
	def can_attack(self, other):
		return other in self.neighbors and other.player != self.player
	
	def attack_result(self, other, attDice, defDice):
		attRolls = []
		defRolls = []
		for i in range(attDice):
			attRolls.append(random.nextint(DICE_VAL))
		for i in range(defDice):
			defRolls.append(random.nextint(DICE_VAL))
		attRolls.sort()
		defRolls.sort()
		res = [0, 0]
		while attRolls and defRolls:
			if attRolls.pop() > defRolls.pop():
				res[0] += 1
			else:
				res[1] += 1
		return res
	
	def apply_attack(self, other, res):
		self.units -= res[0]
		other.units -= res[1]
	
	def takeover(self, other, units):
		if other.units > 0:
			raise Exception("cannot take over territory with units left")
		if self.units <= units:
			raise Exception("cannot take over with more units than present")
		if other not in self.neighbors:
			raise Exception("cannot take over non-neighbor")
		self.units -= units
		other.units = units
		other.player = self.player
			
	
class Continent:
	
	def __init__(self, name, value, color, rgbVariance):
		self.name = name
		self.value = value
		self.color = color
		self.variance = rgbVariance
		self.territories = {}
	
	def get_new_color(self):
		return (self.color[0] + 2 * self.variance[0] * (random.random() - 0.5), self.color[1] + 2 * self.variance[1] * (random.random() - 0.5), self.color[2] + 2 * self.variance[2] * (random.random() - 0.5))
	
	def add_territory(self, terr):
		self.territories[terr.name] = terr
	
	def is_held(self, player):
		for terr in self.territories.values():
			if terr.player != player:
				return False
		return True