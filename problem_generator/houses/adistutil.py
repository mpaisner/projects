import simulator, generator, planner, time, adist
from adist import WindowPair, ChangeFinder, ADistance, Interval

preds = ['at', 'complete', 'has-brick-walls', 'has-foundation', 'has-roof', 'has-wood-walls', 'hoses-loaded', 'on-fire', 'unused']

def pred_count(world):
	preds = {}
	for conjunct in world.get_state_conjuncts():
		if conjunct[0] in preds:
			preds[conjunct[0]] += 1
		else:
			preds[conjunct[0]] = 1
	return preds

#creates alphabetical vector of predicate counts.
def pred_vector(world):
	count = pred_count(world)
	sortedlist = []
	for pred in preds:
		if pred in count:
			sortedlist.append(count[pred])
		else:
			sortedlist.append(0)
	return sortedlist

#creates a plan and generates state vectors at each step for given world.
#may throw errors if unplannable world states are passed in.
#Note that this method changes the world that is passed in; create a copy if it is going to be reused.
def gen_plan_vectors(world):
	plan = planner.gen_plan(world)
	vectors = []
	for i in range(len(plan)):
		vectors.append(pred_vector(world))
		world.execute_action(plan[i])
	vectors.append(pred_vector(world))
	return vectors

defaults = {"minhouses": 6, "maxhouses": 10, "mingoals": 4, "maxgoals": 8, "numworkers": 4, "averagematerials": 3}

def gen_problems_no_fire(num):
	return generator.gen_problems(num, defaults["minhouses"], defaults["maxhouses"], defaults["mingoals"], defaults["maxgoals"], defaults["numworkers"], defaults["averagematerials"], False, True, True)

def gen_problems_fire(num):
	return generator.gen_problems(num, defaults["minhouses"], defaults["maxhouses"], defaults["mingoals"], defaults["maxgoals"], defaults["numworkers"], defaults["averagematerials"], True, True, True)

#will modify problems; use copy if original is needed
def to_dif_streams(problems):
	streams = []
	for pred in preds:
		streams.append([])
	for problem in problems:
		vectors = gen_plan_vectors(problem)
		for i in range(len(vectors) - 1):
			for pred in range(len(preds)): 
				streams[pred].append(vectors[i + 1][pred] - vectors[i][pred])
	return streams

def a_dist_values(problems):
	streams = to_dif_streams(problems)
	distances = []
	for pred in range(len(preds)):
		distances.append([])
		wp = adist.WindowPair.WindowPair(200, 200, 0.5)
		ad = ADistance.ADistance()
		ad.add(Interval.Interval(-1, -1))
		ad.add(Interval.Interval(0, 0))
		ad.add(Interval.Interval(1, 1))
		cf = ChangeFinder.ChangeFinder(ad)
		cf.addWindowPair(wp)
		ad.init(cf)
		for val in streams[pred]:
			cf.addData(val)
			distances[-1].append(cf.getDistances()[0])
	return distances

def a_dist_from_vectors(vectors):
	streams = []
	for pred in preds:
		streams.append([])
	for vector in vectors:
		for i in range(len(vector) - 1):
			for pred in range(len(preds)): 
				streams[pred].append(vector[i + 1][pred] - vector[i][pred])
	distances = []
	for pred in range(len(preds)):
		distances.append([])
		wp = adist.WindowPair.WindowPair(200, 200, 0.5)
		ad = ADistance.ADistance()
		ad.add(Interval.Interval(-1, -1))
		ad.add(Interval.Interval(0, 0))
		ad.add(Interval.Interval(1, 1))
		cf = ChangeFinder.ChangeFinder(ad)
		cf.addWindowPair(wp)
		ad.init(cf)
		for val in streams[pred]:
			cf.addData(val)
			distances[-1].append(cf.getDistances()[0])
	return distances

#e.g. read_n_problems("./probs/p", 1, 50)
def read_n_problems(prefix, start, end):
	problems = []
	for i in range(start, end):
		f = open(prefix + str(i), "r")
		text = f.read()
		objects, state = parse_state(text)
		world = HouseWorld(objects, state)
		world.goals = parse_goals(text)
		problems.append(world)
	return problems

#if num = 15, returns the 15th plan start (not index 15 in list)
def get_plan_start(plans, num):
	val = 0
	for i in range(num - 1):
		val += len(plans[i]) - 1 #(-1) because only intra-plan difs are used
	return val

#hit on any predicate
def get_hit_count(distances, epsilon, start, end):
	hits = 0
	for i in range(start, end):
		for pred in range(len(preds)):
			if distances[pred][i] >= epsilon:
				hits += 1
				break
	return hits

def run_for_precision_recall(probs1, probs2, epsilons):
	planvectors = []
	for problem in (probs + probs2):
		planvectors.append(gen_plan_vectors(problem))
	adist = a_dist_from_vectors(planvectors)
	precision = []
	recall = []
	for epsilon in epsilons:
		tp = get_hit_count(adist, epsilon, get_plan_start(planvectors, len(probs1)), len(adist[0]))
		fp = get_hit_count(adist, epsilon, 0, get_plan_start(planvectors, len(probs1)))
		precision.append(1.0 * tp / (tp + fp))
		recall.append(1.0 * tp / (len(adist[0]) - get_plan_start(planvectors, len(probs1))))
	return precision, recall
			
	

if __name__ == "__main__":
	probs = gen_problems_no_fire(1000)
	probs2 = gen_problems_fire(1000)
	epsilons = [0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]

	t0 = time.clock()
	precision, recall = run_for_precision_recall(probs, probs2, epsilons)
	t1 = time.clock()
	print t1 - t0
	for epsilon in range(len(epsilons)):
		print str(epsilons[epsilon]) + "\t" + str(precision[epsilon]) + "\t" + str(recall[epsilon])

	#print probs[0].get_prob_str("p1")