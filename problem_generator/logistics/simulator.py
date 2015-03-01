import random

class PostOffice:
	
	type = "po"
	
	def __init__(self, name, city):
		#self.name = "po_" + cityname
		self.name = name
		self.city = city
		self.packages = []

class Airport:
	
	type = "ap"
	
	def __init__(self, name, city):
		#self.name = "airport_" + cityname
		self.name = name
		self.city = city
		self.packages = []

class Truck:
	
	type = "truck"
	
	def __init__(self, name, loc):
		#self.name = "t_" + cityname
		self.name = name
		self.loc = loc
		self.packages = []

class City:
	
	type = "city"
	
	def __init__(self, name):
		self.name = name
		self.po = PostOffice("po_" + name, self)
		self.ap = Airport("airport_" + name, self)
		self.truck = Truck("t_" + name, random.choice([self.po, self.ap]))
	
class Package:
	
	type = "package"
	
	def __init__(self, name, loc = None):
		self.name = name
		self.loc = loc

class Plane:
	
	type= "plane"
	
	def __init__(self, name, airport):
		self.name = name
		self.loc = airport
		self.packages = []

class LogisticsWorld:
	
	def __init__(self, objects, state):
		#get cities
		self.cities = {}
		self.locations = {} #airports and post offices
		self.trucks = {}
		for conjunct in objects:
			if conjunct[-1] == "CITY":
				for city in conjunct[:-1]:
					#save city, its post office, its airport, and its truck
					self.cities[city] = City(city)
					self.locations[self.cities[city].po.name] = self.cities[city].po
					self.locations[self.cities[city].ap.name] = self.cities[city].ap
					self.trucks[self.cities[city].truck.name] = self.cities[city].truck
		
		
		#if needed, add stuff here to read alternate aps, pos, trucks
		
		#get planes
		self.planes = {}
		for conjunct in objects:
			if conjunct[-1] == "AIRPLANE":
				for plane in conjunct[:-1]:
					self.planes[plane] = Plane(plane, None)
		
		#get packages
		self.packages = {}
		for conjunct in objects:
			if conjunct[-1] == "OBJECT":
				for package in conjunct[:-1]:
					self.packages[package] = Package(package)
		
		#implement state
		for conjunct in state:
			if conjunct[0] == "at-truck":
				self.trucks[conjunct[1]].loc = self.locations[conjunct[2]]
			elif conjunct[0] == "at-airplane":
				self.planes[conjunct[1]].loc = self.cities[conjunct[2]].ap
			elif conjunct[0] == "at-obj":
				self.locations[conjunct[2]].packages.append(self.packages[conjunct[1]])
				self.packages[conjunct[1]].loc = self.locations[conjunct[2]]
			elif conjunct[0] == "inside-airplane":
				self.planes[conjunct[2]].packages.append(self.packages[conjunct[1]])
				self.packages[conjunct[1]].loc = self.planes[conjunct[2]]
			elif conjunct[0] == "inside-truck":
				self.trucks[conjunct[2]].packages.append(self.packages[conjunct[1]])		
				self.packages[conjunct[1]].loc = self.trucks[conjunct[2]]
		self.goals = []
	
	def get_obj_str(self):
		s = "\t\t\t(objects\n"
		if len(self.cities) > 0:
			s += "\t\t\t\t("
			for city in self.cities.values():
				s += city.name + " "
			s += "CITY)\n"
			s += "\t\t\t\t("
			for city in self.cities.values():
				if city.po:
					s += city.po.name + " "
			s += "POST_OFFICE)\n"
			s += "\t\t\t\t("
			for city in self.cities.values():
				if city.ap:
					s += city.ap.name + " "
			s += "AIRPORT)\n"
			s += "\t\t\t\t("
			for city in self.cities.values():
				if city.truck:
					s += city.truck.name + " "
			s += "TRUCK)\n"
			
		if len(self.planes) > 0:
			s += "\t\t\t\t("
			for plane in self.planes.values():
				s += plane.name + " "
			s += "AIRPLANE)\n"
		if len(self.packages) > 0:
			s += "\t\t\t\t("
			for package in self.packages.values():
				s += package.name + " "
			s += "OBJECT)\n"
		s += "\t\t\t)\n"	
		return s
	
	def get_state_conjuncts(self):
		state = []
		for city in self.cities.values():
			if city.ap:
				state.append(["loc-at", city.ap.name, city.name])
				for package in city.ap.packages:
					state.append(["at-obj", package.name, city.ap.name])
			if city.po:
				state.append(["loc-at", city.po.name, city.name])
				for package in city.po.packages:
					state.append(["at-obj", package.name, city.po.name])
			if city.po and city.ap:
				state.append(["same-city", city.ap.name, city.po.name])
				state.append(["same-city", city.po.name, city.ap.name])
			if city.truck:
				state.append(["part-of", city.truck.name, city.name])
				state.append(["at-truck", city.truck.name, city.truck.loc.name])	
				for package in city.truck.packages:
					state.append(["inside-truck", package.name, city.truck.name])		
		for plane in self.planes.values():
			state.append(["at-airplane", plane.name, plane.loc.city.name])
			for package in plane.packages:
				state.append(["inside-airplane", package.name, plane.name])
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
	
	def readable_str(self):
		s = ""
		for package in self.packages.values():
			s += package.name + " -- " + package.loc.name + "\n"
		for plane in self.planes.values():
			s += plane.name + " at " + plane.loc.name + "\n"
		for goal in self.goals:
			s += str(goal) + "\n"
		return s
	
	def get_thing(self, name):
		for collection in [self.cities, self.locations, self.trucks, self.planes, self.packages]:
			if name in collection:
				return collection[name]
		return None
	
	def execute_action(self, action):
		action = [item for item in action]
		action[0] = action[0].lower()
		for i in range(1, len(action)):
			action[i] = self.get_thing(action[i])
			
		if action[0] == "load-truck": #package, truck, loc
			if action[1] in action[2].loc.packages:
				action[2].loc.packages.remove(action[1])
				action[2].packages.append(action[1])
				action[1].loc = action[2]
		elif action[0] == "load-airplane": #package, plane, loc
			if action[1] in action[2].loc.packages:
				action[2].loc.packages.remove(action[1])
				action[2].packages.append(action[1])
				action[1].loc = action[2]
		elif action[0] == "unload-truck": #package, truck, loc
			if action[1] in action[2].packages:
				action[2].packages.remove(action[1])
				action[2].loc.packages.append(action[1])
				action[1].loc = action[2].loc
		elif action[0] == "unload-airplane": #package, plane, loc
			if action[1] in action[2].packages:
				action[2].packages.remove(action[1])
				action[2].loc.packages.append(action[1])
				action[1].loc = action[2].loc
		elif action[0] == "drive-truck": #truck, start, dest
			if action[1].loc == action[2] and action[2].city == action[3].city:
				action[1].loc = action[3]
		elif action[0] == "fly-airplane": #plane, start, dest
			if action[1].loc == action[2]:
				action[1].loc = action[3]
	
	def execute_plan(self, plan):
		for action in plan:
			self.execute_action(action)
	

#takes a problem file and returns (objects, predicates)
#objects is [[name, name...name, TYPE], ...]
#i.e. [['h1', 'h2', HOUSE], ['w1', FIREMAN], ...]
#state is [[predicate, obj,...obj], ...]
#i.e. [['at', 'w1', 'h1'], ['hoses-loaded', 'w1'], ['has-foundation', 'h2']]
#eventually this should be imported from prodigyparser.py
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
		if end < 0:
			break
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
		if end < 0:
			break
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
#eventually this should be imported from prodigyparser.py
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
		if end < 0:
			break
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


if __name__ == "__main__":
	
	
	f = open("./probs/p1.lisp", "r")
	text = f.read()
	objects, state = parse_state(text)
	world = LogisticsWorld(objects, state)
	world.goals = parse_goals(text)

	#plan = planner.gen_plan(world)
	#print world.get_prob_str("p1")
	#print planner.prodigy_str(plan)
	'''
	planf = open("./p1sol.txt", "r")
	text = planf.read()
	plan = parse_plan(text)
'''
	#world.execute_plan(plan)
	
	#print world.get_prob_str("p1")