import random, gui, pygame, sys
from pygame.locals import *

ASQII_A = 65

#possible goals
G_ON = 0
G_HOLDING = 1
G_CLEAR = 2
G_ON_TABLE = 3
G_ARM_EMPTY = 4

GOAL_TO_NAME = {G_ON: "ON", G_HOLDING: "HOLDING", G_CLEAR: "CLEAR", G_ON_TABLE: "ON TABLE", G_ARM_EMPTY: "ARM EMPTY"}
PREDICATE_TO_GOAL = {"on": G_ON, "holding": G_HOLDING, "clear": G_CLEAR, "on-table": G_ON_TABLE, "arm-empty": G_ARM_EMPTY}
NAME_TO_GOAL = {}
for goal in GOAL_TO_NAME:
	NAME_TO_GOAL[GOAL_TO_NAME[goal]] = goal

DEFAULTS_FILE = "./defaults.txt"

class Block:
	
	def __init__(self, name):
		self.name = name

class Goal:
	
	def __init__(self, pred, obj1, obj2):
		self.predicate = pred
		self.obj1 = obj1
		self.obj2 = obj2

class BlocksworldProblem:
	
	def __init__(self, data):
		self.numblocks = data["numblocks"]
		self.numgoals = data["numgoals"]
		self.goaltypes = data["goaltypes"]
		self.num = data["num"]
	
	'''
	def get_random_container(self):
		objs = []
		for city in self.cities:
			objs.append(city.po)
			objs.append(city.ap)
			objs.append(city.truck)
			for plane in city.ap.planes:
				objs.append(plane)
		return random.choice(objs)
		'''
	
	def gen_goals(self):
		allgoals = []
		if G_ON in self.goaltypes:
			for block1 in self.blocks:
				for block2 in self.blocks:
					if block1 != block2:
						allgoals.append(Goal("on", block1, block2))
		if G_HOLDING in self.goaltypes:
			for block1 in self.blocks:
				allgoals.append(Goal("holding", block1, None))
		if G_CLEAR in self.goaltypes:
			for block1 in self.blocks:
				allgoals.append(Goal("clear", block1, None))
		if G_ON_TABLE in self.goaltypes:
			for block1 in self.blocks:
				allgoals.append(Goal("on-table", block1, None))
		if G_ARM_EMPTY in self.goaltypes:
			allgoals.append(Goal("arm-empty", None, None))

		goals = []
		ison = [] #includes held objects, or objects on table
		otheron = [] #includes clear objects, held objects
		armempty = False
		oneheld = False
		for i in range(self.numgoals):
			if not allgoals:
				break
				print "No legal goals left"
			goal = random.choice(allgoals)
			allgoals.remove(goal)
			goalgood = True
			while (goal.predicate == "arm-empty" and oneheld) or (goal.predicate != "arm-empty" and ((goal.obj1 in ison and (goal.predicate == "on" or goal.predicate == "holding" or goal.predicate == "on-table")) or (goal.predicate == "on" and goal.obj2 in otheron) or (goal.obj1 in otheron and (goal.predicate == "holding" or goal.predicate == "clear")) or ((armempty or oneheld) and goal.predicate == "holding"))):
				goalgood = False
				if not allgoals:
					break
				goalgood = True
				goal = random.choice(allgoals)
				allgoals.remove(goal)
			if goalgood:
				if goal.predicate == "on":
					ison.append(goal.obj1)
					otheron.append(goal.obj2)
				elif goal.predicate == "holding":
					ison.append(goal.obj1)
					otheron.append(goal.obj1)
					oneHeld = True
					print "held " + str(len(goals))
				elif goal.predicate == "clear":
					otheron.append(goal.obj1)
				elif goal.predicate == "on-table":
					ison.append(goal.obj1)
				elif goal.predicate == "arm-empty":
					armempty = True
				goals.append(goal)
			else:
				break
				print "No legal goals left"
		return goals
	
	def generate_start_state(self):
		HELD_CHANCE = 0.25
		oneheld = False
		clear = ["table"]
		state = []
		blocks = list(self.blocks)
		if random.random() < HELD_CHANCE:
			if blocks:
				oneheld = random.choice(blocks)
				blocks.remove(oneheld)
		while blocks:
			next = random.choice(blocks)
			blocks.remove(next)
			on = random.choice(clear)
			if on == "table":
				state.append(Goal("on-table", next, None))
			else:
				state.append(Goal("on", next, on))
				clear.remove(on)
			clear.append(next)
		for block in clear:
			if block != "table":
				state.append(Goal("clear", block, None))
		if oneheld:
			state.append(Goal("holding", oneheld, None))
		else:
			state.append(Goal("arm-empty", None, None))
		return state
	
	def gen_goals_2(self):
		maxgoals = []
		maxattempts = 20
		for i in range(maxattempts):
			goals = self.generate_start_state()
			todelete = []
			for i in range(len(goals)):
				goal = goals[i]
				#print goal.predicate, self.goaltypes
				if PREDICATE_TO_GOAL[goal.predicate] not in self.goaltypes:
					todelete.append(goal)
			for goal in todelete:
				goals.remove(goal)
			if len(goals) >= self.numgoals:
				while len(goals) > self.numgoals:
					goals.remove(random.choice(goals))
				return goals
			elif len(goals) > len(maxgoals):
				maxgoals = goals
		return maxgoals
	
	def generate(self):
		self.blocks = []
		#init stuff
		for i in range(self.numblocks):
			self.blocks.append(Block("block" + chr(ASQII_A + i)))
		self.goals = self.gen_goals_2()
		self.state = self.generate_start_state()
	
	def to_s(self):
		s = "(setf (current-problem) \n\t(create-problem\n\t\t"
		s += "(name p" + str(self.num) + ")\n\t\t (objects ("
		for block in self.blocks:
			s += block.name + " "
		s += "object))\n"
		s += "\t\t(state\n\t\t\t(and\n"
		for part in self.state:
			s += "\t\t\t\t(" + part.predicate
			if part.obj1:
				s += " " + part.obj1.name
			if part.obj2:
				s += " " + part.obj2.name
			s += ")\n"
		s += "))\n\t\t(goal\n\t\t\t(and\n"
		for goal in self.goals:
			s += "\t\t\t\t(" + goal.predicate
			if goal.obj1:
				s += " " + goal.obj1.name
			if goal.obj2:
				s += " " + goal.obj2.name
			s += ")\n"
		s += "))))"
		return s
		
