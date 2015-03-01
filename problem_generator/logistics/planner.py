
def printtype(obj):
	print obj.__class__

def package_loc(world, package):
	for city in world.cities.values():
		for loc in [city.truck, city.po, city.ap]:
			if package in loc.packages:
				return [city, loc.type]
	for plane in world.planes.values():
		if package in plane.packages:
			return [plane, "plane"]
	return None

#returns {goal-package: dest}
def goal_packages(world):
	goals = {}
	for goal in world.goals:
		if goal[0] in ["inside-truck", "at-obj", "inside-airplane"]:
			package = world.get_thing(goal[1])
			goals[package] = world.get_thing(goal[2])
	return goals

#returns [city, type] if type is not "plane", else returns [plane, type = "plane"]
def loc_tuple(loc):
	if loc.type == "plane":
		return [loc, "plane"]
	elif hasattr(loc, "city"):
		return [loc.city, loc.type]
	else:
		return [loc.loc.city, loc.type] #for trucks

#returns {package: startloc}
def package_locs(world, goals):
	locs = {}
	for city in world.cities.values():
		for loc in [city.truck, city.po, city.ap]:
			if not loc:
				continue
			for package in loc.packages:
				if package in goals:
					locs[package] = loc
	for plane in world.planes.values():
		for package in plane.packages:
			if package in goals:
				locs[package] = plane

#for each package in list, given start and goal locs, creates {package : (start city/plane, type, end city/plane, type}
def package fourples(world, locs, goals):
	packages = {}
	for package in locs:
		fourple = loc_tuple(locs[package]) + loc_tuple(goals[package])
		packages[package] = fourple
	return packages

def at_dest(loc, fourple):
	return loc_tuple(loc) == fourple[2:]

def all_in_truck(packages, truck):
	for package in truck.packages:
		if package in packages and not at_dest(truck, packages[package]):
			return False
	return True

#packages is {package: fourple}
#returns cities that have packages for pickup in their airports (dict/set)
def pickup_cities(world, packages):
	cities = {}
	for city1, type1, city2, type2 in packages.values():
		if type1 != "plane":
			if city1 != city2 and type2 != "plane":
				cities[city1] = True
	return cities

#returns all planes that packages in given city must be inside
def inside_planes(world, packages, city):
	planes = {}
	for package in city.ap.packages:
		if package in packages:
			if packages[package][3] == "plane":
				planes[packages[package][2]] = True
	return planes

#all city destinations of packages in airport, other than current city
def dests(world, packages, city):
	dests = {}
	for package in city.ap.packages:
		if package in packages:
			if packages[package][3] != "plane" and packages[package][0] != city:
				dests[packages[package][2]] = True
	return dests
				

def plane_dests(world, packages, plane):
	dests = {}
	for package in plane.packages:
		if package in packages and packages[package][2] != plane.loc.city and packages[package][3] != "plane":
			dests[package] = True
	return dests

def next_plane(world, city):
	for plane in world.planes.values():
		if plane.loc.city == city:
			return plane
	return random.choice(world.planes.values())	

#packages is {package: fourple}
def po_to_ap(world, city, packages):
	plan = []
	if city.truck.loc.type == "ap":
		plan.append(["drive-truck", city.truck.name, city.ap.name, city.po.name]) #get truck to po
		world.execute_action(plan[-1])
	for package in city.po.packages:
		if package in packages and not at_dest(city.po, packages[package]):
			plan.append(["load-truck", package.name, city.truck.name, city.po.name]) #load all packages at po
			world.execute_action(plan[-1])
	if all_in_truck(packages, city.truck):
		return plan #if only goal is inside-truck, do not move/unload
	plan.append(["drive-truck", city.truck.name, city.po.name, city.ap.name])
	world.execute_action(plan[-1])
	for package in city.truck.packages:
		if not at_dest(city.truck, packages[package]):
			plan.append(["unload-truck", package.name, city.truck.name, city.ap.name])
			world.execute_action(plan[-1])
	return plan

