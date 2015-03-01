import sys, copy, random
sys.path.append("../")
from problem_generator.logistics import planner2 as planner, simulator, generator as generate
from os import listdir
from os.path import isfile, join
from utils import adistadapt
from utils.adist import ADistance, ChangeFinder, WindowPair, Interval
from gng import gng

###############
##### Loading pred count files
###############

def get_plan_vectors(filename):
	file = open(filename)
	txt = file.read()[1:-1] #remove outer parens
	txt = txt.replace("NIL", "")
	plans = txt.replace("(", "").replace("\n", "").split("))")
	for plan in range(len(plans)):
		plans[plan] = plans[plan].split(")")
		for step in range(len(plans[plan])):
			plans[plan][step] = plans[plan][step].split()		
			for count in range(len(plans[plan][step])):
				plans[plan][step][count] = plans[plan][step][count].strip()
				plans[plan][step][count] = int(plans[plan][step][count])
	file.close()
	return plans[:-1]
	
################
##### Worlds -> plan vectors
###############

def gen_plan(state, noops = []):
	getFunc = planner.action_restricted_func(noops)
	return planner.a_star(state, get_actions = getFunc, type = "greedy")

def gen_plans(states, noops = []):
	plans = []
	getFunc = planner.action_restricted_func(noops)
	for state in states:
		plans.append(planner.a_star(state, get_actions = getFunc, type = "greedy"))
	return plans

#by default, loads all valid problem files
def worlds_from_prob_files(filedir, fileprefix = ""):
	files = [ f for f in listdir(filedir) if isfile(join(filedir,f)) and fileprefix in f]
	worlds = []
	for file in files:
		file = join(filedir, file)
		try:
			f = open(file)
			text = f.read()
			objects, state = simulator.parse_state(text)
			world = simulator.LogisticsWorld(objects, state)
			world.goals = simulator.parse_goals(text)
		except Exception:
			world = None
		if not world or not world.cities:
			print "File " + file + " is not a valid problem file. Skipping."
		else:
			worlds.append(world)
		f.close()
	return worlds

#only includes changeable predicates
logisticsPreds = ["inside-truck", "inside-airplane", "at-object"]

def pred_counts(world):
	counts = []
	for i in range(len(logisticsPreds)):
		counts.append(0)
	for package in world.packages.values():
		if package.loc.type == "truck":
			counts[0] += 1
		elif package.loc.type == "plane":
			counts[1] += 1
		else:
			counts[2] += 1
	return counts

def dif_vector(newVect, oldVect):
	return [new - old for new, old in zip(newVect, oldVect)]

def dif_vectors(world, plan):
	vectors = []
	lastv = pred_counts(world)
	for step in plan:
		world.execute_action(step)
		newv = pred_counts(world)
		vectors.append(dif_vector(newv, lastv))
		lastv = newv
	return vectors
		
def write_vectors(planVectors, filename):
	f = open(filename, "w")
	s = "("
	for planVector in planVectors:
		s += "("
		for difVector in planVector:
			s += "("
			for val in difVector:
				s += str(val) + " "
			s = s[:-1] + ") "
		s = s[:-1] + ") "
	s = s[:-1] + ")"
	f.write(s)
	f.close()

###############
##### Analysis
###############

def get_relevant_plan_indices(planlengths, step, windowsize = 100):
	sum = 0
	i = 0
	while sum <= step - windowsize:
		if i == len(planlengths):
			return []
		sum += planlengths[i]
		i += 1
	planindices = []
	if i > 0:
		planindices.append(i - 1)
	while sum < step:
		if i == len(planlengths):
			return [planindices]
		planindices.append(i)
		sum += planlengths[i]
		i += 1
	return planindices

def get_relevant_plan_counts(planlengths, steps, windowsize = 100):
	counts = {}
	for step in steps:
		indices = get_relevant_plan_indices(planlengths, step)
		for index in indices:
			if index in counts:
				counts[index] += 1
			else:
				counts[index] = 1
	return counts

#returns the start of a plan
def get_start_step(planlengths, planindex):
	return sum(planlengths[:planindex])	

def get_node_hit_steps(net, vectors):
	hits = {}
	for index in range(len(vectors)):
		node = net.closest_node(vectors[index])[0]
		if node in hits:
			hits[node].append(index)
		else:
			hits[node] = [index]
	return hits

def get_node_mean_errors(net, vectors):
	errors = {}
	hits = {}
	for vector in vectors:
		node, dist = net.closest_node(vector)
		if node in errors:
			errors[node] += dist
			hits[node] += 1
		else:
			errors[node] = dist
			hits[node] = 1
	for node in errors:
		errors[node] /= hits[node]
	return errors

def get_anomaly_value_list(plans):
	vals = []
	for plan in plans:
		for i in range(len(plan)):
			vals.append(plan.anomaly)
	return vals
	
###############
##### Test Integration & Initialization
###############

def gen_and_write_vectors(probfiledir, vectordir, n, vectfilename = "vectors.lisp", probfileid = "", noops = [], plandir = None, planfilename = ""):
	worlds = worlds_from_prob_files(probfiledir, probfileid)
	plans = gen_plans(worlds[:n], noops)
	planVectors = []
	for plan in range(len(plans)):
		if plans[plan]:
			if plandir:
				f = open(plandir + planfilename + str(plan + 1), "w")
				for step in plans[plan][1]:
					f.write(str(step) + "\n")
				f.close()
			vectors = dif_vectors(copy.deepcopy(worlds[plan]), plans[plan][1])
			planVectors.append(vectors)
	write_vectors(planVectors, vectordir + vectfilename)

