import heapq, random
from worldsim import domainread, stateread
from block import Block
from pyhop121 import pyhop, methods_broken as methods, operators
from sklearn import svm

class Tower:
	
	def __init__(self, base):
		self.blocks = [Block(base.name)]
	
	def complete(self, world):
		done = False
		while not done:
			changed = False
			done = False
			#print "resetting, base:", self.blocks[0].name
			for atom in world.atoms:
				if atom.predicate.name == "on" and atom.args[1].name == self.blocks[-1].name:
					self.blocks[-1].clear = False
					self.blocks.append(Block(atom.args[0].name))
					self.blocks[-1].on = self.blocks[-2]
					changed = True
				elif atom.predicate.name == "clear" and atom.args[0].name == self.blocks[-1].name:
					done = True
					changed = True
			if not changed:
				raise Exception("Tower found in which top block is not clear")
	
	def __contains__(self, block):
		return block in self.blocks
	
	def height(self):
		return len(self.blocks)
	
	def popTop(self):
		return self.blocks.pop()
	
	def __cmp__(self, other):
		return cmp(other.height(), self.height()) #reversed on purpose

def blocksOrderedByHeight(world, byTower = True):
	towers = []
	blocks = []
	for atom in world.atoms:
		if atom.predicate.name == "on-table":
			towers.append(Tower(atom.args[0]))
		elif atom.predicate.name == "holding":
			heldBlock = Block(atom.args[0].name)
			heldBlock.on = "held"
			heldBlock.clear = False
			blocks.append(heldBlock)
	for tower in towers:
		tower.complete(world)
	heapq.heapify(towers)
	while towers:
		tallest = heapq.heappop(towers)
		blocks.append(tallest.popTop())
		if byTower:
			while tallest.height() > 0:
				blocks.append(tallest.popTop())
		if tallest.height() > 0:
			heapq.heappush(towers, tallest)
	return blocks

def renameByOrder(blocks):
	for i in range(len(blocks)):
		blocks[i].name = "block " + str(i)

def getOnGoals(blocks, goals):
	onGoals = {}
	for goal in goals:
		if goal.goaltype == "on":
			onGoals[goal.goalargs[0]] = goal.goalargs[1]
	return onGoals

#either goals or ongoals. Ongoals is a dict {top: bottom}, goals is a list of midca goals.
def getVector(world, blocks, length = None, goals = [], onGoals = {}):
	vector = []
	if blocks[0].on != 'held':
		vector = [0, 0, 0] #placeholders for arm-empty
	if not onGoals:
		onGoals = getOnGoals(blocks, goals)
	for block in blocks:
		if block.clear:
			vector.append(1)
		else:
			vector.append(0)
		try:
			vector.append(blocks.index(block.on) + 1)
		except ValueError:
			if block.on == "held":
				vector.append(len(blocks)) #held
			else:
				vector.append(0) #on table
		if block in onGoals:
			vector.append(blocks.index(onGoals[block]) + 1)
		else:
			vector.append(0)
	if length:
		if len(vector) < length:
			vector = vector + [0 for i in range(length - len(vector))]
		elif len(vector) > length:
			vector = vector[:length]
	return vector

def randomBlockState(emptyWorld, numBlocks, tableChance = 0.5, holdingChance = 0.3):
	world = emptyWorld
	if random.random() < holdingChance:
		numBlocks -= 1
		world.add_object(world.types["BLOCK"].instantiate("block 0"))
		world.add_fact("holding", ["block 0"])
	else:
		world.add_fact("arm-empty", [])
	for i in range(1, numBlocks + 1):
		if i == 1 or random.random() < tableChance:
			on = None
		else:
			while True:
				objname = random.choice(world.objects.keys())
				if world.is_true("clear", [objname]):
					on = objname
					break
		world.add_object(world.types["BLOCK"].instantiate("block " + str(i)))
		world.add_fact("clear", ["block " + str(i)])
		if on:
			world.add_fact("on", ["block " + str(i), on])
			world.remove_fact("clear", [on])
		else:
			world.add_fact("on-table", ["block " + str(i)])
	return world

def legalGoal(blocks, ongoals, goal):
	#print goal, [(str(block), str(block.on)) for block in blocks]
	if goal[0] in ongoals or goal[1] in ongoals.values():
		return False
	next = goal[1]
	while True:
		if next == goal[0]:
			return False
		if next in ongoals:
			next = ongoals[next]
		else:
			break
	return True

