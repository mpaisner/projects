from expr import *

class Time:
	
	def __init__(self, initial = 0):
		self.time = initial
	
	def step(self, steps = 1):
		self.time += steps
	
	def get_time(self, agent):
		return self.time
	
	def __add__(self, other):
		if isinstance(other, Time):
			return Time(self.get_time() + other.get_time())
		elif isinstance(a, int):
			return Time(self.get_time() + other)
	
	def __sub__(self, other):
		if isinstance(other, Time):
			return Time(self.get_time() - other.get_time())
		elif isinstance(a, int):
			return Time(self.get_time() - other)
	
	def __eq__(self, other):
		return self.get_time == other.get_time

THE_TIME = Time()
	
class CurrentTimePlus(Time):
	
	def __init__(self, plus):
		self.plus = plus
	
	def get_time(self, agent):
		return agent.get_current_time() + self.plus

class BeliefTime:
	
	def __init__(self, decs):
		self.decs = decs
	
	def get_strength(self, initialStrength, elpasedTime):
		dec = 0
		for inc in self.decs:
			if elapsedTime > inc:
				dec += 1
		if initialStrength < 0:
			return min(initialStrength + dec, 3)
		return max(initialStrength - dec, -3)

class Descriptor:
	
	def __init__(self, name, subject, args):
		self.name = name
		self.subject = subject
		self.args = args
	
	def get_keys():
		return [self.name, self.subject] + self.args
		
	def __eq__(self, other):
		return type(self) == type(other) and self.name == other.name and self.subject == other.subject and self.args == other.args

class Has(Descriptor):
	
	name = "has"
	
	def __init__(self, haver, item):
		self.subject = haver
		self.args = [item]

class SimpleAction:

	def __init__(self, preconds, results):
		self.preconds = preconds
		self.results = results

	def doable(self, args, time):
		likelihood = 0.0
		for precond in preconds:
			likelihood += args[0].believes(precond.get_descriptor(args), time = time)
		return likelihood / len(preconds)
	
	def __eq__(self, other):
		return type(self) == type(other) and self.preconds == other.preconds and self.results == other.results

class CompoundAction:
	
	def __init__(self, actions):
		self.actions = actions

class SimpleEvent:
	
	def __init__(self, action, args, time):
		self.action = action
		self.args = args
		self.time = time
	
	def __eq__(self, other):
		return type(self) == type(other) and self.action == other.action and self.args == other.args and self.time == other.time
	
	def get_keys(self):
		return [self.action] + self.args

class BeliefSource:
	
	def __init__(self, type, instance):
		self.type = type
		self.instance = instance
	
	def __eq__(self, other):
		return type(self) == type(other) and self.instance == other.instance

class Belief:
	
	def __init__(self, fact, time, source):
		self.fact = fact
		self.lastUpdate = time
		self.justifications = {source: time}
		self.strength = self.get_strength()
	
	def get_strength(self, depth = 1):
		#elaborate later
		if depth < 1:
			return self.strength
		strength = 0
		for just in self.justifications:
			strength += just.strength(depth - 1)
		self.strength = strength
		return strength
	
	def has_pred(self, predicate):
		for atom in self.fact.all_atoms():
			if atom.predicate == predicate:
				return True
		return False
	
	def __eq__(self, other):
		return type(self) == type(other) and self.fact == other.fact and self.time == other.time and self.source == other.source and self.strength == other.strength

class Justification:
	
	pass

class MPJustification(Justification):
	
	def __init__(self, agent, cond, ps, q):
		self.agent = agent
		self.cond = cond
		self.ps = ps
		self.q = q
	
	def valid(self, p):
		if self.cond.beliefLevel <= 0:
			return None #negated conditionals cannot be used in MP
		if not self.cond[1].same_belief(self.q):
			cond = self.cond.replace_to_match(self.q, self.cond[1])
		else:
			cond = self.cond
		if not cond or not cond.same_belief(self.q):
			raise Exception("MPJustification does not fit result")
		if cond[0].same_belief(p):
			return True
		else: #if condp is an EXISTS quantifier and p is an example
			condp = cond[0].replace_to_match(p, cond[0], types = [EXISTS])
			if condp and condp.same_belief(p):
				return True
		return False		
	
	def strength(self, depth = 0):
		strength = 0
		for p in self.ps:
			if self.valid(p):
				strength += self.agent.evaluate_belief(p, depth)
				#this should not be simple addition in final version
		return max(0, min(strength, self.cond.beliefStrength))
			
	

