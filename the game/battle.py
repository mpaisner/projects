import random

def roll(max, num = 1):
	val = 0
	for i in range(num):
		val += random.randrange(1, max)
	return val

class Hit:
	
	def __init__(self, src, target):
		self.src = src
		self.target = target

class UnitType:
	
	def __init__(self, args):
		self.args = args
	
	def __getattr__(self, attr):
		try:
			return self.args[attr]
		except KeyError:
			return None

class BattleUnit:
	
	battleDice = 6
	ATTACK_ATTR = 0
	DEFENSE_ATTR = 1
	ATTACKS = 2
	
	def __init__(self, type):
		self.type = type
	
	def __getattr__(self, attr):
		'''
		for most implementations, there will be attributes that can be different from the generic values for this type. For example, a veteran unit might have higher attack and defense. Those modificiations should be applied in this method after retrieving the generic value.
		'''
		typeVal = self.type[attr]
		return typeVal
	
	def swing(self, battle):
		if battle.isAttacker(self):
			strength = self[ATTACK_ATTR]
		elif battle.isDefender(self):
			strength = self[DEFENSE_ATTR]
		else:
			raise Exception("Unit not involved in battle")
		
		numAttacks = self[ATTACKS]
		if not numAttacks:
			numAttacks = 1 #default - must set 0 explicitly if desired.
		for i in range(numAttacks):
			if roll(self.battleDice) <= strength:
				battle.

class Location:
	
	def getBattleBkg(self):
		return None

class Battle:
	
	def __init__(self, location):
		self.location = location
		self.attackers = []
		self.defenders = []
		self.outstandingHits = []
	
	def isAttacker(self, unit):
		return unit in self.attackers
	
	def isDefender(self, unit):
		return unit in self.defenders
	
	def addHit(self, hit):
		self.outstandingHits.append(hit)
	
	def applyHit(self):
		

class BattleDisplay(self, battle):
	