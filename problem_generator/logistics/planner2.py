import heapq, copy

#assumes same underlying worlds, so same objects
def same_state(world1, world2):
	for package in world1.packages:
		if package not in world2.packages or world1.packages[package].loc.name != world2.packages[package].loc.name:
			return False
	for plane in world1.planes:
		if plane not in world2.planes or world1.planes[plane].loc.name != world2.planes[plane].loc.name:
			return False
	for truck in world1.trucks:
		if truck not in world2.trucks or world1.trucks[truck].loc.name != world2.trucks[truck].loc.name:
			return False
	return True

#goals should be (obj, dest) - all goals in logistics are "at" goals
#heuristic is conservative, since multiple boxes can be carried at once - i.e. it will usually underestimate steps remaining
def heuristic_steps(world, goals):
	steps = 0
	for goal in goals:
		obj = goal[0]
		dest = goal[1]
		if obj.loc == dest:
			continue
		if obj.type == "package":
			if obj.loc.type == "truck":
				if dest.type == "truck":
					steps += 4 #min - unload, load/unload plane, load truck
				elif dest.type == "plane":
					steps += 2 #min - unload, load plane
				elif dest.type == "po":
					if dest.city == obj.loc.loc.city:
						steps += 1 #unload
					else:
						steps += 5 #unload, load/unload plane, next truck
				else: #dest.type == "ap"
					if dest.city == obj.loc.loc.city:
						steps += 1 #unload
					else:
						steps += 3 #unload, load/unload plane
			elif obj.loc.type == "plane":
				if dest.type == "truck":
					steps += 2 #min - unload, load truck
				elif dest.type == "plane":
					steps += 2 #min - unload, load plane
				elif dest.type == "po":
					steps += 3 #unload, load/unload truck
				else: #dest.type == "ap"
					steps += 1 #unload
			elif obj.loc.type == "po":
				if dest.type == "truck":
					if dest.loc.city == obj.loc.city:
						steps += 1 #load truck
					else:
						steps += 5 #load/unload truck, plane, load truck
				elif dest.type == "plane":
					steps += 3 #min - load/unload truck, load plane
				elif dest.type == "po":
					steps += 6 #load/unload truck, plane, truck
				else: #dest.type == "ap"
					if dest.city == obj.loc.city:
						steps += 2 #load/unload truck
					else:
						steps += 4 #load/unload truck, plane
			elif obj.loc.type == "ap":
				if dest.type == "truck":
					if dest.loc.city == obj.loc.city:
						steps += 1 #load truck
					else:
						steps += 3 #load/unload plane, load truck
				elif dest.type == "plane":
					steps += 1 #load plane
				elif dest.type == "po":
					if dest.city == obj.loc.city:
						steps += 2 #load/unload truck
					else:
						steps += 4 #load/unload plane, truck
				else: #dest.type == "ap"
					steps += 2 #load/unload plane
		else: #obj.type == "truck" or "plane":
			steps += 1 #move - ok since moves not counted above
	return steps

class Action:
	
	def __init__(self, name, args):
		self.name = name
		self.args = args
	
	def __eq__(self, other):
		return self.name == other.name and self.args == other.args
	
	def to_list(self):
		l = [self.name]
		for arg in self.args:
			l.append(arg)
		return l

def get_actions(world, goals):
	actions = []
	for goal in goals:
		obj = goal[0]
		dest = goal[1]
		if obj.loc == dest:
			continue
		if obj.type == "package":
			if obj.loc.type == "truck":
				actions.append(Action("unload-truck", (obj.name, obj.loc.name, obj.loc.loc.name)))
				if obj.loc.loc.type == "ap":
					if dest.type == "po" and dest.city == obj.loc.loc.city:
						actions.append(Action("drive-truck", (obj.loc.name, obj.loc.loc.name, obj.loc.loc.city.po.name)))
				else: # obj.loc.loc.type == "po":
					actions.append(Action("drive-truck", (obj.loc.name, obj.loc.loc.name, obj.loc.loc.city.ap.name)))
			elif obj.loc.type == "plane":
				actions.append(Action("unload-airplane", (obj.name, obj.loc.name, obj.loc.loc.name)))
				if dest.type in ["po", "ap"] and dest.city != obj.loc.loc.city:
					actions.append(Action("fly-airplane", (obj.loc.name, obj.loc.loc.name, dest.city.ap.name)))
				elif dest.type in ["truck", "plane"] and dest.loc.city != obj.loc.loc.city:
					actions.append(Action("fly-airplane", (obj.loc.name, obj.loc.loc.name, dest.loc.city.ap.name)))
			elif obj.loc.type == "ap":
				if dest.type in ["po", "ap"]:
					if dest.city == obj.loc.city:
						if obj.loc.city.truck.loc == obj.loc:
							actions.append(Action("load-truck", (obj.name, obj.loc.city.truck.name, obj.loc.name)))
						else:
							actions.append(Action("drive-truck", (obj.loc.city.truck.name, obj.loc.city.po.name, obj.loc.name)))
					else:
						for plane in world.planes.values():
							if plane.loc == obj.loc:
								actions.append(Action("load-airplane", (obj.name, plane.name, obj.loc.name)))
							else:
								actions.append(Action("fly-airplane", (plane.name, plane.loc.name, obj.loc.name)))
				elif dest.type == "truck":
					if dest.loc.city == obj.loc.city:
						if dest.loc == obj.loc:
							actions.append(Action("load-truck", (obj.name, obj.loc.city.truck.name, obj.loc.name)))
						else:
							actions.append(Action("drive-truck", (dest.name, dest.loc.name, obj.loc.name)))
					else:
						for plane in world.planes.values():
							if plane.loc == obj.loc:
								actions.append(Action("load-airplane", (obj.name, plane.name, obj.loc.name)))
							else:
								actions.append(Action("fly-airplane", (plane.name, plane.loc.name, obj.loc.name)))
				else: #dest.type == "plane"
					if dest.loc.city == obj.loc.city:
						actions.append(Action("load-airplane", (obj.name, dest.name, obj.loc.name)))
					else:
						actions.append(Action("fly-airplane", (dest.name, dest.loc.name, obj.loc.name)))
			else: #obj.loc.type == "po"
				if obj.loc.city.truck.loc == obj.loc:
					actions.append(Action("load-truck", (obj.name, obj.loc.city.truck.name, obj.loc.name)))
				else:
					actions.append(Action("drive-truck", (obj.loc.city.truck.name, obj.loc.city.ap.name, obj.loc.name)))
		elif obj.type == "plane":
			actions.append(Action("fly-airplane", (obj.name, obj.loc.name, dest.name)))
		else: #obj.type == "truck"
			if obj.loc.type == "ap":
				actions.append(Action("drive-truck", (obj.name, obj.loc.name, obj.loc.city.po.name)))
			else:
				actions.append(Action("drive-truck", (obj.name, obj.loc.name, obj.loc.city.ap.name)))
	return actions