class Evaluation:
	
	def __init__(self, agent, belief, source):
		self.agent = agent
		self.belief = belief
		self.irrelevant = set()
		self.relevant = set()
		self.justifications = set()
		if source:
			self.justifications.add(source)
		self.lastCheck = -1
	
	def check(self, maxops, maxdepth, time):
		pass

class BeliefSet:
	
	def __init__(self, baseSet = {}):
		self.beliefs = baseSet.copy()
		self.currentBeliefs = None
	
	def add(self, key, belief):
		if key in self.beliefs:
			self.beliefs[key].append(belief)
		else:
			self.beliefs[key] = [belief]
	
	#ck = common knowledge
	def add_ck(self, expr, time, source, strength):
		keys = expr.get_keys()
		#keys.append(source.instance)
		belief = Belief(expr, time, source, strength)
		self.add("time", belief)
		for key in keys:
			self.add(key, belief)
	
	def add_descriptor(self, descriptor, time, source, strength):
		keys = []
		keys += descriptor.get_keys()
		keys.append(source.instance) #not source.type since those are general
		belief = Belief(descriptor, time, source, strength)
		self.add("time", belief)
		for key in keys:
			self.add(key, belief)
	
	def add_event_memory(self, event, time, source, strength):#*
		keys = []
		keys += event.get_keys()
		keys.append(source.instance) #not source.type since those are general
		belief = Belief(event, time, source, strength)
		self.add("time", belief)
		for key in keys:
			self.add(key, belief)
		
	def get_relevant_beliefs(self, keys):
		beliefs = []
		for key in keys:
			if key in self.beliefs:
				beliefs += self.beliefs[key]
		return beliefs
	
	def get_beliefs_with_pred(self, beliefs, predicate):
		return [belief for belief in beliefs if belief.has_pred(predicate)]
	
	#returns an expression that must be true for belief to prove atom. Implementing to work only with conditonals that have the relevant atom as either entire if or entire then at first.
	def get_conds_for_proof(self, atom, belief):
		fact = belief.fact
		conds = []
		if fact.kind == CONDITIONAL:
			if fact[0].kind == ATOM and fact[0].predicate == atom.predicate:
				matchedExpr = fact.replace_to_match(atom, fact[0])
				if matchedExpr:
					conds.append(Expression(NOT, [matchedExpr[1]])) #Modus Tolens
			elif fact[1].kind == ATOM and fact[1].predicate == atom.predicate:
				matchedExpr = fact.replace_to_match(atom, fact[1])
				if matchedExpr:
					conds.append(matchedExpr[0]) #Modus Ponens
		return conds
					
	def test_proof(self):
		furry = Atom("furry", [QuantifiedVar(FORALL, "v1")])
		dog = Atom("dog", [QuantifiedVar(FORALL, "v1")])
		dogsAreFurry = Expression(CONDITIONAL, [dog, furry])
		fidoFurry = Atom("furry", [Item("fido")])
		fidoDog = Atom("dog", [Item("fido")])
		self.add_ck(dogsAreFurry, 0, None, "+++")
		conds = self.get_conds_for_proof(fidoFurry, Belief(dogsAreFurry, 0, None, "+++"))
		print conds[0]
		print conds[0].evaluate(self)
		conds = self.get_conds_for_proof(fidoDog, Belief(dogsAreFurry, 0, None, "+++"))
		print conds[0].kind, conds[0][0]
		print conds[0].evaluate(self)
	
	#should return list of +/-, list of of corresponding source beliefs.
	def evaluate_atom(self, atom):
		if not self.currentBeliefs:
			self.currentBeliefs = self.get_relevant_beliefs(atom.get_keys())
		relevant = self.get_beliefs_with_pred(self.currentBeliefs, atom.predicate)
		
		

bs = BeliefSet()
bs.test_proof()

	
		
	#*time refers to the time when the MEMORY happened, not the event. So a memory that someone else told an agent about at time 10 would have time = 10 here, though event.time would be earlier. Another event would be remembered, the event of the other agent talking about the original event. That event would have time = 10 and event.time = 10, with source as direct observation, strength = '+++'


class Agent:

	def __init__(self):
		self.memory = BeliefSet()
	
	def get_relevant_facts(self, arg):
		pass#keys = 
	
	def discover_descriptor_truth(self, descriptor):
		pass
	
	def get_current_time(self):
		return THE_TIME
	
	def believes(self):
		pass