def init_ADist(vectors, windowsize = 100, threshold = 0.5):
	cfs = []
	for n in range(len(vectors[0])):
		distobj = ADistance.ADistance()
		cf = ChangeFinder.ChangeFinder(distobj)
		for i in [-1.5, -0.5, 0.5]:
			distobj.add(Interval.Interval(i, i + 1))
		cf.addWindowPair(WindowPair.WindowPair(windowsize, windowsize, threshold))
		distobj.init(cf)
		cfs.append(cf)
	return cfs

def init_gng(vectors):
	net = gng.GNG(len(vectors[0]))
	#net.combinefreq = 500
	#net.combinemultiplier = 1.0
	#net.numdeviations = 2.0
	net.nodeLearningRate = 0.05
	net.neighborLearningRate = 0
	net.maxDistance = 0.09
	#net.minDistance = 0.04
	net.newNodeInterval = 200
	net.maximumAge = 1000
	return net

def run(difvectors, cfs, net = None):
	distVectors = []
	i = 0
	for dif in difvectors:
		if i % 1000 == 0:
			print "step ", i
			if net:
				print "nodes: ", len(net.nodes)
		distVector = []
		for cf in range(len(cfs)):
			if len(dif) != len(cfs):
				print "oy", dif, difvectors[difvectors.index(dif) - 3:], len(cfs), len(difvectors), len(difvectors[difvectors.index(dif):])
			cfs[cf].addData(dif[cf])
			distVector.append(cfs[cf].getDistances()[0])
		if net:
			net.update(distVector)
		distVectors.append(distVector)
		i += 1
	#if net:
		#net.consolidate()
		#net.cleanup()
		#print "nodes: ", len(net.nodes)
	return distVectors

probfiledir = "./probs/"
vectordir = "./vectors/"
plandir = "./plans/"

def write_prob_and_vect_files(probfiledir, vectordir, plandir, n, probfilename = "", vectfilename = "vectors.lisp", planfilename = "", noops = []):
	genInput = generate.defaults
	genInput["num"] = n
	generate.print_n_logistics(input = genInput, dir = probfiledir, name = probfilename)
	print str(n) + " problem files written to " + probfiledir + probfilename
	gen_and_write_vectors(probfiledir, vectordir, n, vectfilename, probfilename, noops, plandir, planfilename)
	print str(n) + " plan vectors written to " + vectordir + vectfilename

def get_worlds_and_plans(n, predsmissing):
	numpercycle = 10
	#normal data
	worlds = []
	plans = []
	while len(plans) < n:
		worlds += generate.get_n_logistics(numprobs = numpercycle)
		plans += gen_plans(worlds[-numpercycle:], predsmissing)
		i = len(plans) - numpercycle
		while i < len(plans):
			if not plans[i]:
				del worlds[i]
				del plans[i]
			else:
				i += 1
		print str(len(plans)) + " of " + str(n) + " plans generated."
	worlds = worlds[:n]
	plans = plans[:n]
	assert len(worlds) == n and len(plans) == n
	return worlds, plans

def write_plans_get_vectors(worlds, plans, plandir, planfilename, startindex = 0):
	planVectors = []
	for plan in range(len(plans)):
		if plans[plan]:
			if plandir:
				f = open(plandir + planfilename + str(plan + 1 + startindex), "w")
				for step in plans[plan][1]:
					f.write(str(step) + "\n")
				f.close()
			vectors = dif_vectors(copy.deepcopy(worlds[plan]), plans[plan][1])
			planVectors.append(vectors)
	return planVectors


def write_worlds(worlds, dir, filename, startindex = 0):
	for i in range(len(worlds)):
		f = open(dir + filename + str(i + 1 + startindex), "w")
		f.write(worlds[i].get_prob_str("prob" + str(i + 1 + startindex)))
		f.close()

def write_norm_and_anomalous_test_set(testname, nNormal, nAnomalous, anomalystart, basedir, predsmissing):
	#normal set 1
	worlds1, plans1 = get_worlds_and_plans(min(anomalystart, nNormal), [])
	vectors = write_plans_get_vectors(worlds1, plans1, basedir + "plans/", testname)
	write_worlds(worlds1, basedir + "probs/", testname)
	
	#anomalous
	worlds2, plans2 = get_worlds_and_plans(nAnomalous, predsmissing)
	vectors += write_plans_get_vectors(worlds2, plans2, basedir + "plans/", testname, startindex = anomalystart)
	write_worlds(worlds2, basedir + "probs/", testname, startindex = anomalystart)
	
	#normal set 2
	worlds3, plans3 = get_worlds_and_plans(max(nNormal - anomalystart, 0), [])
	vectors += write_plans_get_vectors(worlds3, plans3, basedir + "plans/", testname, startindex = anomalystart + nAnomalous)
	write_worlds(worlds3, basedir + "probs/", testname, startindex = anomalystart + nAnomalous)
	
	write_vectors(vectors, basedir + "vectors/" + testname)