def get_actions_no_op(world, goals, ops = []):
	actions = get_actions(world, goals)
	return [action for action in actions if action.name not in ops]

def action_restricted_func(actions):
	return lambda world, goals: get_actions_no_op(world, goals, actions)

def get_goals(world):
	goals = []
	for goal in world.goals:
		gl = []
		gl.append(world.get_thing(goal[1]))
		gl.append(world.get_thing(goal[2]))
		goals.append(gl)
	return goals

def finished(goals):
	for goal in goals:
		if goal[0].loc.name != goal[1].name:
			return False
	return True

def get_plan(state, preds):
	plan = []
	while state:
		state, action = preds[state]
		plan.append(action)
	reversedPlan = []
	i = len(plan) - 2
	while i >= 0:
		reversedPlan.append(plan[i])
		i -= 1
	return reversedPlan

def a_star(world, heuristic = heuristic_steps, get_actions = get_actions, type = "greedy", quickfail = True, timelimit = None):
	wcopy = copy.deepcopy(world)
	goals = get_goals(wcopy)
	visited = {wcopy: (None, None)}
	heap = [(heuristic(wcopy, goals), wcopy)]
	i = 0
	printed = False
	while heap:
		i += 1
		cost, state = heapq.heappop(heap)
		if i == 500:
			print "Exceeded node limit (500). Planning failed."
			return None
		goals = get_goals(state)
		if finished(goals):
			return state, get_plan(state, visited)
		cost -= heuristic(state, goals)
		actions = get_actions(state, goals)
		if not actions:
			if not printed:
				pass#print state.readable_str()
			printed = True
			if quickfail:
				return None
		for action in actions:
			newstate = copy.deepcopy(state)
			newstate.execute_action(action.to_list())
			inVisited = False
			#not a long-term solution, instead change world.__eq__()
			for visitedState in visited: 
				if same_state(visitedState, newstate):
					inVisited = True
					break
			if not inVisited:
				newgoals = get_goals(state)
				if type == "greedy":
					heapq.heappush(heap, (heuristic(newstate, newgoals), newstate))
				elif type == "astar":
					heapq.heappush(heap, (heuristic(newstate, newgoals) + cost + 1, newstate))
				visited[newstate] = (state, action.to_list())
		
	

if __name__ == "__main__":
	
	import simulator, copy, datetime
	
	f = open("./probs/p1.lisp", "r")
	text = f.read()
	objects, state = simulator.parse_state(text)
	world = simulator.LogisticsWorld(objects, state)
	world.goals = simulator.parse_goals(text)
	goals = get_goals(world)
	for action in get_actions(world, goals):
		print action.to_list()
	print
	getFunc = action_restricted_func(["unload-airplane", "load-airplane"])
	for action in getFunc(world, goals):
		print action.to_list()		
	
	
	res = a_star(world, get_actions = getFunc)
	if res:
		for step in res[1]:
			world.execute_action(step)
	
	'''
	t1 = datetime.datetime.today()
	print t1
	if res:
		for step in res[1]:
			print step
	t2 = datetime.datetime.today()
	print t2
	print (t2 - t1).total_seconds()
	
	print "timetest"
	t1 = datetime.datetime.today()
	print t1
	
	for i in range(1000):
		w = copy.deepcopy(world)
		b = same_state(w, world)
		heuristic_steps(world, goals)
		get_actions(world, goals)
	t2 = datetime.datetime.today()
	print t2
	print (t2 - t1).total_seconds()
	'''
	

	#for action in get_actions(world, goals):
	#	print action.to_list()
	#print heuristic_steps(world, goals)