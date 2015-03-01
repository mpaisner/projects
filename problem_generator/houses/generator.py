import simulator, random

class HouseWorldGen:
	
	foundationchance = 0.4
	wallchance = 0.4 #if foundation, 50/50 brick wood
	roofchance = 0.3 #if walls
	firechance = 0.2
	
	housegoals = ["has-foundation", "has-roof", "has-brick-walls", "has-wood-walls", "complete"]
	
	def __init__(self):
		pass
	
	def add_houses(self, numhouses, world):
		for i in range(numhouses):
			house = simulator.Location("h" + str(i + 1), "HOUSE", (0, 0))
			world.locations[house.name] = house
	
	def randomize_houses(self, world):
		for house in world.locations.values():
			if house.type == "HOUSE":
				if random.random() < self.foundationchance:
					house.foundation = True
					if random.random() < self.wallchance:
						house.walls = random.choice(["WOOD", "BRICK"])
						if random.random() < self.roofchance:
							house.roof = True
				if random.random() < self.firechance:
					house.fire = True
	
	def add_random_houses(self, numhouses, world):
		self.add_houses(numhouses, world)
		self.randomize_houses(world)
	
	def add_workers(self, num, world, randomlocs = True, oneofeach = True):
		i = 1
		if oneofeach:
			i += 3
			fireman = simulator.Worker("w1", "FIREMAN", "hq")
			world.workers[fireman.name] = fireman
			teamster = simulator.Worker("w2", "TEAMSTER", "hq")
			world.workers[teamster.name] = teamster
			worker = simulator.Worker("w3", "CONSTRUCTION-WORKER", "hq")
			world.workers[worker.name] = worker
		while i < num + 1:
			worker = simulator.Worker("w" + str(i), random.choice(simulator.Worker.types), "hq")
			world.workers[worker.name] = worker
			i += 1
		if randomlocs:
			for worker in world.workers.values():
				worker.loc = random.choice(world.locations.values())
	
	#adds random goals to build (partially or fully) houses and put out fires. No house will be selected for multiple build goals.
	def add_random_goals(self, num, world, firegoals):
		goals = []
		if firegoals:
			for location in world.locations.values():
				if location.type == "HOUSE" and location.fire:
					goals.append(["~", "on-fire", location.name])
		houses = list(world.locations.values())
		while len(goals) < num and len(houses) > 1:
			house = random.choice(houses)
			while house.type == "HQ":
				house = random.choice(houses)
			houses.remove(house)
			goalpred = random.choice(self.housegoals)
			while goalpred in ["has-brick-walls", "has-wood-walls"] and house.walls:
				goalpred = random.choice(self.housegoals)
			goals.append([goalpred, house.name])
		world.goals = goals
	
	def enough_materials(self, dict):
		return dict["CONCRETE"] > 0 and dict["SHINGLE"] > 0 and max(dict["WOOD"], dict["BRICK"]) > 0
	
	#adds the complete house goal to houses that have not been started and while materials are sufficient. Prioritizes houses that have all required materials on site. Adds goals to put out any fires.
	def add_set_goals(self, world, maxgoals):
		goals = []
		materials = {}
		houses = list(world.locations.values())
		for location in houses:
			if location.type == "HQ":
				houses.remove(location)
		for type in simulator.Material.types:
			materials[type] = 0
		for material in world.materials.values():
			materials[material.type] += 1
		for house in houses:
			if house.foundation or house.walls:
				continue #do not add goals when construction has started
			onsite = {}
			for type in materials:
				onsite[type] = 0
			for material in world.materials.values():
				if material.loc == house:
					onsite[material.type] += 1
			if self.enough_materials(onsite):
				goals.append(["complete", house.name])
				houses.remove(house)
				for type in materials:
					materials[type] -= 1
				#now replace one wood or brick since only one is used
				if materials["WOOD"] < materials["BRICK"]:
					materials["WOOD"] += 1
				else:
					materials["BRICK"] += 1
		#now add houses that don't have materials on site, until there aren't enough left
		while self.enough_materials(materials) and houses:
			house = random.choice(houses)
			houses.remove(house)
			if house.foundation or house.walls:
				continue #do not add goals when construction has started
			goals.append(["complete", house.name])
			for type in materials:
				materials[type] -= 1
			#now replace one wood or brick since only one is used
			if materials["WOOD"] < materials["BRICK"]:
				materials["WOOD"] += 1
			else:
				materials["BRICK"] += 1
		#now put out fires
		for location in world.locations.values():
			if location.type == "HOUSE" and location.fire:
				goals.append(["~", "on-fire", location.name])
		while len(goals) > maxgoals:
			goals.pop(0)
		world.goals = goals
		
	
	def add_needed_materials(self, world):
		materialindex = 1
		for goal in world.goals:
			goalpred = goal[0]
			if goal[1] in world.locations:
				house = world.locations[goal[1]]
			else:
				print goal[1]
				continue
			if goalpred == "has-foundation":
				if not house.foundation:
					material = simulator.Material("m" + str(materialindex), "CONCRETE", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
			elif goalpred == "has-brick-walls":
				if not house.foundation:
					material = simulator.Material("m" + str(materialindex), "CONCRETE", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
					material = simulator.Material("m" + str(materialindex), "BRICK", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
				elif not house.walls:
					material = simulator.Material("m" + str(materialindex), "BRICK", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
			elif goalpred == "has-wood-walls":
				if not house.foundation:
					material = simulator.Material("m" + str(materialindex), "CONCRETE", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
					material = simulator.Material("m" + str(materialindex), "WOOD", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
				elif not house.walls:
					material = simulator.Material("m" + str(materialindex), "WOOD", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
			elif goalpred in ["has-roof", "complete"]:
				if not house.foundation:
					material = simulator.Material("m" + str(materialindex), "CONCRETE", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
					material = simulator.Material("m" + str(materialindex), random.choice(["BRICK", "WOOD"]), random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
					material = simulator.Material("m" + str(materialindex), "SHINGLE", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
				elif not house.walls:
					material = simulator.Material("m" + str(materialindex), random.choice(["BRICK", "WOOD"]), random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
					material = simulator.Material("m" + str(materialindex), "SHINGLE", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
				elif not house.roof:
					material = simulator.Material("m" + str(materialindex), "SHINGLE", random.choice(world.locations.values()), False)
					world.materials[material.name] = material
					materialindex += 1
	
	def add_random_materials(self, averagenum, world):
		materialindex = 1
		for type in simulator.Material.types:
			num = max(0, random.gauss(1, 1.0) * averagenum)
			i = 0
			while i < num:
				material = simulator.Material("m" + str(materialindex), type, random.choice(world.locations.values()), False)
				world.materials[material.name] = material
				i += 1
				materialindex += 1
			
		
	
	#problems are random within limits: they must be solvable.
	def gen_random_world(self, minhouses, maxhouses, mingoals, maxgoals, numworkers, fires, firegoals):
		world = simulator.HouseWorld([], [])
		numhouses = random.randrange(minhouses, maxhouses + 1)
		numgoals = random.randrange(mingoals, maxgoals + 1)
		self.add_random_houses(numhouses, world)
		if not fires:
			for house in world.locations.values():
				if house.type == "HOUSE":
					house.fire = False
		self.add_workers(numworkers, world)
		self.add_random_goals(numgoals, world, firegoals)
		if not firegoals:
			for goal in world.goals:
				if goal[1] == "on-fire":
					world.goals.remove(goal)
		self.add_needed_materials(world)
		return world
	
	def gen_random_world_set_goals(self, minhouses, maxhouses, mingoals, maxgoals, numworkers, averagematerials, fires, firegoals):
		world = simulator.HouseWorld([], [])
		numhouses = random.randrange(minhouses, maxhouses + 1)
		numgoals = random.randrange(mingoals, maxgoals + 1)
		self.add_random_houses(numhouses, world)
		if not fires:
			for house in world.locations.values():
				if house.type == "HOUSE":
					house.fire = False
		self.add_workers(numworkers, world)
		self.add_random_materials(averagematerials, world)
		self.add_set_goals(world, maxgoals)
		if not firegoals:
			for goal in world.goals:
				if goal[1] == "on-fire":
					world.goals.remove(goal)
		return world
	
	def gen_simple_problem(self):
		world = simulator.HouseWorld([], [])
		numhouses = 1
		maxgoals = 1
		self.foundationchance = 0.28
		self.firechance = 0.5
		self.add_random_houses(numhouses, world)
		self.add_workers(3, world)
		self.add_random_materials(2, world)
		self.add_set_goals(world, 2)
		return world
	

def add_goals_from_state(world, maxgoals):
	gen = HouseWorldGen()
	gen.add_set_goals(world, maxgoals)

def add_random_goals_from_state(world, num):
	gen = HouseWorldGen()
	gen.add_random_goals(num, world, True)
			
def gen_problems(n, minhouses, maxhouses, mingoals, maxgoals, numworkers, averagematerials, fires, firegoals, setgoals):
	gen = HouseWorldGen()
	problems = []
	for i in range(n):
		if setgoals:
			world = gen.gen_random_world_set_goals(minhouses, maxhouses, mingoals, maxgoals, numworkers, averagematerials, fires, firegoals)
		else:
			world = gen.gen_random_world(minhouses, maxhouses, mingoals, maxgoals, numworkers, fires, firegoals)
		problems.append(world)
	return problems

#note PC directory structures may mess this up
def write_problems(dir, n, minhouses, maxhouses, mingoals, maxgoals, numworkers, averagematerials, fires, firegoals, setgoals):
	if dir[-1] != "/":
		dir += "/"	
	problems = gen_problems(n, minhouses, maxhouses, mingoals, maxgoals, numworkers, averagematerials, fires, firegoals, setgoals)
	for i in range(len(problems)):
		name = "p" + str(i + 1)
		f = open(dir + name + ".lisp", "w")
		f.write(problems[i].get_prob_str(name))
		f.close()
	print str(len(problems)) + " problems generated."

def write_simple_problems(dir, n):
	gen = HouseWorldGen()
	problems = []
	fires = 0
	houses = 0
	for i in range(n):
		problems.append(gen.gen_simple_problem())
		for goal in problems[-1].goals:
			if goal[0] == "~":
				fires += 1
			elif goal[0] == "complete":
				houses += 1
	if dir[-1] != "/":
		dir += "/"	
	for i in range(len(problems)):
		name = "p" + str(i + 1)
		f = open(dir + name + ".lisp", "w")
		f.write(problems[i].get_prob_str(name))
		f.close()
	print str(len(problems)) + " problems generated."
	print "house percent: " + str(100.0 * houses / n)
	print "fire percent: " + str(100.0 * fires / n)
	
if __name__ == "__main__":
	write_problems("./probs", 5, 4, 8, 3, 8, 4, 3, False, True, False)
	