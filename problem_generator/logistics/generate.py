import random, gui, pygame, sys, simulator
from pygame.locals import *
from simulator import PostOffice, Airport, Truck, City, Plane, Package

ASQII_A = 65

#possible goals
G_BOX_TRUCK = 0
G_BOX_PO = 1
G_BOX_AP = 2
G_BOX_PLANE = 3
G_TRUCK_PO = 4
G_TRUCK_AP = 5
G_PLANE_AP = 6

DEFAULTS_FILE = "./defaults.txt"

class Goal:
	
	def __init__(self, pred, obj1, obj2):
		self.predicate = pred
		self.obj1 = obj1
		self.obj2 = obj2

class LogisticsProblem:
	
	def __init__(self, data):
		self.numcities = data["numcities"]
		self.numplanes = data["numplanes"]
		self.numboxes = data["numboxes"]
		self.numgoals = data["numgoals"]
		self.goaltypes = data["goaltypes"]
		self.num = data["num"]
	
	def get_random_container(self):
		objs = []
		for city in self.cities:
			objs.append(city.po)
			objs.append(city.ap)
			objs.append(city.truck)
			for plane in city.ap.planes:
				objs.append(plane)
		return random.choice(objs)
	
	def gen_goals(self):
		allgoals = []
		if G_BOX_TRUCK in self.goaltypes:
			for box in self.boxes:
				for city in self.cities:
					allgoals.append(Goal("inside-truck", box, city.truck))
		if G_BOX_PO in self.goaltypes:
			for box in self.boxes:
				for city in self.cities:
					allgoals.append(Goal("at-obj", box, city.po))
		if G_BOX_AP in self.goaltypes:
			for box in self.boxes:
				for city in self.cities:
					allgoals.append(Goal("at-obj", box, city.ap))
		if G_BOX_PLANE in self.goaltypes:
			for box in self.boxes:
				for plane in self.planes:
					allgoals.append(Goal("inside-airplane", box, plane))
		if G_TRUCK_PO in self.goaltypes:
			for city in self.cities:
				allgoals.append(Goal("at-truck", city.truck, city.po))
		if G_TRUCK_AP in self.goaltypes:
			for city in self.cities:
				allgoals.append(Goal("at-truck", city.truck, city.ap))
		if G_PLANE_AP in self.goaltypes:
			for plane in self.planes:
				for city in self.cities:
					allgoals.append(Goal("at-airplane", plane, city.ap))
		goals = []
		usedobjs = []
		for i in range(self.numgoals):
			if not allgoals:
				break
				print "No legal goals left"
			goal = random.choice(allgoals)
			allgoals.remove(goal)
			goalgood = True
			while goal.obj1 in usedobjs:
				goalgood = False
				if not allgoals:
					break
				goalgood = True
				goal = random.choice(allgoals)
				allgoals.remove(goal)
			if goalgood:
				usedobjs.append(goal.obj1)
				goals.append(goal)
			else:
				break
				print "No legal goals left"
		return goals
	
	def generate(self):
		self.cities = []
		self.planes = []
		self.boxes = []
		#init stuff
		for i in range(self.numcities):
			self.cities.append(City("c" + chr(ASQII_A + i)))
		for i in range(self.numplanes):
			cities = list(self.cities)
			city = random.choice(cities)
			plane = Plane("plane" + chr(ASQII_A + i), city)	
			city.ap.planes.append(plane)
			self.planes.append(plane)
		for i in range(self.numboxes):
			name = "obj" + chr(ASQII_A + i)
			loc = self.get_random_container()
			box = Package(name, loc)
			loc.packages.append(box)
			self.boxes.append(box)
		self.goals = self.gen_goals()
	
	def to_s(self):
		s = "(setf (current-problem) \n\t(create-problem\n\t\t"
		s += "(name p" + str(self.num) + ")\n\t\t (objects\n\t\t\t("
		for city in self.cities:
			s += city.name + " "
		s += "CITY)\n\t\t\t("
		for box in self.boxes:
			s += box.name + " "
		s += "OBJECT)\n\t\t\t("
		for city in self.cities:
			s += city.truck.name + " "
		s += "TRUCK)\n\t\t\t("
		for city in self.cities:
			s += city.ap.name + " "
		s += "AIRPORT)\n\t\t\t("
		for plane in self.planes:
			s += plane.name + " "
		s += "AIRPLANE)\n\t\t\t("
		for city in self.cities:
			s += city.po.name + " "
		s += "POST-OFFICE)\n)\n"
		s += "\t\t(state\n\t\t\t(and\n"
		for city in self.cities:
			s += "\t\t\t\t(loc-at " + city.ap.name + " " + city.name + ")\n"
			s += "\t\t\t\t(loc-at " + city.po.name + " " + city.name + ")\n"
			s += "\t\t\t\t(same-city " + city.ap.name + " " + city.po.name + ")\n"
			s += "\t\t\t\t(same-city " + city.po.name + " " + city.ap.name + ")\n"
			s += "\t\t\t\t(part-of " + city.truck.name + " " + city.name + ")\n"
			s += "\t\t\t\t(at-truck " + city.truck.name + " " + city.truck.loc.name + ")\n"
		for plane in self.planes:
			s += "\t\t\t\t(at-airplane " + plane.name + " " + plane.city.name + ")\n"
		for box in self.boxes:
			if box.loc.type == "plane":
				s += "\t\t\t\t(inside-airplane " + box.name + " " + box.loc.name + ")\n"
			elif box.loc.type == "truck":
				s += "\t\t\t\t(inside-truck " + box.name + " " + box.loc.name + ")\n"
			else:
				s += "\t\t\t\t(at-obj " + box.name + " " + box.loc.name + ")\n"
		s += "))\n\t\t(goal\n\t\t\t(and\n"
		for goal in self.goals:
			s += "\t\t\t\t(" + goal.predicate + " " + goal.obj1.name + " " + goal.obj2.name + ")\n"
		s += "))))"
		return s

