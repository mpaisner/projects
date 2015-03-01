import planner

class Location:

	#pass in dict of vals if house should be partly constructed.
	def __init__(self, name, type, loc, vals = None):
		self.name = name
		self.type = type
		self.loc = loc
		self.fire = False
		if type == "HOUSE":
			self.foundation = None
			self.walls = None
			self.roof = None
			if vals:
				if "foundation" in vals:
					self.foundation = vals["foundation"]
				if "walls" in vals:
					self.walls = vals["walls"]
				if "roof" in vals:
					self.roof = vals["roof"]
				if "fire" in vals:
					self.fire = vals["fire"]
	
class Material:
	
	types = ["CONCRETE", "WOOD", "BRICK", "SHINGLE"]
	
	def __init__(self, name, type, loc, used = True):
		self.name = name
		self.type = type
		self.loc = loc
		self.used = used

class Worker:
	
	types = ["CONSTRUCTION-WORKER", "FIREMAN", "TEAMSTER"]
	
	def __init__(self, name, type, loc):
		self.name = name
		self.type = type
		self.loc = loc
		if type == "FIREMAN":
			self.hosesloaded = False

class Executor:
	
	#This class is for eventually doing this the right way, with good error messages.
	def __init__(self, world):
		self.world = world
	
	def fail_msg(self, action, msg = None):
		s = "Action failed: ("
		for piece in action:
			s += piece + " "
		s = s[:-1] + ")"
		if msg:
			s += "\n" + msg
		return s
	
	def lay_foundation(self, action):
		if action[1] not in self.world.locations:
			raise Exception(self.fail_msg(self, action, "house " + action[1] + " DNE."))
		house = self.world.locations[action[1]]
		if action[2] not in self.world.materials:
			raise Exception(self.fail_msg(self, action, "material " + action[2] + " DNE."))
		material = self.world.materials[action[2]]
		if action[3] not in self.world.workers:
			raise Exception(self.fail_msg(self, action, "worker " + action[3] + " DNE."))
		worker = self.world.workers[action[3]]
		#got items, now check if they fit
		if house.walls:
			raise Exception(self.fail_msg(self, action, "house " + house.name + " has walls."))
		if house.foundation:
			raise Exception(self.fail_msg(self, action, "house " + house.name + " has a foundation."))
	
	def execute_action(self, action):
		for i in range(len(action)):
			action[i] = action[i].lower()
		if action[0] == "lay-foundation":
			self.lay_foundation(action)
		