def randomOnGoals(blocks, num):
	ongoals = {}
	if num > len(blocks) - 1:
		raise Exception("Can't have more goals than blocks - 1")
	for i in range(num):
		while True:
			goal = (random.choice(blocks), random.choice(blocks))
			if legalGoal(blocks, ongoals, goal):
				ongoals[goal[0]] = goal[1]
				break
	return ongoals
	

	print [block.name for block in blocksOrderedByHeight(world)]


def pyhop_state_from_world(world, name = "state"):
	s = pyhop.State(name)
	s.pos = {}
	s.clear = {}
	s.holding = False
	s.fire = {}
	s.free = {}
	blocks = []
	for objname in world.objects:
		if world.objects[objname].type.name == "BLOCK" and objname != "table":
			blocks.append(objname)
		elif world.objects[objname].type.name == "ARSONIST":
			s.free[objname] = False
	for atom in world.atoms:
		if atom.predicate.name == "clear":
			s.clear[atom.args[0].name] = True
		elif atom.predicate.name == "holding":
			s.holding = atom.args[0].name
		elif atom.predicate.name == "arm-empty":
			s.holding = False
		elif atom.predicate.name == "on":
			s.pos[atom.args[0].name] = atom.args[1].name
		elif atom.predicate.name == "on-table":
			s.pos[atom.args[0].name] = "table"
		elif atom.predicate.name == "onfire":
			s.fire[atom.args[0].name] = True
		elif atom.predicate.name == "free":
			s.free[atom.args[0].name] = True
	for block in blocks:
		if block not in s.clear:
			s.clear[block] = False
		if block not in s.fire:
			s.fire[block] = False
		if block not in s.pos:
			s.pos[block] = "in-arm"
	return s

def pyhop_tasks_from_goals(goals):
	alltasks = []
	blkgoals = pyhop.Goal("goals")
	blkgoals.pos = {}
	for top, bottom in goals.items():
		blkgoals.pos[top.name] = bottom.name
	if blkgoals.pos:
		alltasks.append(("move_blocks", blkgoals))
	return alltasks

def attemptRandomPlan(emptyWorld, numBlocks = None, maxBlocks = 6):
	vectorLen = (maxBlocks + 1) * 3
	if not numBlocks:
		numBlocks = random.randrange(2, maxBlocks + 1)
	world = randomBlockState(emptyWorld, numBlocks)
	blocks = blocksOrderedByHeight(world)
	goals = randomOnGoals(blocks, random.randrange(1, numBlocks))
	vector = getVector(world, blocks, onGoals = goals, length = vectorLen)
	try:
		plan = pyhop.pyhop(pyhop_state_from_world(world), pyhop_tasks_from_goals(goals), verbose = 0)
		if plan:
			return 1, vector
		else:
			return 1, vector
	except Exception:
		return 0, vector

def testN(n, numBlocks = None, maxBlocks = 6):
	emptyWorld = domainread.load_domain("worldsim/domains/blocks.sim")
	results = []
	vectors = []
	for i in range(n):
		result, vector = attemptRandomPlan(emptyWorld.copy(), numBlocks, maxBlocks)
		results.append(result)
		vectors.append(vector)
	return results, vectors

def precisionRecall(predictions, results):
	assert len(predictions) == len(results)
	fp = 0
	tp = 0
	fn = 0
	tn = 0
	for i in range(len(predictions)):
		if predictions[i] == 0 and results[i] == 0:
			tn += 1
		elif predictions[i] == 0:
			fn += 1
		elif results[i] == 0:
			fp += 1
		else:
			tp += 1
	precision = float(tp + 0.00001) / (tp + fp + 0.00001)
	recall = float(tp + 0.00001) / (tp + fn + 0.00001)
	revPrecision = float(tn + 0.00001) / (tn + fn + 0.00001)
	revRecall = float(tn + 0.00001) / (tn + fp + 0.00001)
	return precision, recall, revPrecision, revRecall

'''
'''
def tryAction(world, goals, action, clf, vectorLen):
	if action:
		world = world.copy()
		world.apply(action)
	#print "trying", action
	blocks = blocksOrderedByHeight(world)
	vector = getVector(world, blocks, onGoals = goals, length = vectorLen)
	result = clf.predict(vector)
	return result, world

def continueFlailing(world, goals, clf, vectorLen, depth):
	results = [(world, [])]
	while depth > 0:
		newResults = []
		for world, actionList in results:
			actions = world.get_possible_actions()
			#print [str(action) for action in actions]
			for action in actions:
				result = tryAction(world, goals, action, clf, vectorLen)
				if result[0] == 1:
					return (result[1], actionList + [action])
				else:
					newResults.append((result[1], actionList + [action]))
		results = newResults
		depth -= 1
	return False #no predicted success in results

