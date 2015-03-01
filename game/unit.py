import pygame, math, sys, random

#constants
MAXROLL = 20

history = []
positiveAbilities = ["leadership", "morale", "fortify"] #order matters
negativeAbilities = ["chaos", "fear", "siege"] #order matters

def dMax(dict1, dict2, val):
	if val in dict1 and val in dict2:
		return max(dict1[val], dict2[val]
	elif val in dict1:
		return dict1[val]
	elif val in dict2:
		return dict2[val]
	else:
		return 0

class Unit:
	
	def __init__(self, strength, hits, abilities, move):
		self.max_moves = move
		self.moves = move
		self.strength = strength
		self.hits = hits
		self.abilities = abilities
	
	def faceEnemy(self, enemy):
		if "assassin" in self.abilities:
			self.curAss = self.abilities["assassin"]
			if "assassin" in enemy.abilities:
				self.curAss -= enemy.abilities["assassin"]
		else:
			self.curAss = 0
		self.curArrows -= enemy.curArrows
		
	
	#assumes calc_abilities has been called on both group and enemies
	def enterBattle(self, group, enemies, terrain, attacker):
		self.curHits = self.hits
		self.curStrength = self.strength
		for i in range(len(positiveAbilities)):
			self.curStrength += max(-1, min(3, group.abilities[positiveAbilities[i]] - enemies.abilities[negativeAbilities[i]]))
		self.curStrength = max(1, min(self.strength + 5, self.curStrength))
		if terrain in self.abilities:
			self.curStrength += self.abilities[terrain]
		if "cityAttacker" in self.abilities and terrain == "city" and attacker:
			self.curStrength += self.abilities["cityAttacker"]
		if "cityDefender" in self.abilities and terrain == "city" and not attacker:
			self.curStrength += self.abilities["cityDefender"]	
		
		if "hits" in group.abilities:
			self.curHits += group.abilities["hits"]
		if "arrows" in self.abilities:
			self.curArrows = self.abilities["arrows"]
		else:
			self.curArrows = 0
			

class Group:
	
	def __init__(self, units, loc):
		self.units = units
		self.calc_abilities()
		self.calc_moves()
		self.loc = loc
	
	def calc_abilties(self):
		self.abilities = {}
		for unit in self.units:
			for ability in positiveAbilities + negativeAbilities:
				self.abilities[ability] = dMax(self.abilities, unit.abilities, ability)
			if "all_fly" not in self.abilities:
				if "flying" not in unit.abilities and "hero" not in unit.abilities:
					self.abilities["flying"] = False #ground unit
			if "flying" in unit.abilities:
				if "flying" not in self.abilities:
					self.abilities["flying"] = True #flyer
				if "all_fly" in unit.abilities:
					self.abilities["all_fly"] = True
					self.abilities["flying"] = True #wind-walker
		if "flying" not in self.abilities:
			self.abilities["flying"] = False #hero alone
			
	def order_for_battle(self, enemies, attacker):
		if attacker: loc = self.loc
		else: loc = enemies.loc
		for unit in units:
			unit.enter_battle(self, enemies, loc, attacker)
		
#returns (result, target, animation)
def strike(u1, u2):
	rand1 = random.random()
	rand2 = random.random()
	if u1.curAss > 0:
		if rand1 < u1.curAss / 10.0:
			return ("death", u2, "assassin")
		u1.curAss = 0
		return ("miss", None, None)
	if u2.curAss > 0:
		if rand2 < u2.curAss / 10.0:
			return ("death", u1, "assassin")
		u2.curAss = 0
		return ("miss", None, None)
	
	hit1 = rand1 * MAXROLL <= u1.curStrength
	hit2 = rand2 * MAXROLL <= u2.curStrength
	if u1.curArrows > 0:
		u1.curArrows -= 1
		if hit1 and not hit2:
			return ("death", u2, "arrows")
		return ("miss", None, None)
	if u2.curArrows > 0:
		u2.curArrows -= 1
		if hit2 and not hit1:
			return ("death", u1, "arrows")
		return ("miss", None, None)
	
	if hit1 and not hit2:
		if u2.curHits < 2:
			return ("death", u2, "normal")
		else:
			u2.curHits -= 1
			return ("hit", u2, "normal")
	if hit2 and not hit1:
		if u1.curHits < 2:
			return ("death", u1, "normal")
		else:
			u1.curHits -= 1
			return ("hit", u1, "normal")
	return ("miss", None, None)

#returns target of first killing strike + chain of animations
def fight_units(u1, u2):
	u1.face_enemy(u2)
	u2.face_enemy(u1)
	animations = []
	while 1:
		res = strike(u1, u2)
		if res[2]:
			animations.append(res)
		if res[0] == "death":
			return (res[1], animations)

#g1 is attacker. Return (winner, animations)
def fight_battle(g1, g2):
	g1.order_for_battle()
	g2.order_for_battle()
	animations = []
	while g1.units and g2.units:
		u1 = g1.units[0]
		u2 = g2.units[0]
		res = fight_units(u1, u2)
		if res[0] == u1:
			g1.units = g1.units[1:]
			history.append(Record(u1, (u2, res[1][-1])))
		else:
			g2.units = g2.units[1:]
			history.append(Record(u2, (u1, res[1][-1])))
		animations += res[1]
	if g1.units:
		return (g1, animations)
	return (g2, animations)
	

class Record:
	
	def __init__(self, unit, death):
		self.unit = unit
		self.death = death