def write_norm_and_2_anomalous_test_set(testname, nNormal, nAnoms, anomStarts, basedir, predsmissing):
	#normal set 1
	worlds, plans = get_worlds_and_plans(min(anomStarts[0], nNormal), [])
	vectors = write_plans_get_vectors(worlds, plans, basedir + "plans/", testname)
	write_worlds(worlds, basedir + "probs/", testname)
	
	#anomaly1
	worlds, plans = get_worlds_and_plans(nAnoms[0], predsmissing[0])
	vectors += write_plans_get_vectors(worlds, plans, basedir + "plans/", testname, startindex = anomStarts[0])
	write_worlds(worlds, basedir + "probs/", testname, startindex = anomStarts[0])
	
	#normal set 2
	worlds, plans = get_worlds_and_plans(max(min(anomStarts[1] - anomStarts[0] - nAnoms[0], nNormal - anomStarts[0] - nAnoms[0]), 0), [])
	vectors += write_plans_get_vectors(worlds, plans, basedir + "plans/", testname, startindex = anomStarts[0] + nAnoms[0])
	write_worlds(worlds, basedir + "probs/", testname, startindex = anomStarts[0] + nAnoms[0])
	
	#anomaly2
	worlds, plans = get_worlds_and_plans(nAnoms[1], predsmissing[1])
	vectors += write_plans_get_vectors(worlds, plans, basedir + "plans/", testname, startindex = anomStarts[1])
	write_worlds(worlds, basedir + "probs/", testname, startindex = anomStarts[1])
	
	#normal set 3
	worlds, plans = get_worlds_and_plans(nNormal - anomStarts[1] + nAnoms[0], [])
	vectors += write_plans_get_vectors(worlds, plans, basedir + "plans/", testname, startindex = anomStarts[1] + nAnoms[1])
	write_worlds(worlds, basedir + "probs/", testname, startindex = anomStarts[1] + nAnoms[1])
	
	write_vectors(vectors, basedir + "vectors/" + testname)
		
###############
##### Old Style Tests
###############

def get_adist_bool_vector(distvects, epsilon):
	bools = []
	for vect in distvects:
		hit = False
		for val in vect:
			if val > epsilon:
				hit = True
				break
		bools.append(hit)
	assert len(bools) == len(distvects)
	return bools

#returns list of (bool, intensity)
def get_adist_bool_vector_complex(distvects, epsilon, plans):
	anomalylist = get_anomaly_value_list(plans)
	assert len(anomalylist) == len(distvects)
	bools = []
	window = []
	for i in range(len(distvects)):
		if len(window) == 100:
			window.pop(0)
		window.append(anomalylist[i])
		intensity = 0
		for val in window:
			if val > 0:
				intensity += 1
		intensity /= 100.0
		hit = False
		for val in distvects[i]:
			if val > epsilon:
				hit = True
		bools.append((hit, intensity))
	return bools

#returns list of (bool, intensity)
def get_adist_bool_vector_complex_new(distvects, epsilons, plans):
	anomalylist = get_anomaly_value_list(plans)
	assert len(anomalylist) == len(distvects)
	bools = []
	window = []
	for i in range(len(distvects)):
		if len(window) == 100:
			window.pop(0)
		window.append(anomalylist[i])
		intensity = sum(window) / 100.0
		hit = False
		for val in range(len(distvects[i])):
			if distvects[i][val] > epsilons[val]:
				hit = True
		bools.append((hit, intensity))
	return bools	

def get_gng_bool_vector_old(distvects, net, maxdist):
	bools = []
	zero = [0 for i in range(len(distvects[0]))]
	for vect in distvects:
		node, dist = net.closest_node(vect)
		if gng.distance(zero, node.location) > maxdist:
			bools.append(True)
		else:
			bools.append(False)
	assert len(bools) == len(distvects)
	return bools

def get_gng_bool_vector(distvects, net):
	bools = []
	zero = [0 for i in range(len(distvects[0]))]
	minnode, mindist = net.closest_node(zero)
	for vect in distvects:
		node, dist = net.closest_node(vect)
		if node != minnode:
			bools.append(True)
		else:
			bools.append(False)
	assert len(bools) == len(distvects)
	return bools

def get_gng_bool_vector_complex(distvects, net, plans, maxnorm):
	anomalylist = get_anomaly_value_list(plans)
	bools = []
	window = []
	zero = [0 for i in range(len(distvects[0]))]
	for i in range(len(distvects)):
		if len(window) == 100:
			window.pop(0)
		window.append(anomalylist[i])
		intensity = 0
		for val in window:
			if val > 0:
				intensity += 1
		intensity /= (1.0 * max(1, len(window)))
		vect = distvects[i]
		node, dist = net.closest_node(vect)
		if gng.distance(node.location, zero) > maxnorm:
			bools.append((True, intensity))
		else:
			bools.append((False, intensity))
	assert len(bools) == len(distvects)
	return bools

def correctness_str(boolvect, anomalystart, anomalyend):
	s = ""
	for i in range(len(boolvect)):
		if boolvect[i]:
			if i > anomalystart and i < anomalyend:
				s += '\033[94m' + str(i) + " " + '\033[0m'
			else:
				s += str(i) + " "
	return s