def print_n_blocksworld(input):
	numprobs = input["num"]
	for i in range(numprobs):
		input["num"] = i + 1
		prob = BlocksworldProblem(input)
		prob.generate()
		f = open("p" + str(i + 1) + ".lisp", 'w')
		f.write(prob.to_s())
		f.close()

defaults = {"numblocks": 4, "numgoals": 3, "goaltypes": [0, 1, 2, 3, 4], "num": 1}

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
guiscreen = gui.GUI(screen.get_size())
guiscreen.bkgcolor = (200, 100, 100)

inputboxes = {}
for item in ["numblocks", "numgoals"]:
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

for goal in GOAL_TO_NAME:
	guiscreen.add(gui.CheckBox(GOAL_TO_NAME[goal], goal in defaults["goaltypes"]), (checkx, y))
	y += 75

def get_input():
	input = {}
	input["numblocks"] = int(inputboxes["numblocks"].text)
	input["numgoals"] = int(inputboxes["numgoals"].text)
	input["num"] = int(inputboxes["numproblems"].text)
	input["goaltypes"] = []
	for obj in guiscreen.objects:
		if hasattr(obj, "label"):
			if obj.label in NAME_TO_GOAL and obj.checked:
				input["goaltypes"].append(NAME_TO_GOAL[obj.label])
	return input

changed = True
while 1:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit(0)
			elif event.key == K_RETURN:
				print_n_blocksworld(get_input())
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
