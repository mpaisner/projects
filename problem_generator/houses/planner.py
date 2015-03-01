#must apply each action as generated, otherwise complex plans fail.

def lay_foundation(house, world, materials):
	plan = []
	if house.foundation:
		return plan
	mymaterial = None
	for material in materials:
		if material.type == "CONCRETE" and not material.used:
			mymaterial = material
			break
	if not mymaterial:
		raise Exception("Not enough concrete")
	if mymaterial.loc != house:
		for worker in world.workers.values():
			if worker.type == "TEAMSTER":
				if worker.loc != mymaterial.loc:
					plan.append(["dispatch-worker", worker.name, worker.loc.name, material.loc.name])
					world.execute_action(plan[-1])
				plan.append(["move-material", worker.name, mymaterial.name, house.name])
				world.execute_action(plan[-1])
				break
	for worker in world.workers.values():
		if worker.type == "CONSTRUCTION-WORKER":
			if worker.loc != house:
				plan.append(["dispatch-worker", worker.name, worker.loc.name, house.name])
				world.execute_action(plan[-1])
			plan.append(["lay-foundation", house.name, mymaterial.name, worker.name])
			world.execute_action(plan[-1])
			materials.remove(mymaterial)
			break
	return plan

def build_brick_walls(house, world, materials):
	plan = []
	if house.walls == "BRICK":
		return plan
	elif house.walls:
		raise Exception("Wood walls already built")
	mymaterial = None
	for material in materials:
		if material.type == "BRICK" and not material.used:
			mymaterial = material
			break
	if not mymaterial:
		raise Exception("Not enough Brick")
	if mymaterial.loc != house:
		for worker in world.workers.values():
			if worker.type == "TEAMSTER":
				if worker.loc != mymaterial.loc:
					plan.append(["dispatch-worker", worker.name, worker.loc.name, material.loc.name])
					world.execute_action(plan[-1])
				plan.append(["move-material", worker.name, mymaterial.name, house.name])
				world.execute_action(plan[-1])
				break
	for worker in world.workers.values():
		if worker.type == "CONSTRUCTION-WORKER":
			if worker.loc != house:
				plan.append(["dispatch-worker", worker.name, worker.loc.name, house.name])
				world.execute_action(plan[-1])
			plan.append(["build-brick-walls", house.name, mymaterial.name, worker.name])
			world.execute_action(plan[-1])
			materials.remove(mymaterial)
			break
	return plan

def build_wood_walls(house, world, materials):
	plan = []
	if house.walls == "WOOD":
		return plan
	elif house.walls:
		raise Exception("Brick walls already built")
	mymaterial = None
	for material in materials:
		if material.type == "WOOD" and not material.used:
			mymaterial = material
			break
	if not mymaterial:
		raise Exception("Not enough Wood")
	if mymaterial.loc != house:
		for worker in world.workers.values():
			if worker.type == "TEAMSTER":
				if worker.loc != mymaterial.loc:
					plan.append(["dispatch-worker", worker.name, worker.loc.name, material.loc.name])
					world.execute_action(plan[-1])
				plan.append(["move-material", worker.name, mymaterial.name, house.name])
				world.execute_action(plan[-1])
				break
	for worker in world.workers.values():
		if worker.type == "CONSTRUCTION-WORKER":
			if worker.loc != house:
				plan.append(["dispatch-worker", worker.name, worker.loc.name, house.name])
				world.execute_action(plan[-1])
			plan.append(["build-wood-walls", house.name, mymaterial.name, worker.name])
			world.execute_action(plan[-1])
			materials.remove(mymaterial)
			break
	return plan

def build_roof(house, world, materials):
	try:
		plan = build_brick_walls(house, world, materials)
	except Exception:
		plan = build_wood_walls(house, world, materials)
	if house.roof:
		return plan
	mymaterial = None
	for material in materials:
		if material.type == "SHINGLE" and not material.used:
			mymaterial = material
			break
	if not mymaterial:
		raise Exception("Not enough Shingle")
	if mymaterial.loc != house:
		for worker in world.workers.values():
			if worker.type == "TEAMSTER":
				if worker.loc != mymaterial.loc:
					print prodigy_str(plan), material.name, worker.name, material.type
					plan.append(["dispatch-worker", worker.name, worker.loc.name, material.loc.name])
					world.execute_action(plan[-1])
				plan.append(["move-material", worker.name, mymaterial.name, house.name])
				world.execute_action(plan[-1])
				break
	for worker in world.workers.values():
		if worker.type == "CONSTRUCTION-WORKER":
			if worker.loc != house:
				plan.append(["dispatch-worker", worker.name, worker.loc.name, house.name])
				world.execute_action(plan[-1])
			plan.append(["build-roof", house.name, mymaterial.name, worker.name])
			world.execute_action(plan[-1])
			materials.remove(mymaterial)
			break
	return plan

def put_out_fire(house, world, materials):
	plan = []
	if not house.fire:
		return plan
	for worker in world.workers.values():
		if worker.type == "FIREMAN":
			if not worker.hosesloaded:
				if worker.loc != world.locations["hq"]:
					plan.append(["dispatch-worker", worker.name, worker.loc.name, "hq"])
					world.execute_action(plan[-1])
				plan.append(["load-hoses", worker.name])
				world.execute_action(plan[-1])
				plan.append(["dispatch-worker", worker.name, "hq", house.name])
				world.execute_action(plan[-1])
			elif worker.loc != house:
				plan.append(["dispatch-worker", worker.name, worker.loc.name, house.name])
				world.execute_action(plan[-1])
			plan.append(["put-out-fire", worker.name, house.name])
			world.execute_action(plan[-1])
			break
	return plan

def complete_house(house, world, materials):
	plan = lay_foundation(house, world, materials)
	plan += build_roof(house, world, materials)
	plan += put_out_fire(house, world, materials)
	plan.append(["house-complete", house.name])
	world.execute_action(plan[-1])
	return plan

def gen_plan(world):
	plan = []
	materials = list(world.materials.values())
	for material in materials:
		if material.used:
			materials.remove(material)
	for goal in world.goals:
		if goal[0] == "has-foundation":
			plan += lay_foundation(world.locations[goal[1]], world, materials)
	for goal in world.goals:
		if goal[0] == "has-brick-walls":
			plan += build_brick_walls(world.locations[goal[1]], world, materials)
	for goal in world.goals:
		if goal[0] == "has-wood-walls":
			plan += build_wood_walls(world.locations[goal[1]], world, materials)
	for goal in world.goals:
		if goal[0] == "has-roof":
			plan += build_roof(world.locations[goal[1]], world, materials)
		elif goal[0] == "complete":
			plan += complete_house(world.locations[goal[1]], world, materials)
		elif goal[0] == "~" and goal[1] == "on-fire":
			plan += put_out_fire(world.locations[goal[2]], world, materials)
	return plan

def prodigy_str(plan):
	s = "Solution:\n\n"
	for step in plan:
		s += "<"
		for piece in step:
			s += piece + " "
		s = s[:-1] + ">\n"
	return s