class HMFT:
	
	def __init__(self, intensity, threshold = 0.5):
		self.hits = 0
		self.misses = 0
		self.fps = 0
		self.tns = 0
		self.intensity = intensity
		self.threshold = threshold
	
	def __getitem__(self, item):
		if item == 0:
			return self.hits
		elif item == 1:
			return self.misses
		elif item == 2:
			return self.fps
		elif item == 3:
			return self.tns
	
	def hit(self):
		if self.intensity >= self.threshold:
			self.hits += 1
		else:
			self.fps += 1
	
	def miss(self):
		if self.intensity >= self.threshold:
			self.misses += 1
		else:
			self.tns += 1

def correctness_distribution(boolvect, anomalystart, anomalyend):
	hits = 0
	misses = 0
	fps = 0
	tns = 0
	for i in range(len(boolvect)):
		anomaly = i > anomalystart and i < anomalyend
		if boolvect[i]:
			if anomaly:
				hits += 1
			else:
				fps += 1
		elif anomaly:
			misses += 1
		else:
			tns += 1
	return hits, misses, fps, tns

#takes in list of (bool, intensity) rather than list of bool. Returns a dict of {intensity: HMFT}
def correctness_distribution_complex(boolvect):
	hmfts = {}
	for i in range(len(boolvect)):
		bool, intensity = boolvect[i]
		if intensity not in hmfts:
			hmfts[intensity] = HMFT(intensity)
		if bool:
			hmfts[intensity].hit()
		else:
			hmfts[intensity].miss()
	return hmfts

def precision(hmfts):
	hits = 0
	fps = 0
	for hmft in hmfts:
		hits += hmft.hits
		fps += hmft.fps
	if hits + fps == 0:
		return 0.0
	return 1.0 * hits / (hits + fps)

def recall(hmfts):
	hits = 0
	misses = 0
	for hmft in hmfts:
		hits += hmft.hits
		misses += hmft.misses
	if hits + misses == 0:
		return 1.0
	return 1.0 * hits / (hits + misses)

def f1(hmfts):
	pr = precision(hmfts)
	rec = recall(hmfts)
	if pr == 0 and rec == 0:
		return 0
	return 2 * pr * rec / (pr + rec)

def accuracy(hmfts):
	good = 0
	bad = 0
	for hmft in hmfts:
		good += hmft.hits + hmft.tns
		bad += hmft.misses + hmft.fps
	if bad + good == 0:
		return 0
	else:
		return 1.0 * good / (good + bad)

class Plan:
	
	def __init__(self, vectors, anomaly = 0):
		self.vectors = vectors
		self.anomaly = anomaly
	
	def __len__(self):
		return len(self.vectors)
	
	def __iter__(self):
		return self.vectors.__iter__()
	
	def __getitem__(self, item):
		return self.vectors.__getitem__(item)
	
	def anomalous(self):
		return self.anomaly > 0

def get_difs(difsfile, anomalystart, anomalyend):
	vectors = get_plan_vectors(difsfile)
	normaldifs = [Plan(vector) for vector in vectors[:anomalystart] + vectors[anomalyend:]]
	anomalousdifs = [Plan(vector, 1) for vector in vectors[anomalystart:anomalyend]]
	return normaldifs, anomalousdifs

def get_difs_2(difsfile, anomalystarts, anomalylengths):
	vectors = get_plan_vectors(difsfile)
	normaldifs = [Plan(vector) for vector in vectors[:anomalystarts[0]] + vectors[anomalystarts[0] + anomalylengths[0]:anomalystarts[1]] + vectors[anomalystarts[1] + anomalylengths[1]:]]
	anomalous1 = anomalousdifs = [Plan(vector, 1) for vector in vectors[anomalystarts[0]:anomalystarts[0] + anomalylengths[0]]]
	anomalous2 = anomalousdifs = [Plan(vector, 2) for vector in vectors[anomalystarts[1]:anomalystarts[1] + anomalylengths[1]]]
	return normaldifs, anomalous1, anomalous2

def shuffled_difs(normaldifs, anomalousdifs, intensity, newstart):
	normaldifs = normaldifs[:]
	anomalousdifs = anomalousdifs[:]
	newanomaly = []
	anomalylength = len(anomalousdifs)
	numanomalous = int(round(intensity * len(anomalousdifs), 0))
	for i in range(numanomalous):
		vecti = random.choice(range(len(anomalousdifs)))
		newanomaly.append(anomalousdifs.pop(vecti))
	while len(newanomaly) < anomalylength:
		vecti = random.choice(range(len(normaldifs)))
		newanomaly.append(normaldifs.pop(vecti))
	random.shuffle(newanomaly)
	random.shuffle(normaldifs)
	if numanomalous > 0:
		normaldifs = normaldifs[:-numanomalous]
	return normaldifs[:newstart] + newanomaly + normaldifs[newstart:]

def create_random_trial(normaldifs, anomalousdifs, intensity, newstart):
	difs = shuffled_difs(normaldifs, anomalousdifs, intensity, newstart)
	assert len(difs) == len(normaldifs)
	planlengths = []
	vectors = []
	for plan in difs:
		planlengths.append(len(plan))
		vectors += plan
	assert sum(planlengths) == len(vectors)
	return vectors, planlengths, difs

