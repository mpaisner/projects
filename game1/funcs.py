'''
SOL Function needs:

1) Constant increase/decrease in output. *ConstantOutputChange

2) Constant reduction in cost. *ConstantCostChange

3) % reduction in cost over a segment. *ConstantPercentCostChange

4) % reduction in cost centered at a point and decreasing constantly in value with distance from that point in both directions. *TwoWayPercent
	
	A) Must have coefficient for decrease speed.
	
	B) Must have a default option to disable changes when % < 0.

5) % reduction in cost centered at a point and decreasing quadratically in value with distance from that point in both directions. *Not implemented
	
	A) Must have coefficient for decrease speed (squared).
	
	B) Must have a default option to disable changes when % < 0.
	
	C) Should calculate most/all values when initialized.
	
6) % reduction in cost centered at a point and decreasing exponentially with the distance from that point. *TwoWayPercent + *ExpReducePercentCostChange

	A) Must have coefficient for decrease speed.
	
	B) Must consider center point to be distance 1. so 1 away from center point produces (1/(2 ^ coefficient)) * (effect value)
	
	C) Should calculate most/all values when initialized, and define a maximum distance beyond which effects are small enough to be ignored.

7) Was redundant.

8) % reduction in cost starting at a point and increasing or decreasing constantly to another point. *ConstReducePercentCostChange

	A) End point can be open-ended.
	
9) 8, but with quadratic increase/decrease *Quadratic not implemented

10) Pinning cost at a point to a certain value. *SetCost

11) Setting minumum or maximum cost at a point to a certain value. *SetMin, *SetMax

12) 2-9, but with cost increases rather than reductions. *'increasing' option

13) Reducing/increasing cost by constant, increasing/decreasing over interval *several ConstCostChange classes


Note: All effects must have precedence that determines order of application.
Note: Each turn, the cost of each level must be paid before any higher level can be reached.
'''

import math

#Decrease types
CONST = 0
CONST_PERCENT = 1
QUAD_PERCENT = 2
EXP = 3

class Interval:
	
	minval = 0.01
	
	def __init__(self, start, startval, decreasetype, decreaseval, fixedwidth = None, reverse = False):
		self.start = start
		self.startval = startval
		self.decreasetype = decreasetype
		self.decreaseval = decreaseval
		self.fixedwidth = fixedwidth
		self.vals = [startval]
		self.currentpercent = 1.0
		self.reverse = reverse
		self.get_vals()
	
	def last_val(self):
		return self.vals[-1]
	
	#might optimize by creating different classes to implement this method.
	def next_val(self):
		lastval = self.last_val()
		if self.decreasetype == CONST:
			return math.copysign(max(0, abs(lastval) - abs(self.decreaseval)), lastval)
		elif self.decreasetype == CONST_PERCENT:
			self.currentpercent -= self.decreaseval
			return self.startval * self.currentpercent
		elif self.decreasetype == QUAD_PERCENT:
			return self.startval * (1 - (self.decreaseval * (len(self.vals) ** 2)))
		elif self.decreasetype == EXP:
			return lastval * self.decreaseval
	

class OneWayInterval(Interval):
	
	def get_vals(self):
		if self.fixedwidth:
			while len(self.vals) <= self.fixedwidth:
				self.vals.append(self.next_val())
		else:
			while True:
				next = self.next_val()
				if next < self.minval:
					break
				self.vals.append(next)
		if self.reverse:
			self.vals = self.vals[::-1]

#start refers to the centerpoint; width is the one-way width (so actually half interval width)	
class CenteredInterval(Interval):
	
	def get_vals(self):
		rightinterval = OneWayInterval(self.start, self.startval, self.decreasetype, self.decreaseval, self.fixedwidth, False)
		self.vals = rightinterval.vals[::-1] + rightinterval.vals[1:]
		

class ConstantOutputChange:
	
	def __init__(self, precedence, tags, val):
		self.val = val
		self.precedence = precedence
		self.tags = tags
	
	def apply(self, output):
		return output + val

class ConstantCostChange:

	minconstchange = 0.01 #not used currently
	
	def __init__(self, precedence, tags, val, start, end):
		self.interval = OneWayInterval(start, val, CONST, 0, end - start)
		self.precedence = precedence
		self.tags = tags
	
	def apply(self, vals):
		retvals = list(vals)
		for i in range(min(len(self.interval.vals), len(vals) - self.interval.start)):
			retvals[i + self.interval.start] += self.interval.vals[i]
		return retvals

class UniversalConstantCostChange(ConstantCostChange):
	
	def __init__(self, precedence, tags, val, maxlen):
		self.interval = OneWayInterval(0, val, CONST, 0, maxlen)
		self.precedence = precedence
		self.tags = tags

class ConstReduceConstCostChange(ConstantCostChange):
	
	def __init__(self, precedence, tags, maxval, start, decval, increasing, width = None):
		self.interval = OneWayInterval(start, maxval, CONST, decval, fixedwidth = width, reverse = increasing)
		self.precedence = precedence
		self.tags = tags

class PercentReduceConstCostChange(ConstantCostChange):
	
	def __init__(self, precedence, tags, maxval, start, decval, increasing, width = None):
		self.interval = OneWayInterval(start, maxval, CONST_PERCENT, decval, fixedwidth = width, reverse = increasing)
		self.precedence = precedence
		self.tags = tags

class ExpReduceConstCostChange(ConstantCostChange):
	
	def __init__(self, precedence, tags, maxval, start, decval, increasing, width = None):
		self.interval = OneWayInterval(start, maxval, EXP, decval, fixedwidth = width, reverse = increasing)
		self.precedence = precedence
		self.tags = tags

