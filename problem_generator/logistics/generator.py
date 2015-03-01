import simulator, random

ASQII_A = 65

class LogisticsWorldGen:
		
	def __init__(self):
		pass
	
	#each city will have a standardly-named post office, airport and truck
	def add_cities(self, num, world):
		for i in range(num):
			letter = chr(len(world.cities) + ASQII_A)
			name = "c" + letter
			world.cities[name] = simulator.City(name)
			world.locations["po_" + name] = world.cities[name].po
			world.locations["airport_" + name] = world.cities[name].ap
			world.trucks["t_" + name] = world.cities[name].truck
	
	#note that created planes have no location.
	def add_planes(self, num, world):
		for i in range(num):
			name = "plane" + chr(len(world.planes) + ASQII_A)
			world.planes[name] = simulator.Plane(name, None)
	
	#randomizes all planes in the world, or a given set(may be in world or not, but user must ensure names do not conflict). This method will cause problems if there are no airports.
	def randomize_planes(self, world, planes = None):
		if not planes:
			planes = world.planes.values()
		airports = []
		for city in world.cities.values():
			if city.ap:
				airports.append(city.ap)
		for plane in planes:
			plane.loc = random.choice(airports)
	
	def add_random_planes(self, num, world):
		self.add_planes(num, world)
		self.randomize_planes(world, world.planes.values()[-num:])
	
	def add_packages(self, num, world):
		for i in range(num):
			name = "obj" + chr(len(world.packages) + ASQII_A)
			world.packages[name] = simulator.Package(name)
	
	def randomize_packages(self, world, packages = None):
		if not packages:
			packages = world.packages.values()
		locs = world.locations.values() + world.trucks.values() + world.planes.values()
		for package in packages:
			loc = random.choice(locs)
			loc.packages.append(package)
			package.loc = loc
	
	def add_random_packages(self, num, world):
		self.add_packages(num, world)
		self.randomize_packages(world, world.packages.values()[-num:])
	
	#put a goal in types multiple times to increase selection chance
	def add_random_goals(self, num, types, world):
		goals = []
		trucks = list(world.trucks.values())
		packages = list(world.packages.values())
		planes = list(world.planes.values())
		for i in range(num):
			goaltype = random.choice(types)
			if goaltype.lower() == "inside-truck":
				package = random.choice(packages)
				goals.append([goaltype, package.name, random.choice(world.trucks.keys())])
				packages.remove(package)
			elif goaltype.lower() == "at-obj":
				package = random.choice(packages)
				goals.append([goaltype, package.name, random.choice(world.locations.keys())])
				packages.remove(package)
			elif goaltype.lower() == "inside-airplane":
				package = random.choice(packages)
				goals.append([goaltype, package.name, random.choice(world.planes.keys())])
				packages.remove(package)
			elif goaltype.lower() == "at-truck":
				truck = random.choice(trucks)
				goals.append([goaltype, truck.name, random.choice([truck.loc.city.po.name, truck.loc.city.ap.name])])
				trucks.remove(truck)
			elif goaltype.lower() == "at-airplane":
				plane = random.choice(planes)
				goals.append([goaltype, plane.name, random.choice(world.cities.values()).ap.name])	
				planes.remove(plane)
		world.goals += goals
	
	def random_world(self, cities, planes, packages):
		world = simulator.LogisticsWorld([], [])
		self.add_cities(cities, world)
		self.add_random_planes(planes, world)
		self.add_random_packages(packages, world)
		return world
	
goaltypes = ["inside-truck", "at-obj", "at-obj", "at-obj", "at-obj", "inside-airplane", "at-truck", "at-airplane"]

defaults = {"numcities": 6, "numplanes": 4, "numpackages": 6, "numgoals": 4, "goaltypes": goaltypes}

def get_n_logistics(numprobs, input = defaults):
	gen = LogisticsWorldGen()
	worlds = []
	for i in range(numprobs):
		worlds.append(gen.random_world(input["numcities"], input["numplanes"], input["numpackages"]))
		gen.add_random_goals(input["numgoals"], input["goaltypes"], worlds[-1])
	return worlds
		
import planner2 as planner		
if __name__ == "__main__":
	gen = LogisticsWorldGen()
	world = gen.random_world(5, 4, 6)
	print world.get_prob_str("p1")
	gen.add_random_goals(4, goaltypes, world)
	print world.get_prob_str("p1")