def shuffled_difs_new(normaldifs, anomalousdifs, intensity, starts):
	normaldifs = normaldifs[:]
	anomalous1 = anomalousdifs[0][:]
	anomalous2 = anomalousdifs[1][:]
	newanomaly1 = []
	newanomaly2 = []
	len1 = len(anomalous1)
	len2 = len(anomalous2)
	numanom1 = int(round(intensity * len1, 0))
	numanom2 = int(round(intensity * len2, 0))
	for i in range(numanom1):
		vecti = random.choice(range(len(anomalous1)))
		newanomaly1.append(anomalous1.pop(vecti))
	while len(newanomaly1) < len1:
		vecti = random.choice(range(len(normaldifs)))
		newanomaly1.append(normaldifs.pop(vecti))
	for i in range(numanom2):
		vecti = random.choice(range(len(anomalous2)))
		newanomaly2.append(anomalous2.pop(vecti))
	while len(newanomaly2) < len2:
		vecti = random.choice(range(len(normaldifs)))
		newanomaly2.append(normaldifs.pop(vecti))
	random.shuffle(newanomaly1)
	random.shuffle(newanomaly2)
	random.shuffle(normaldifs)
	if numanom1 + numanom2 > 0:
		normaldifs = normaldifs[:-(numanom1 + numanom2)]
	return normaldifs[:starts[0]] + newanomaly1 + normaldifs[starts[0]:starts[1] - len1] + newanomaly2 + normaldifs[starts[1] - len1:]

def create_random_trial_new(normaldifs, anomalousdifs, intensity, starts):
	difs = shuffled_difs_new(normaldifs, anomalousdifs, intensity, starts)
	assert len(difs) == len(normaldifs)
	planlengths = []
	vectors = []
	for plan in difs:
		planlengths.append(len(plan))
		vectors += plan.vectors
	assert sum(planlengths) == len(vectors)
	return vectors, planlengths, difs

class Result:
	
	def __init__(self):
		self.byepsilon = {}
		self.byintensity = {}
	
	def add(self, epsilon, intensity, hmft):
		if epsilon in self.byepsilon:
			if intensity in self.byepsilon[epsilon]:
				self.byepsilon[epsilon][intensity].append(hmft)
			else:
				self.byepsilon[epsilon][intensity] = [hmft]
		else:
			self.byepsilon[epsilon] = {}
			self.byepsilon[epsilon][intensity] = [hmft]
		if intensity in self.byintensity:
			if epsilon in self.byintensity[intensity]:
				self.byintensity[intensity][epsilon].append(hmft)
			else:
				self.byintensity[intensity][epsilon] = [hmft]
		else:
			self.byintensity[intensity] = {}
			self.byintensity[intensity][epsilon] = [hmft]
	
	def save_results(self, dir, trialnum = ""):
		#by epsilon
		epsilons = sorted(self.byepsilon.keys())
		epsStr = "epsilon\tPrecision\tRecall\tF1\n"
		for epsilon in epsilons:
			epsStr += str(epsilon) + "\t"
			allhmfts = []
			for hmfts in self.byepsilon[epsilon].values():
				allhmfts += hmfts
			epsStr += str(precision(allhmfts)) + "\t"
			epsStr += str(recall(allhmfts)) + "\t"
			epsStr += str(f1(allhmfts)) + "\n"
		#do by intensity
		intensities = sorted(self.byintensity.keys())
		recStr = "Recall:\n"
		prStr = "Precision:\n"
		f1Str = "F1:\n"
		accStr = "Accuracy:\n"
		for epsilon in epsilons:
			recStr += "\tepsilon = " + str(epsilon)
			prStr += "\tepsilon = " + str(epsilon)
			f1Str += "\tepsilon = " + str(epsilon)
			accStr += "\tepsilon = " + str(epsilon)
		for intensity in intensities:
			recStr += "\n"
			prStr += "\n"
			f1Str += "\n"
			accStr += "\n"
			recStr += str(intensity)
			prStr += str(intensity)
			f1Str += str(intensity)
			accStr += str(intensity)
			for epsilon in self.byintensity[intensity]:
				recStr += "\t" + str(recall(self.byintensity[intensity][epsilon]))
				prStr += "\t" + str(precision(self.byintensity[intensity][epsilon]))
				f1Str += "\t" + str(f1(self.byintensity[intensity][epsilon]))
				accStr += "\t" + str(accuracy(self.byintensity[intensity][epsilon]))
		
		f = open(dir + "by_eps_" + trialnum + ".tsv", "w")
		f.write(epsStr)
		f.close()
		f = open(dir + "recall_" + trialnum + ".tsv", "w")
		f.write(recStr)
		f.close()
		f = open(dir + "precison_" + trialnum + ".tsv", "w")
		f.write(prStr)
		f.close()
		f = open(dir + "F1_" + trialnum + ".tsv", "w")
		f.write(f1Str)
		f.close()
		f = open(dir + "accuracy_" + trialnum + ".tsv", "w")
		f.write(accStr)
		f.close()

testepsilons = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
testintensities = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

def get_epsilons(changefinders, normal, n = 10, cutoff = 0.95):
	epsilons = []
	for i in range(len(changefinders)):
		cf = changefinders[i]
		cf.computeAlphas([vect[i] for vect in normal], cutoff, n)
		epsilons.append(cf.windowPairs[0].alpha)
	return epsilons