class PercentCostChange:
	
	def apply(self, vals):
		retvals = list(vals)
		for i in range(min(len(self.interval.vals), len(vals) - self.interval.start)):
			retvals[i + self.interval.start] *= (1 - self.interval.vals[i])
		return retvals

class ConstantPercentCostChange(PercentCostChange):
	
	def __init__(self, precedence, tags, val, start, end):
		self.interval = OneWayInterval(start, -val, CONST, 0, end - start)
		self.precedence = precedence
		self.tags = tags

class ConstReducePercentCostChange(PercentCostChange):
	
	def __init__(self, precedence, tags, maxval, start, decval, increasing, width = None):
		self.interval = OneWayInterval(start, -maxval, CONST, decval, reverse = increasing, fixedwidth = width)
		self.precedence = precedence
		self.tags = tags

class PercentReducePercentCostChange(PercentCostChange):
	
	def __init__(self, precedence, tags, maxval, start, decval, increasing, width = None):
		self.interval = OneWayInterval(start, -maxval, CONST_PERCENT, decval, fixedwidth = width, reverse = increasing)
		self.precedence = precedence
		self.tags = tags

class ExpReducePercentCostChange(PercentCostChange):

	def __init__(self, precedence, tags, maxval, start, decval, increasing, width = None):
		self.interval = OneWayInterval(start, maxval, EXP, decval, fixedwidth = width, reverse = increasing)
		self.precedence = precedence
		self.tags = tags
	
	def apply(self, vals):
		retvals = list(vals)
		for i in range(min(len(self.interval.vals), len(vals) - self.interval.start)):
			retvals[i + self.interval.start] *= self.interval.vals[i]
		return retvals

class TwoWayPercent(PercentCostChange):
	
	def __init__(self, righthalf):
		self.precedence = righthalf.precedence
		self.tags = righthalf.tags
		self.interval = righthalf.interval
		self.interval.vals = self.interval.vals[::-1] + self.interval.vals[1:]
		#changes start, adjusts for starts < 0
		newstart = max(0, self.interval.start - len(self.interval.vals) / 2)
		self.interval.vals = self.interval.vals[max(0, len(self.interval.vals) / 2 - self.interval.start):]
		self.interval.start = newstart

class TwoWayConst(ConstantCostChange):
	
	def __init__(self, righthalf):
		self.precedence = righthalf.precedence
		self.tags = righthalf.tags
		self.interval = righthalf.interval
		self.interval.vals = self.interval.vals[::-1] + self.interval.vals[1:]
		#changes start, adjusts for starts < 0
		newstart = max(0, self.interval.start - len(self.interval.vals) / 2)
		self.interval.vals = self.interval.vals[max(0, len(self.interval.vals) / 2 - self.interval.start):]
		self.interval.start = newstart

class SetCost:
	
	def __init__(self, precedence, tags, vals, start):
		self.precedence = precedence
		self.tags = tags
		self.vals = vals
		self.start = start
	
	def apply(self, vals):
		retvals = list(vals)
		for i in range(min(len(vals) - self.start, len(self.vals))):
			retvals[i + self.start] = self.vals[i]
		return retvals

class SetMin:
	
	def __init__(self, precedence, tags, vals, start):
		self.precedence = precedence
		self.tags = tags
		self.vals = vals
		self.start = start
	
	def apply(self, vals):
		retvals = list(vals)
		for i in range(min(len(vals) - self.start, len(self.vals))):
			if retvals[i + self.start] < self.vals[i]:
				retvals[i + self.start] = self.vals[i]
		return retvals

class SetMax:
	
	def __init__(self, precedence, tags, vals, start):
		self.precedence = precedence
		self.tags = tags
		self.vals = vals
		self.start = start
	
	def apply(self, vals):
		retvals = list(vals)
		for i in range(min(len(vals) - self.start, len(self.vals))):
			if retvals[i + self.start] > self.vals[i]:
				retvals[i + self.start] = self.vals[i]
		return retvals

class DiscreteFunction:
	
	def __init__(self, basecosts = None, numvals = 100, defval = 1):
		if basecosts:
			self.basecosts = basecosts
		else:
			self.basecosts = [defval for i in range(numvals)]
		self.orderedeffects = []
		self.outputeffects = []
		self.currentcosts = list(self.basecosts)
	
	def add_effect(self, neweffect):
		i = 0
		for effect in self.orderedeffects:
			if effect.precedence <= neweffect.precedence:
				i += 1
			else:
				break
		self.orderedeffects.insert(i, neweffect)
		return i
	
	def add_output_effect(self, neweffect):
		i = 0
		for effect in self.outputeffects:
			if effect.precedence <= neweffect.precedence:
				i += 1
			else:
				break
		self.orderedeffects.insert(i, neweffect)
		return i
	
	def remove_effect(self, effect):
		self.orderedeffects.remove(effect)
	
	def remove_effects(self, effects):
		self.orderedeffects = [effect for effect in self.orderedeffects + self.outputeffects if effect not in effects]
	
	def get_effects_by_tag(self, tag):
		return [effect for effect in self.orderedeffects + self.outputeffects if tag in effect.tags]
	
	def update(self, tags, neweffects):
		if not hasattr(tags, "__iter__"):
			tags = [tags]
		if not hasattr(neweffects, "__iter__"):
			neweffects = [neweffects]
		oldeffects = []
		for tag in tags:
			oldeffects += self.get_effects_by_tag(tag)
		self.remove_effects(oldeffects)
		for effect in neweffects:
			self.add_effect(effect)
		
	#will probably need to increase efficiency here at some point - keep record so not all calculations need to be redone.	
	def calc_costs(self):
		res = self.basecosts
		for effect in self.orderedeffects:
			res = effect.apply(res)
		self.currentcosts = res
		return res
	