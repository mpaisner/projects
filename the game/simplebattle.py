import random


#traits
TRAIT_TOHIT = 0
TRAIT_POWER = 1
TRAIT_ARMOR = 2
TRAIT_NUM_ATTACKS = 3
TRAIT_ATTACK = 4
TRAIT_DEFENSE = 5

#roles
ROLE_ATTACK = 0
ROLE_DEFENSE = 1

#condition keys
BATTLE_ROLE = 0

class Dice:
	
	def getChance(self, *args):
		raise Exception("Get Chance method not implemented")
	
	def roll(self):
		raise Exception("Roll not method implemented")
	
	def success(self, *args):
		raise Exception("success method not implemented")

class Attack:
	
	def __init__(self, id, unit, target, hitScore):
		self.id = id
		self.unit = unit
		self.target = target
		self.hitScore = hitScore

class Hit:
	
	def __init__(self, attack, dmgScore):
		self.id = attack.id
		self.unit = attack.unit
		self.target = attack.target
		self.dmgScore = attack.dmgScore

class Wound:
	
	def __init__(self, hit, dmg):
		self.id = hit.id
		self.unit = hit.unit
		self.target = hit.target
		self.dmg = dmg

class Kill:
	
	def __init__(self, hit):
		self.id = hit.id
		self.unit = hit.unit
		self.target = hit.target

class RoundResult:
	
	def __init__(self, combatants, attacks, hits, wounds, kills):
		self.combatants = [combatant.copy() for combatant in combatants]
		self.attacks = attacks
		self.hits = hits
		self.wounds = wounds
		self.kills = kills

class RoundResultBuilder:

	'''
	Allows results to be fully calculated using simultaneous attacks
	then ordered to make animations sensical (i.e. dead units stop shooting)
	'''
	
	def __init__(self, combatants):
		self.combatants = combatants
		self.results = []	
	
	def finalize(self):
		attacks = [result[0] for result in self.results if result[0]]
		hits = [result[1] for result in self.results if result[1]]
		wounds = [result[2] for result in self.results if result[2]]
		kills = [result[3] for result in self.results if result[3]]
		return RoundResult(combatants, attacks, hits, wounds, kills)
	
	def order(self):
		pass
	
	def storeResult(self, attack = None, hit = None, wound = None, kill = None):
		self.results.append((attack, hit, wound, kill))

class Battle:
	
	def __init__(self, combatantsByRole, unitExposure, toHitDice, dmgDice):
		self.combatants = combatantsByRole
		self.exposure = unitExposure
		self.toHitDice = toHitDice
		self.dmgDice = dmgDice
		self.nextID = 1
		self.rounds = []
			
	def getDmgScore(self, unit, target, phase, role):
		try:
			powerScore = unit.get(POWER, phase, role)
		except KeyError:
			try:
				powerScore = unit.get(POWER, role)
			except KeyError:
				try:
					powerScore = unit.get(POWER, phase)
				except KeyError:
					try:
						powerScore = unit.get(POWER)
					except KeyError:
						powerScore = None
		if not powerScore:
			return None
		try:
			armorScore = unit.get(ARMOR, phase, role)
		except KeyError:
			try:
				armorScore = unit.get(ARMOR, role)
			except KeyError:
				try:
					armorScore = unit.get(ARMOR, phase)
				except KeyError:
					try:
						armorScore = unit.get(ARMOR)
					except KeyError:
						armorScore = None
		if not armorScore:
			return None
		return armorScore - powerScore
	
	def getHitScore(self, unit, target, phase, role):
		'''
		1 - hit probability does not depend on target
		2 - checks for ability scores from most to least specific
		'''
		try:
			score = unit.get(TOHIT, phase, role)
		except KeyError:
			try:
				score = unit.get(TOHIT, role)
			except KeyError:
				try:
					score = unit.get(TOHIT, phase)
				except KeyError:
					try:
						score = unit.get(TOHIT)
					except KeyError:
						score = None
		return score
	
	def getHitChance(self, hitScore):
		return self.toHitDice.getChance(score)
	
	def getWoundChance(self, dmgScore):
		return self.dmgDice.getChance(score)
	
	def processAttack(self, unit, target, phase, role):
		attack = Attack(self.nextID, unit, target, self.getHitScore(unit, target, phase, role))
		self.nextID += 1
		if not self.toHitDice.success(attack.hitScore):
			return attack,
		else:
			#hit
			hit = Hit(attack, self.getDmgScore(unit, target, phase, role))
			if not self.dmgDice.success(hit.dmgScore):
				return (attack, hit)
			else:
				wound = Wound(hit, 1)
				kill = Kill(hit)
				return (attack, hit, wound, kill)
	
	def processAttacks(self, unitsByRole, unitExposure, phase):
		'''
		next: each unit has a chance of being targeted. For simplicity and gameplay, this does not vary by attacker for now. So, next thing is to have a method to cycle through all units for attacker and defender and selected pseudo-random targets and process all attacks, storing the results in a RoundResultBuilder object:
		resBuilder.storeResult(*(self.processAttack(unit, target, role, phase)))
	
		Phase should be an input to this method, as should a dictionary of {role: unit}. for now the roles will only be attacker and defender, and each can only attack the other.	
		'''
		result = RoundResultBuilder(unitsByRole)
		attackers = unitsByRole[ATTACK]
		defenders = unitsByRole[DEFENSE]
		#attackers first	
		killed = set()
		defenderOdds = []
		for defender in defenders:
			try:
				defenderOdds += [defender] * unitExposure[defender]
			except KeyError:
				#assume chance = 1
				defenderOdds.append(defender)
		for attacker in attackers:
			for i in range(attacker.get(ATTACKS, phase, unitsByRole[attacker])):
				target = random.choice(defenderOdds)
				attack, hit, wound, kill = self.processAttack(attacker, target, phase, unitsByRole[attacker])
				if kill:
					killed.add(target)
					defenderOdds = [defender for defender in defenderOdds if defender != target]
				result.storeResult(attack, hit, wound, kill)
		return result
	
	def runRound(self, phase):
		result = self.processAttacks(self.combatants, h)
		pass