def run_trials(difsfile, anomalystart, anomalyend, numtrials = 1, name = "res"):
	normal, anomalous = get_difs(difsfile, anomalystart, anomalyend)
	res = Result()
	for i in range(numtrials):
		for intensity in testintensities:
			vectors, planlengths = create_random_trial(normal, anomalous, intensity, anomalystart)
			changefinders = init_ADist(vectors)
			dists = run(vectors, changefinders)
			anomalystarti = get_start_step(planlengths, anomalystart) + 50
			anomalyendi = get_start_step(planlengths, anomalyend) + 50
			for epsilon in testepsilons:
				dists = correctness_distribution_complex(get_adist_bool_vector_complex(dists, epsilon, vectors))
				if intensity > 0:
					res.add(epsilon, intensity, correctness_distribution(get_adist_bool_vector(dists, epsilon), anomalystarti, anomalyendi))
				else: #no anomaly
					res.add(epsilon, intensity, correctness_distribution(get_adist_bool_vector(dists, epsilon), anomalystarti, anomalystarti))
	res.save_results("./", name)

def run_trials_new(difsfile, anomalystart, anomalyend, numtrials = 1, name = "res"):
	normal, anomalous = get_difs(difsfile, anomalystart, anomalyend)
	res = Result()
	for i in range(numtrials):
		for intensity in testintensities:			
			vectors, planlengths, plans = create_random_trial_new(normal, anomalous, intensity, anomalystart)
			changefinders = init_ADist(vectors)
			dists = run(vectors, changefinders)
			anomalystarti = get_start_step(planlengths, anomalystart) + 50
			anomalyendi = get_start_step(planlengths, anomalyend) + 50
			for epsilon in testepsilons:
				distrs = correctness_distribution_complex(get_adist_bool_vector_complex(dists, epsilon, plans))
				for actualintensity, hmft in distrs.items():
					res.add(epsilon, actualintensity, hmft)
	res.save_results("./", name)

def run_trials_new_2_anoms(difsfile, anomalystarts, anomalylengths, numtrials = 1, name = "res"):
	normal, anomalous1, anomalous2 = get_difs_2(difsfile, anomalystarts, anomalylengths)
	res = Result()
	for i in range(numtrials):
		for intensity in testintensities:			
			vectors, planlengths, plans = create_random_trial_new(normal, (anomalous1, anomalous2), intensity, anomalystarts)
			changefinders = init_ADist(vectors)
			dists = run(vectors, changefinders)
			#anomalystarti = get_start_step(planlengths, anomalystart) + 50
			#anomalyendi = get_start_step(planlengths, anomalyend) + 50
			for epsilon in testepsilons:
				distrs = correctness_distribution_complex(get_adist_bool_vector_complex(dists, epsilon, plans))
				for actualintensity, hmft in distrs.items():
					res.add(epsilon, actualintensity, hmft)
	res.save_results("./", name)

def get_max_norm_dist(normal, numtrials = 1, maxDist = 1.0):
	distances = []
	for i in range(numtrials):
		vectors, planlengths, plans = create_random_trial(normal, [], 1, 0)
		zerov = [0 for i in range(len(vectors[0]))]
		changefinders = init_ADist(vectors)
		net = init_gng(vectors)
		net.maxDist = maxDist
		dists = run(vectors, changefinders, net)
		for node in net.nodes:
			if node.updates > 30:
				distances.append(gng.distance(zerov, node.location))
	distances.sort()
	eightieth = int(len(distances) * 0.8)
	ninetyfifth = int(len(distances) * 0.95)
	fortieth = int(len(distances) * 0.4)
	return distances[ninetyfifth], distances[fortieth]

def run_trials_new_2_anoms_gng(difsfile, anomalystarts, anomalylengths, numtrials = 1, name = "res", maxDist = 1.5):
	normal, anomalous1, anomalous2 = get_difs_2(difsfile, anomalystarts, anomalylengths)
	max, min = get_max_norm_dist(normal, numtrials = 10, maxDist = maxDist)
	print "dist", max
	res1 = Result()
	res2 = Result()
	for i in range(numtrials):
		for intensity in testintensities:			
			print "Trial ", i
			vectors, planlengths, plans = create_random_trial_new(normal, (anomalous1, anomalous2), intensity, anomalystarts)
			changefinders = init_ADist(vectors)
			net = init_gng(vectors)
			net.maxDistance = maxDist
			dists = run(vectors, changefinders, net)
			#anomalystarti = get_start_step(planlengths, anomalystart) + 50
			#anomalyendi = get_start_step(planlengths, anomalyend) + 50
			for epsilon in ["gng"]:
				distrs = correctness_distribution_complex(get_gng_bool_vector_complex(dists, net, plans, max))
				for actualintensity, hmft in distrs.items():
					res1.add(epsilon, actualintensity, hmft)
					res2.add(epsilon, intensity, hmft)
			for epsilon in [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]:
				distrs = correctness_distribution_complex(get_adist_bool_vector_complex(dists, epsilon, plans))
				for actualintensity, hmft in distrs.items():
					res1.add(epsilon, actualintensity, hmft)
					res2.add(epsilon, intensity, hmft)
	res1.save_results("./actual", name)
	res2.save_results("./projected", name)

