import random

MAX_ROLL = 100

def weightedRandomChoice(choiceWeights):
	total = sum(choiceWeights.values())
	stop = random.random() * total
	cur = 0.0
	for choice, weight in choiceWeights.items():
		cur += weight
		if cur > stop:
			return choice

def getTarget(unit, enemies, tacticsRating):
	targets = getTargetQuality(unit, enemies) 
	#returns {enemy: 1-centric quality > 0}
	targets = {target: quality ** tacticsRating for target, quality in targets.items()}
	return weightedRandomChoice(targets)

class Hit:
	
	def __init__(self, source, target, power):
		self.source = source
		self.power = power

def getHit(self, unit, target):
	#does not factor in number of attacks, since each attack may target a different enemy
	strength = unit.attributeValue("attack")
	if not strength:
		return None#unit has no attack ability
	strength = applyModifiers(unit, target, strength)
	power = strength - random.random() * MAX_ROLL
	if power >= 0:
		return Hit(unit, power)
	return None

def isKilled(unit, hit):
	if not hit:
		return False
	penetration = hit.power + random.random() * MAX_ROLL
	return not unit.hasAttribute("armor") or penetration > unit.attributeValue("armor")

class BattleRound:
	
	def __init__(self, sideOne, sideTwo, oneTactics):
		self.oneAlive = {UnitCopy(unit) for unit in sideOne}
		self.oneKilled = {}
		self.twoAlive = {UnitCopy(unit) for unit in sideTwo}
		self.twoKilled = {}
		self.oneTactics = oneTactics #tactics is zero-sum (actually 2-sum)
		#killed dict values are the killers.
	
	def propogate(self):
		'''
		creates a new round with only the live units remaining. This will not recalculate tactics ratings, or any modifiers.
		'''
		return BattleRound(self.oneAlive, self.twoAlive, self.oneTactics)
	
	def resolve(self, selector):
		for unit in self.oneAlive:
			if selector(unit):
				target = getTarget(unit, self.twoAlive, self.oneTactics)
				if isKilled(target, getHit(unit, target)):
					self.twoAlive.remove(target)
					self.twoKilled[target] = unit
		for unit in self.twoAlive | self.twoKilled.keys():
			if selector(unit):
				target = getTarget(unit, self.oneAlive, 2 - self.oneTactics)
				if isKilled(target, getHit(unit, target)):
					self.oneAlive.remove(target)
					self.oneKilled[target] = unit

class UnitCopy(Unit):
	
	'''
	Class used for freezing an 'image' of a unit. Exactly the same as the original unit, but contains a reference to that original and is immutable. A UnitCopy which is passed a copy will maintain a reference to the original, but have the values of the copy.
	'''
	
	def __init__(self, unit):
		if hasattr(unit, "parent"):
			#if unit is itself a copy
			self.parent = unit.parent
		else:
			self.parent = unit
		#copy values

def selectRanged(unit):
	return unit.hasAttribute("ranged") and unit.attributeValue("ranged") > 0

class Battle:
	
	#modifiers should have been added to units prior to starting battle
	def __init__(self, sideOne, sideTwo, oneTactics):
		self.sideOne = sideOne
		self.sideTwo = sideTwo
		self.oneTactics = oneTactics
		
		self.rounds = [BattleRound(sideOne, sideTwo, oneTactics)]
	
	def simulateRound(self, selector):
		self.rounds.append(self.rounds[-1].propogate())
		self.rounds[-1].resolve(selector)
			
	def applyEffect(self, selector, effect, livingOnly = True):
		'''
		This selector takes unit as input.
		'''
		if livingOnly:
			units = self.rounds[-1].oneAlive | self.rounds[-1].twoAlive
		else:
			units = self.sideOne | self.sideTwo
		for unit in units:
			if selector(unit):
				unit.addEffect(effect)
	
	def removeEffect(self, selector, livingOnly = True):
		'''
		This selector takes effect, unit as inputs.
		'''
		if livingOnly:
			units = self.rounds[-1].oneAlive | self.rounds[-1].twoAlive
		else:
			units = self.sideOne | self.sideTwo
		for unit in units:
			unit.removeEffects(effectSelector)

PERMANENT = 0 #effect will persist unless removed
BATTLE = 1 #effect will last until the battle ends
BATTLETURNS = 2 #effect will last n rounds of a battle
GAMETURNS = 3 #effect will last n rounds of game

class Duration:
	
	'''
	note that instant duration effects can be applied - they will simply not perform any reversal when they are removed.
	'''
	
	def __init__(self, type, num = -1):
		self.type = type
		self.num = num


class EffectType(self, name, applyFunction, reverseFunction):
	self.name = name
	self.applyFunction = applyFunction
	self.reverseFunction = reverseFunction

class Effect:
	
	def __init__(self, type, duration, start, source):
		self.type = type
		self.duration = duration
		self.start = start
		self.source = source
	
	def add(self, unit):
		unit.effects.add(self)
	
	def remove(self, unit):
		unit.effects.remove(self)
	
	def apply(self, attributes):
		self.type.applyFunction(attributes)		
	
	#may not use reverse.
	def reverse(self, unit):
		self.type.reverseFunction(self, unit.attributes)		
	
	def endsWithBattle(self):	
		return self.duration.type in [BATTLE, BATTLETURNS]
	
	def endsOnTurn(self, turn):
		return self.duration.type == GAMETURNS and self.duration.num <= turn - self.start
	
	def endsOnBattleRound(self, round):
		return self.duration.type == BATTLETURNS and self.duration.num <= round - self.start
	
	def __str__(self):
		return str(self.type)
	

class RuleSet:
	
	