class HouseWorld:

	
	def __init__(self, objects, state):
		#get locations first
		self.locations = {}
		self.locations["hq"] = Location("hq", "HQ", (0, 0))
		for conjunct in objects:
			if conjunct[-1] == "HOUSE":
				for house in conjunct[:-1]:
					self.locations[house] = Location(house, "HOUSE", (0, 0))
		
		#get materials
		self.materials = {}
		for conjunct in objects:
			if conjunct[-1] in Material.types:
				for material in conjunct[:-1]:
					self.materials[material] = Material(material, conjunct[-1], None)
		
		#get workers
		self.workers = {}
		for conjunct in objects:
			if conjunct[-1] in Worker.types:
				for worker in conjunct[:-1]:
					self.workers[worker] = Worker(worker, conjunct[-1], None)
		
		#implement state
		for conjunct in state:
			if conjunct[0] == "at":
				if conjunct[1] in self.materials:
					self.materials[conjunct[1]].loc = self.locations[conjunct[2]]
				else: #in self.workers, or there is a mistake
					self.workers[conjunct[1]].loc = self.locations[conjunct[2]]
			elif conjunct[0] == "has-foundation":
				self.locations[conjunct[1]].foundation = True
			elif conjunct[0] == "has-roof":
				self.locations[conjunct[1]].roof = True
			elif conjunct[0] == "has-brick-walls":
				self.locations[conjunct[1]].walls = "BRICK"
			elif conjunct[0] == "has-wood-walls":
				self.locations[conjunct[1]].walls = "WOOD"
			elif conjunct[0] == "on-fire":
				self.locations[conjunct[1]].fire = True
			elif conjunct[0] == "hoses-loaded":
				self.workers[conjunct[1]].hosesloaded = True
			elif conjunct[0] == "unused":
				self.materials[conjunct[1]].used = False
		
		self.goals = None
	
	def has_worker_type(self, type):
		for worker in self.workers.values():
			if worker.type == type:
				return True
		return False
	
	def has_material_type(self, type):
		for material in self.materials.values():
			if material.type == type:
				return True
		return False
	
	def get_obj_str(self):
		s = "\t\t\t(objects\n"
		if len(self.locations) > 1:
			s += "\t\t\t\t("
			for location in self.locations.values():
				if location.type == "HOUSE":
					s += location.name + " "
			s += "HOUSE)\n"
		for type in Worker.types:
			if self.has_worker_type(type):
				s += "\t\t\t\t("
				for worker in self.workers.values():
					if worker.type == type:
						s += worker.name + " "
				s += type + ")\n"
		for type in Material.types:
			if self.has_material_type(type):
				s += "\t\t\t\t("
				for material in self.materials.values():
					if material.type == type:
						s += material.name + " "
				s += type + ")\n"
		s += "\t\t\t)\n"	
		return s
	
	def get_state_conjuncts(self):
		state = []
		for location in self.locations.values():
			if location.type == "HOUSE":
				if location.foundation:
					state.append(["has-foundation", location.name])
				if location.roof:
					state.append(["has-roof", location.name])
				if location.walls == "BRICK":
					state.append(["has-brick-walls", location.name])
				if location.walls == "WOOD":
					state.append(["has-wood-walls", location.name])
				if location.fire:
					state.append(["on-fire", location.name])
				if location.foundation and location.roof and location.walls and (not location.fire):
					state.append(["complete", location.name])
		for material in self.materials.values():
			if material.loc:
				state.append(["at", material.name, material.loc.name])
			if not material.used:
				state.append(["unused", material.name])
		for worker in self.workers.values():
			if worker.loc:
				state.append(["at", worker.name, worker.loc.name])
			if worker.type == "FIREMAN" and worker.hosesloaded:
				state.append(["hoses-loaded", worker.name])
		return state
	
	def get_state_str(self):
		state = self.get_state_conjuncts()
		s = "\t\t\t(state\n\t\t\t\t(and\n"
		for conjunct in state:
			s += "\t\t\t\t\t("
			for piece in conjunct:
				s += piece + " "
			s = s[:-1] + ")\n"
		s += "\t\t\t\t)\n\t\t\t)\n"
		return s
	
	def get_goal_str(self):
		if not self.goals:
			return ""
		s = "\t\t\t(goal\n\t\t\t\t(and\n"
		for goal in self.goals:
			s += "\t\t\t\t\t("
			if goal[0] in ["~", "or"]:
				s += goal[0] + " ("
				for piece in goal[1:]:
					s += piece + " "
				s = s[:-1] + ")"
				s += ")"
			else:
				for piece in goal:
					s += piece + " "
				s = s[:-1] + ")"
			s += "\n"
		s += "\t\t\t\t)\n\t\t\t)\n"
		return s
	
	def get_prob_str(self, name):
		s = "(setf (current-problem)\n"
		s += "\t(create-problem\n\t\t(name " + name + ")\n"
		s += self.get_obj_str()
		s += self.get_state_str()
		s += self.get_goal_str()
		s += "\t)\n)"
		return s
	
	def get_thing(self, name):
		for collection in [self.workers, self.locations, self.materials]:
			if name in collection:
				return collection[name]
		return None
	
	def execute_action(self, action):
		action = list(action)
		action[0] = action[0].lower()
		for i in range(1, len(action)):
			action[i] = self.get_thing(action[i])
			
		if action[0] == "lay-foundation":
			action[2].used = True
			action[1].foundation = True
			action[2].loc = None
		elif action[0] == "build-wood-walls":
			action[1].walls = "WOOD"
			action[2].used = True
			action[2].loc = None
		elif action[0] == "build-brick-walls":
			action[1].walls = "BRICK"
			action[2].used = True
			action[2].loc = None
		elif action[0] == "build-roof":
			action[1].roof = True
			action[2].used = True
			action[2].loc = None
		elif action[0] == "dispatch-worker":
			action[1].loc = action[3]
		elif action[0] == "put-out-fire":
			action[1].hosesloaded = False
			action[2].fire = False
		elif action[0] == "load-hoses":
			action[1].hosesloaded = True
		elif action[0] == "move-material":
			action[1].loc = action[3]
			action[2].loc = action[3]
	
	def execute_plan(self, plan):
		for action in plan:
			self.execute_action(action)
	
	def new_house(self):
		pass
	
	def deep_copy(self):
		str = self.get_prob_str("p1")
		objects, state = parse_state(str)
		copy = HouseWorld(objects, state)
		copy.goals = parse_goals(str)
		return copy
		