def get_nodes_in_2_anomalies(difsfile, anomalystarts, anomalylengths, maxDist = 1.1):
	normal, anomalous1, anomalous2 = get_difs_2(difsfile, anomalystarts, anomalylengths)
	vectors, planlengths, plans = create_random_trial_new(normal, (anomalous1, anomalous2), 0.7, anomalystarts)
	changefinders = init_ADist(vectors)
	net = init_gng(vectors)
	net.maxDistance = maxDist
	for i in range(1):
		dists = run(vectors, changefinders, net)
	anomalystarti1 = get_start_step(planlengths, anomalystarts[0]) - 100
	anomalystarti2 = get_start_step(planlengths, anomalystarts[1]) - 100
	anomalyendi1 = get_start_step(planlengths, anomalystarts[0] + anomalylengths[0]) + 100 + 100
	anomalyendi2 = get_start_step(planlengths, anomalystarts[1] + anomalylengths[1]) + 100 + 100
	nodeindices1 = []
	nodeindices2 = []
	orderedNodes = ordered_nodes(net.nodes)
	for step in range(anomalystarti1, min(anomalyendi1, len(dists))):
		node = net.closest_node(dists[step])[0]
		nodeindices1.append(orderedNodes.index(node))
	for step in range(anomalystarti2, min(anomalyendi2, len(dists))):
		node = net.closest_node(dists[step])[0]
		nodeindices2.append(orderedNodes.index(node))
	return nodeindices1, nodeindices2, orderedNodes

def run_gng_trials_old(difsfile, anomalystart, anomalyend, numtrials = 1, name = "Trial", maxDist = 1.0):
	normal, anomalous = get_difs(difsfile, anomalystart, anomalyend)
	max, min = get_max_norm_dist(normal, numtrials = 10, maxDist = maxDist)
	res = Result()
	distVs = []
	nets = []
	lengths = []
	for i in range(numtrials):
		for intensity in [1]:
			print "Trial ", i
			vectors, planlengths = create_random_trial(normal, anomalous, intensity, 200)
			changefinders = init_ADist(vectors)
			net = init_gng(vectors)
			net.numdeviations = gngdevs
			for i in range(5):
				dists = run(vectors, changefinders, net)
			anomalystarti = get_start_step(planlengths, 200) + 50
			anomalyendi = get_start_step(planlengths, 300) + 50
			distVs.append(dists)
			nets.append(net)
			lengths.append(planlengths)
			if intensity > 0:
				res.add(0, intensity, correctness_distribution(get_gng_bool_vector(dists, net), anomalystarti, anomalyendi))
			else: #no anomaly
				res.add(0, intensity, correctness_distribution(get_gng_bool_vector(dists, net), anomalystarti, anomalystarti))
	res.save_results("./", name)
	print "small : large", max, min
	for net in nets:
		print net.smallupdates, net.largeupdates
	return max		
	
def run_gng_trials_new(difsfile, anomalystart, anomalyend, numtrials = 1, name = "res", maxDist = 1.0, realintensity = True):
	normal, anomalous= get_difs(difsfile, anomalystart, anomalyend)
	max, min = get_max_norm_dist(normal, numtrials = 10, maxDist = maxDist)
	print "dist", max
	#vectors, planlengths, plans = create_random_trial(normal, [], 0, 0)
	#startnet = init_gng(vectors)
	#for i in range(5):
		#vectors, planlengths, plans = create_random_trial(normal, [], 0, 0)
		#changefinders = init_ADist(vectors)
		#run(vectors, changefinders, startnet)	
	res = Result()
	for i in range(numtrials):
		for intensity in testintensities:			
			print "Trial ", i
			vectors, planlengths, plans = create_random_trial(normal, anomalous, intensity, anomalystart)
			changefinders = init_ADist(vectors)
			net = init_gng(vectors)
			#net = copy.deepcopy(startnet)
			net.maxDist = maxDist
			dists = run(vectors, changefinders, net)
			#anomalystarti = get_start_step(planlengths, anomalystart) + 50
			#anomalyendi = get_start_step(planlengths, anomalyend) + 50
			distrs = correctness_distribution_complex(get_gng_bool_vector_complex(dists, net, plans, max))
			for actualintensity, hmft in distrs.items():
				if realintensity:
					res.add("gng", actualintensity, hmft)
				else:
					res.add("gng", intensity, hmft)
			for epsilon in [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]:
				distrs = correctness_distribution_complex(get_adist_bool_vector_complex(dists, epsilon, plans))
				for actualintensity, hmft in distrs.items():
					if realintensity:
						res.add(epsilon, actualintensity, hmft)
					else:
						res.add(epsilon, intensity, hmft)
	res.save_results("./", name)

