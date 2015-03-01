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