#packages is {package: fourple}
#return plan, note that plane is at city2 regardless of start
def air_transport(world, plane, city1, city2, packages, toload = None):
	if not toload:
		toload = city1.ap.packages
	plan = []
	if planecity != city1:
		plan.append(["fly-airplane", plane.name, plane.loc.name, city1.ap.name])
		world.execute_action(plan[-1])
	for package in toload:
		if package in packages and not at_dest(city1.ap, packages[package]) and not (packages[package][3] == "plane" and packages[package][2] != plane):
			plan.append(["load-airplane", package.name, plane.name, city1.ap.name])
			world.execute_action(plan[-1])
	plan.append(["fly-airplane", plane.name, city1.ap.name, city2.ap.name])
	world.execute_action(plan[-1])
	for package in plane.packages:
		if package in packages and packages[package][2] == city2 or (packages[package][3] == "plane" and packages[package][2] != plane):
			plan.append(["unload-airplane", package.name, plane.name, city2.ap.name])
			world.execute_action(plan[-1])
	return plan

#note that this should only be called after all packages have been flown to destination cities, otherwise it will mess things up. Could fix by checking if dests are at po or truck rather than NOT at ap.
def ap_to_po(world, city, packages):
	plan = []
	if city.truck.loc.type == "po":
		plan.append(["drive-truck", city.truck.name, city.po.name, city.ap.name]) #get truck to ap
		world.execute_action(plan[-1])
	for package in city.ap.packages:
		if package in packages and not at_dest(city.ap, packages[package]):
			plan.append(["load-truck", package.name, city.truck.name, city.ap.name]) #load all packages at ap
			world.execute_action(plan[-1])
	if all_in_truck(packages, city.truck):
		return plan #do not drive if all packages destined for truck
	plan.append(["drive-truck", city.truck.name, city.ap.name, city.po.name])
	world.execute_action(plan[-1])
	for package in city.truck.packages:
		if not at_dest(city.truck, packages[package]):
			plan.append(["unload-truck", package.name, city.truck.name, city.po.name])
			world.execute_action(plan[-1])
	return plan

def unload_truck(world, city, packages, dest):
	plan = []
	if city.truck.loc != dest:
		plan.append(["drive-truck", city.truck.name, city.truck.loc.name, dest.name])
		world.execute_action(plan[-1])
	for package in city.truck.packages:
		if package in packages and not at_dest(city.truck, packages[package]):
			plan.append(["unload-truck", package.name, city.truck.name, dest.name])
			world.execute_action(plan[-1])
	return plan
	

def load_planes(world, packages):
	plan = []
	for package in packages:
		if packages[package][3] == "plane":
			packageloc = package_loc(world, package)
			plane = packages[package][2]
			if packageloc[1] == "plane" and packageloc[0] != plane:
				plan.append(["unload-airplane", package.name, plane.name, plane.loc.name])
				world.execute_action(plan[-1])
				packageloc = [plane.loc.city, "ap"]
			if packages[package][2].loc.city != packageloc[0]:
				plan.append(["fly-airplane", plane.name, plane.loc.name, packageloc[0].ap.name])
				world.execute_action(plan[-1])
			plan.append(["load-airplane", package.name, plane.name, packageloc[0].ap.name])
	return plan
#all po-ap, all-trans, all ap-po, all ap-pickup

def all_to_ap(world, packages):
	plan = []
	cities = {}
	for city in world.cities.values():
		for package in city.po.packages:
			if package in packages and not at_dest(city.po, packages[package]):
				cities[city] = True
	for city in world.cities.values():
		if city not in cities:
			ap = False
			po = False
			for package in city.truck.packages:
				if package in packages and not at_dest(city.truck, packages[package]):
					if packages[package][2] == city and packages[package][3] == "po":
						po = True
					else:
						ap = True
			if ap:
				plan += unload_truck(world, city, packages, city.ap)
			elif po:
				plan += unload_truck(world, city, packages, city.po)
	for city in cities:
		plan += po_to_ap(world, city, packages)
	return plan

def all_flights(world, packages):
	plan = []
	cities = pickup_cities(world, packages).keys()
	while cities:
		city = random.choice(cities)
		cities.remove(city)
		plane = next_plane(world, city)
		if plane.loc.city != city:
			plan.append(["fly-airplane", plane.name, plane.loc.name, city.ap.name])
			world.execute_action(plan[-1])
		dests = dests(world, packages, city)
		for dest in plane_dests(world, packages, plane):
			if dest not in dests:
				dests[dest]= True
		dests = dests.keys()
		while dests:
			dest = random.choice(dests)
			dests.remove(dest)
			plan += air_transport(world, plane, city, dest, packages)
			city = dest
			cities.remove(city)
			for newdest in dests(world, packages, city):
				if newdest not in dests:
					dests.append(newdest)
	return plan

#next, all ap-po, 
	