def flailToBetterWorld(world, clf, blocks, goals, vectorLen, depth = 1, greedy = True):
	vector = getVector(world, blocks, onGoals = goals, length = vectorLen)
	if clf.predict(vector) == 1:
		return (world, [])
	else:
		return continueFlailing(world, goals, clf, vectorLen, depth)

def getRandomResults(n, emptyWorld, clf, numBlocks, maxBlocks):
	results = []
	for trial in range(n):
		world = randomBlockState(emptyWorld.copy(), numBlocks)
		blocks = blocksOrderedByHeight(world)
		goals = randomOnGoals(blocks, random.randrange(1, len(blocks)))
		vectorLen = (maxBlocks + 1) * 3
		vector = getVector(world, blocks, onGoals = goals, length = vectorLen)
		prediction = clf.predict(vector)
		if prediction == 0:
			world.apply(random.choice(world.get_possible_actions()))
		try:
			plan = pyhop.pyhop(pyhop_state_from_world(world), pyhop_tasks_from_goals(goals), verbose = 0)
			results.append(1)
		except Exception:
			results.append(0)
	return results
		

def getFlailResults(n, emptyWorld, clf, numBlocks, maxBlocks, depth = 1):
	predicted = []
	actual = []
	flailResults = []
	for trial in range(n):
		world = randomBlockState(emptyWorld.copy(), numBlocks)
		blocks = blocksOrderedByHeight(world)
		goals = randomOnGoals(blocks, random.randrange(1, len(blocks)))
		vectorLen = (maxBlocks + 1) * 3
		res = flailToBetterWorld(world, clf, blocks, goals, vectorLen, depth)
		if not res:
			predicted.append(0)
			try:
				plan = pyhop.pyhop(pyhop_state_from_world(world), pyhop_tasks_from_goals(goals), verbose = 0)
				actual.append(1)
			except Exception:
				actual.append(0)
		else:
			world, actions = res
			predicted.append(1)
			try:
				plan = pyhop.pyhop(pyhop_state_from_world(world), pyhop_tasks_from_goals(goals), verbose = 0)
				actual.append(1)
				if actions:
					flailResults.append(1)
			except Exception:
				actual.append(0)
				if actions:
					flailResults.append(0)
	return predicted, actual, flailResults
			

'''
'''

#doRandomAction()
#sys.exit()

def testFlail():
	results, vectors = testN(5000)
	clf = svm.SVC(class_weight = 'auto', C = 1000)
	clf.fit(vectors, results)
	for i in range(2, 7):
		print "testing with", i, "blocks." 
		testRes, testVect = testN(300, i, 6)
		predictions = clf.predict(testVect)
		success = float(sum([1 for n in range(len(predictions)) if predictions[n] == testRes[n]])) / len(predictions)
		print "regular:"
		print "percent correct:", success
		print "percent plans successful (actual):", float(sum(testRes)) / len(testRes)
		print precisionRecall(predictions, testRes)
		print
		
		print "with flail:"
		emptyWorld = domainread.load_domain("worldsim/domains/blocks.sim")
		predicted, actual, flailResults = getFlailResults(300, emptyWorld, clf, i, 6, depth = 2)
		predictSuccess = float(sum([1 for n in range(len(predicted)) if predicted[n] == actual[n]])) / len(predicted)
		print "percent correct:", predictSuccess
		print "percent plans successful (actual):", float(sum(actual)) / len(actual)
		print precisionRecall(predicted, actual)
		print
		
		randResults = getRandomResults(300, emptyWorld, clf, i, 6)
		print "Random action: ", float(sum(randResults)) / len(randResults)

testFlail()

def testNoFlail():
	results, vectors = testN(10000)
	clf = svm.SVC(class_weight = 'auto', C = 1000)
	clf.fit(vectors, results)
	for i in range(2, 7):
		print "testing with", i, "blocks." 
		testRes, testVect = testN(1000, i, 6)	
		predictions = clf.predict(testVect)
		success = float(sum([1 for i in range(len(predictions)) if predictions[i] == testRes[i]])) / len(predictions)
		print "percent correct:", success
		print "percent plans successful (actual):", float(sum(testRes)) / len(testRes)
		print precisionRecall(predictions, testRes)
		print