class SetScore:
	
	def __init__(self, func):
		self.func = func
	
	def apply(self, previous, **state):
		return self.func(**state)

class AddToScore:
	
	def __init__(self, func):
		self.func = func
	
	def apply(self, previous, **state):
		return previous + self.func(**state)

class MultScore:
	
	def __init__(self, func):
		self.func = func
	
	def apply(self, previous, **state):
		return previous * self.func(**state)

class Effect:
	
	def __init__(self, check, effect, order):
		self.check = check
		self.effect = effect
		self.order = order
	
	def __cmp__(self, other):
		return cmp(self.order, other.order)
	
	def applies(self, **state):
		return self.check(**state)
	
	def apply(self, previous, **state):
		return self.effect.apply(previous, **state)

def inState(key):	
	return lambda **state: key in state and state[key]

def And(checks):
	return lambda **state: not [True for check in checks if not check(**state)]

def Or(checks):
	return lambda **state: len([True for check in checks if check(**state)]) > 0

state = {'1': 1, '2': 2}
print Or([inState('1'), inState('2')])(**state)
print Or([inState('0'), inState('2')])(**state)
print Or([inState('0'), inState('3')])(**state)
	

ROLE_EFFECT = Effect(check = inState(BATTLE_ROLE), effect = SetScore(lambda **state: state[COND_BASE_ATTACK

def TraitEffect:
	
	def __init__(self, trait, check, effect, order):
		self.effect = Effect(check, effect, order)
		self.trait = trait
		self.order = order
	
	def __cmp__(self, other):
		return cmp(self.order, other.order)
	
	def applies(self, unit, **info):
		pass
		

class Interactable:
	
	def applyCondition(self, applier):
		self.state = applier(self.state)
	
	def doConditions(self):
		for condition in self.getConditions():
			condition.apply()
	
	def get(self, trait):
		val = trait.default
		for effect in trait.effects:
			if effect.applies(**state):
				val = effect.apply(val, **state)
		return val

class Condition:
	
	def __init__(self, targeter, applier, order):
		self.targeter = targeter
		self.applier = applier
		self.order = order
	
	def __cmp__(self, other):
		return cmp(self.order, other.order)
		
	def apply(self):
		for target in self.targeter():
			target.applyCondition(self.applier)

class Trait:
	
	def __init__(self, name, default, effects):
		self.name = name
		self.default = default
		self.effects = effects



class Unit(Interactable):
	
	def __init__(self, traits, attrs):
		self.traits = traits
		self.attrs = attrs
		self.traitEffects = getTraitEffects()
		
		self.applyEffects(orderedEffects)
	
	#call this once unless trait effects change
	def getTraitEffects(self):
		effects = []
		for trait in self.traits:
			effects += trait.effects
		effects.sort()
		return effects
	
	def attrsAsDict(self):
		pass
	
	def get(self, trait):
		return self.traits[trait]
	
	def applyEffects(self, orderedEffects):
		self.traits = {trait: 