def run_gng_trials_calc_eps(difsfile, anomalystart, anomalyend, numtrials = 1, name = "res", maxDist = 1.0, realintensity = True):
	normal, anomalous= get_difs(difsfile, anomalystart, anomalyend)
	max, min = get_max_norm_dist(normal, numtrials = 10, maxDist = maxDist)
	print "dist", max
	vectors, planlengths, plans = create_random_trial(normal, [], 0, 0)
	changefinders = init_ADist(vectors)
	epsilons = get_epsilons(changefinders, vectors, n = 200, cutoff = 0.96)
	#vectors, planlengths, plans = create_random_trial(normal, [], 0, 0)
	#startnet = init_gng(vectors)
	#for i in range(5):
		#vectors, planlengths, plans = create_random_trial(normal, [], 0, 0)
		#changefinders = init_ADist(vectors)
		#run(vectors, changefinders, startnet)	
	res1 = Result()
	res2 = Result()
	lengths = []
	for i in range(numtrials):
		for intensity in testintensities:			
			print "Trial ", i
			vectors, planlengths, plans = create_random_trial(normal, anomalous, intensity, anomalystart)
			lengths.append(len(vectors))
			changefinders = init_ADist(vectors)
			net = init_gng(vectors)
			#net = copy.deepcopy(startnet)
			net.maxDist = maxDist
			dists = run(vectors, changefinders, net)
			#anomalystarti = get_start_step(planlengths, anomalystart) + 50
			#anomalyendi = get_start_step(planlengths, anomalyend) + 50
			distrs = correctness_distribution_complex(get_gng_bool_vector_complex(dists, net, plans, max))
			for actualintensity, hmft in distrs.items():
				res1.add("gng", actualintensity, hmft)
				res2.add("gng", intensity, hmft)
			distrs = correctness_distribution_complex(get_adist_bool_vector_complex_new(dists, epsilons, plans))
			for actualintensity, hmft in distrs.items():
				res1.add(str(epsilons), actualintensity, hmft)
				res2.add(str(epsilons), intensity, hmft)
			for epsilon in [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]:
				distrs = correctness_distribution_complex(get_adist_bool_vector_complex(dists, epsilon, plans))
				for actualintensity, hmft in distrs.items():
					res1.add(epsilon, actualintensity, hmft)
					res2.add(epsilon, intensity, hmft)
	res1.save_results("./actual_", name)
	res2.save_results("./projected_", name)
	print "average stream length", 1.0 * sum(lengths) / len(lengths)

def ordered_nodes(nodes):
	zeros = [0 for i in range(len(nodes[0].location))]
	return sorted(nodes, key = lambda x: -gng.distance(x.location, zeros))

def get_nodes_in_anomaly(difsfile, anomalystart, anomalyend):
	normal, anomalous = get_difs(difsfile, anomalystart, anomalyend)
	vectors, planlengths = create_random_trial(normal, anomalous, 1, 200)
	changefinders = init_ADist(vectors)
	net = init_gng(vectors)
	dists = run(vectors, changefinders, net)
	anomalystarti = get_start_step(planlengths, 200)
	anomalyendi = get_start_step(planlengths, 250) + 100
	nodeindices = []
	orderedNodes = ordered_nodes(net.nodes)
	for step in range(anomalystarti, anomalyendi):
		node = net.closest_node(dists[step])[0]
		nodeindices.append(orderedNodes.index(node))
	return nodeindices, orderedNodes
	
basedir = "./"

if __name__ == "__main__":
	
	write_norm_and_anomalous_test_set("paper_airplane", 100, 10, 20, basedir, ["unload-airplane", "load-airplane"])
	sys.exit()
	#write_norm_and_anomalous_test_set("paper_truck", 500, 100, 200, basedir, ["unload-truck"])
	#sys.exit()
	
	#write_norm_and_2_anomalous_test_set("test_2_pred_", 500, (100, 100), (150, 400), basedir, [["unload-airplane"], ["unload-truck"]])
	#sys.exit()
	
	#run_trials_new_2_anoms_gng(vectordir + "test_2_pred_", (150, 400), (100, 100), numtrials = 2, name = "2test")
	
	#sys.exit()
	
	#run_gng_trials_calc_eps(vectordir + "paper_airplane", 200, 300, numtrials = 50, name = "plane_10", maxDist = 1.0, realintensity = False)
	#run_gng_trials_calc_eps(vectordir + "paper_truck", 200, 300, numtrials = 50, name = "truck_10", maxDist = 1.0, realintensity = False)
	
	#sys.exit()
	
	one, two, nodes = get_nodes_in_2_anomalies(vectordir + "test_2_pred_", (150, 400), (100, 100), maxDist = 0.1)
	
	print one, "\n", two, "\n"
	print len(one), len(two)
	nodestr = ""
	for node in nodes:
		nodestr += str(node.location[0]) + "\t" + str(node.location[1]) + "\t" + str(node.location[2]) + "\n"
	
	f = open("these_results", "w")
	s = "unload airplane"
	for val in one:
		s += "\t" + str(len(nodes) - val)
	s += "\nunload truck"
	for val in two:
		s += "\t" + str(len(nodes) - val)
	f.write(s)
	f.write("\n" + nodestr)
	f.close()
	
	sys.exit()
	
	run_gng_trials(vectordir + "test2_", 300, 400, numtrials = 1, name = "Trial", gngdevs = 3.2)
	sys.exit()
	
	'''
	normal, anomalous = get_difs(vectordir + "test2_", 300, 400)
	vectors, planlengths = create_random_trial(normal, [], 1, 0)
	#vectors, planlengths = create_random_trial(normal, anomalous, 1, 200)
	
	net = init_gng([])
	cfs = init_ADist(vectors)
	dists = run(vectors, cfs)
	net.calibrate(dists, numtests = 50)'''
	
	maxs = []	
	for maxdist in [0.1]:
		maxs.append(run_trials_new(vectordir + "test2_", 300, 400, 20, "test"))
	sys.exit()

# color: '\033[94m' + str(round(val, 2)) + '\033[0m'