#takes a problem file and returns (objects, predicates)
#objects is [[name, name...name, TYPE], ...]
#i.e. [['h1', 'h2', HOUSE], ['w1', FIREMAN], ...]
#state is [[predicate, obj,...obj], ...]
#i.e. [['at', 'w1', 'h1'], ['hoses-loaded', 'w1'], ['has-foundation', 'h2']]
def parse_state(text):
	lines = text
	objects = []
	state = []
	start = lines.find("objects")
	#now we have the index of "objects"
	parens = 1
	end = start
	while parens > 0:
		end = min(lines.find("(", start), lines.find(")", start))
		if end == -1:
			end = max(lines.find("(", start), lines.find(")", start))
		if lines[end] == "(":
			parens += 1
		else: #")"
			parens -= 1
			if parens == 1: #this is a conjunct
				conjunct = lines[start:end].split(" ")
				objects.append(conjunct)
		start = end + 1
	start = lines.find("state")
	#now we have the index of "state"
	parens = 1
	end = start
	while parens > 0:
		end = min(lines.find("(", start), lines.find(")", start))
		if end == -1:
			end = max(lines.find("(", start), lines.find(")", start))
		if lines[end] == "(":
			parens += 1
		else: #")"
			parens -= 1
			if parens == 2: #this is a state conjunct
				conjunct = lines[start:end].split(" ")
				state.append(conjunct)
		start = end + 1
	return objects, state

# returns a list of goals from a given prodigy problem file. Goals are:
# [*optional* ~, predicate, obj1, obj2, ...] For example:
# [['~', 'on-fire', 'h1'], ['complete', 'h2'], ['has-roof', 'h1']]
# Requires that h1 is not on fire and has a roof, and that h2 is complete.
def parse_goals(text):
	lines = text
	goals = []
	start = lines.find("goal")
	parens = 1
	end = start
	opennot = False
	openor = False
	while parens > 0:
		end = min(lines.find("(", start), lines.find(")", start))
		if end == -1:
			end = max(lines.find("(", start), lines.find(")", start))
		if lines[end] == "(":
			parens += 1
			if parens == 4 and lines[start] == "~":
				opennot = True
			elif parens == 4 and lines[start:start + 2] == "or":
				openor = True
		else: #")"
			parens -= 1
			if parens == 2: #this is a goal conjunct/not/or
				if not (opennot or openor):
					conjunct = lines[start:end].split(" ")
					goals.append(conjunct)
				else:
					opennot = False
					openor = False
			if parens == 3:
				if opennot:
					conjunct = lines[start:end].split(" ")
					goals.append(["~"] + conjunct)
				elif openor:
					conjunct = lines[start:end].split(" ")
					goals.append(["or"] + conjunct)
		start = end + 1
	return goals
	

def parse_plan(text):
	lines = text
	actions = []
	start = lines.find("Solution:")
	while lines.find("<", start + 1) > 0:
		start = lines.find("<", start + 1)
		end = lines.find(">", start)
		action = lines[start + 1:end].split(" ")
		if action[0] == "PRODIGY":
			break
		actions.append(action)
	return actions
	

if __name__ == "__main__":
	
	f = open("./probs/p1.lisp", "r")
	text = f.read()
	objects, state = parse_state(text)
	world = HouseWorld(objects, state)
	world.goals = parse_goals(text)

	plan = planner.gen_plan(world)
	print world.get_prob_str("p1")
	print planner.prodigy_str(plan)
	'''
	planf = open("./p1sol.txt", "r")
	text = planf.read()
	plan = parse_plan(text)
'''
	world.execute_plan(plan)
	
	print world.get_prob_str("p1")
	