emptyinput = {"numcities": 0, "numplanes": 0, "numboxes": 0, "numgoals": 0, "goaltypes": 0, "num": 0}

		
#only move package goals allowed
defaults = {"numcities": 6, "numplanes": 4, "numboxes": 6, "numgoals": 4, "goaltypes": [0, 1, 2, 3, 4, 5, 6], "num": 1}

def print_n_logistics(input = defaults, dir = "", name = "p"):
	numprobs = input["num"]
	for i in range(numprobs):
		input["num"] = i + 1
		prob = LogisticsProblem(input)
		prob.generate()
		f = open(dir + name + str(i + 1) + ".lisp", 'w')
		f.write(prob.to_s())
		f.close()

def get_n_logistics(input = defaults, numprobs = defaults["num"]):
	probs = []
	for i in range(numprobs):
		input["num"] = i + 1
		prob = LogisticsProblem(input)
		prob.generate()
		text = prob.to_s()
		objects, state = simulator.parse_state(text)
		world = simulator.LogisticsWorld(objects, state)
		world.goals = simulator.parse_goals(text)
		probs.append(world)
	return probs

def get_n_logistics_only_boxes(input = defaults, numprobs = defaults["num"]):
	probs = []
	for i in range(numprobs):
		input["num"] = i + 1
		prob = LogisticsProblem(input)
		prob.generate()
		text = prob.to_s()
		objects, state = simulator.parse_state(text)
		world = simulator.LogisticsWorld(objects, state)
		world.goals = simulator.parse_goals(text)
		probs.append(world)
	return probs

def get_input(inputboxes, guiscreen):
	input = {}
	input["numcities"] = int(inputboxes["numcities"].text)
	input["numplanes"] = int(inputboxes["numplanes"].text)
	input["numboxes"] = int(inputboxes["numboxes"].text)
	input["numgoals"] = int(inputboxes["numgoals"].text)
	input["num"] = int(inputboxes["numproblems"].text)
	input["goaltypes"] = []
	for obj in guiscreen.objects:
		if hasattr(obj, "label"):
			if obj.label == "Box-in-Truck" and obj.checked:
				input["goaltypes"].append(G_BOX_TRUCK)
			elif obj.label == "Box-at-PO" and obj.checked:
				input["goaltypes"].append(G_BOX_PO)
			elif obj.label == "Box-at-Airport" and obj.checked:
				input["goaltypes"].append(G_BOX_AP)
			elif obj.label == "Box-in-Plane" and obj.checked:
				input["goaltypes"].append(G_BOX_PLANE)
			elif obj.label == "Truck-at-PO" and obj.checked:
				input["goaltypes"].append(G_TRUCK_PO)
			elif obj.label == "Truck-at-Airport" and obj.checked:
				input["goaltypes"].append(G_TRUCK_AP)
			elif obj.label == "Plane-at-Airport" and obj.checked:
				input["goaltypes"].append(G_PLANE_AP)
	return input

if __name__ == "__main__":
	pygame.init()
	pygame.font.init()
	screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
	guiscreen = gui.GUI(screen.get_size())
	guiscreen.bkgcolor = (200, 100, 100)

	inputboxes = {}
	for item in ["numcities", "numplanes", "numboxes", "numgoals"]:
		inputboxes[item] = gui.TextBox(str(defaults[item]), numericOnly=True)
	inputboxes["numproblems"] = gui.TextBox(str(defaults["num"]), numericOnly=True)

	y = 100
	labelx = 150
	boxx = 350
	
	for ib in inputboxes:
		guiscreen.add(gui.Label(ib), (labelx, y))
		guiscreen.add(inputboxes[ib], (boxx, y))
		y += 100

	checkx = 600
	y = 100

	guiscreen.add(gui.CheckBox("Box-in-Truck", G_BOX_TRUCK in defaults["goaltypes"]), (checkx, y))
	y += 75
	guiscreen.add(gui.CheckBox("Box-at-PO", G_BOX_PO in defaults["goaltypes"]), (checkx, y))
	y += 75
	guiscreen.add(gui.CheckBox("Box-at-Airport", G_BOX_AP in defaults["goaltypes"]), (checkx, y))
	y += 75
	guiscreen.add(gui.CheckBox("Box-in-Plane", G_BOX_PLANE in defaults["goaltypes"]), (checkx, y))
	y += 75
	guiscreen.add(gui.CheckBox("Truck-at-PO", G_TRUCK_PO in defaults["goaltypes"]), (checkx, y))
	y += 75
	guiscreen.add(gui.CheckBox("Truck-at-Airport", G_TRUCK_AP in defaults["goaltypes"]), (checkx, y))
	y += 75
	guiscreen.add(gui.CheckBox("Plane-at-Airport", G_PLANE_AP in defaults["goaltypes"]), (checkx, y))


	changed = True
	while 1:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == K_ESCAPE:
					sys.exit(0)
				elif event.key == K_RETURN:
					print_n_logistics(get_input(inputboxes, guiscreen))
				else:
					guiscreen.key_down(event.key)
					changed = True
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1 or event.button == 3:
					guiscreen.click(event.button, event.pos)
					changed = True
		if changed:
			screen.blit(guiscreen.draw(), (0, 0))
			pygame.display.flip()
			changed = False
