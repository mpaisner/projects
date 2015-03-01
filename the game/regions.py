

class Region:
	
	def __init__(self, name):
		self.name = name
		self.armies = set() #an army contains 1-n units.
		self.buildings = set() #the buildings should contain info on the number that have been built, if applicable.
	
	def calcProduction(self):
		raise NotImplementedException()
	
	def battle(self, attackers):
		raise NotImplementedException()
		#creates a battle object pitting the attackers against territory defenders.

class BattleScene:
	
	def __init__(self