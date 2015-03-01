import main, sys, random
sys.path.append("../")
from problem_generator.logistics import planner2 as planner, simulator, generator

defEpsilons = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65]
defIntensities = [i * 0.1 for i in range(11)]
defGoalTypes = ["inside-truck", "at-obj", "inside-airplane", "at-truck", "at-airplane"]

def run_trial(num, numplans, anomalystart, anomalyend, intensity, res, missingops = [], windowsize = 100, epsilons = defEpsilons, goaltypes = defGoalTypes):
	gen = generator.LogisticsWorldGen()
	numcities = 6
	numplanes = 4
	numpackages = 6
	world = gen.random_world(numcities, numplanes, numpackages)	
	
	difs = []
	i = 0
	while i < anomalystart and i < numplans:
		gen.add_random_goals(3, goaltypes, world)
		plan = main.gen_plan(world)
		if plan:
			difs.append(main.dif_vectors(world, plan[1]))
			i += 1			
		world.goals = []
		if i % 20 == 0:
			print str(i) + " plans completed, anomaly ends " + str(anomalyend)
	anomalyattempts = 0
	while i < anomalyend and i < numplans:
		gen.add_random_goals(3, goaltypes, world)
		if random.random() < intensity:
			plan = main.gen_plan(world, missingops)
			currentattempts = 1
			while not plan:
				world.goals = []
				gen.add_random_goals(3, goaltypes, world)
				plan = main.gen_plan(world, missingops)
				currentattempts += 1
				if currentattempts % 50 == 0:
					print "anomaly planning attempts", currentattempts
					if currentattempts > 300: #restart if plan gen is failing.
						print world.readable_str()
						run_trial(num, numplans, anomalystart, anomalyend, intensity, res, missingops, windowsize, epsilons, goaltypes)
		else:
			plan = main.gen_plan(world)
		if plan:
			difs.append(main.dif_vectors(world, plan[1]))
			i += 1			
		world.goals = []
		if i % 20 == 0:
			print str(i) + " plans completed"
	while i < numplans:
		gen.add_random_goals(4, goaltypes, world)
		plan = main.gen_plan(world)
		if plan:
			difs.append(main.dif_vectors(world, plan[1]))
			i += 1			
		world.goals = []
		if i % 20 == 0:
			print str(i) + " plans completed"
	main.write_vectors(difs, "difvects" + str(num))
	
	normal, anomalous = main.get_difs("difvects" + str(num), anomalystart, anomalyend)
	planlengths = []
	vectors = []
	for plan in difs:
		planlengths.append(len(plan))
		vectors += plan
	changefinders = main.init_ADist(vectors)
	dists = main.run(vectors, changefinders)
	
	anomalystarti = main.get_start_step(planlengths, anomalystart) #+ 50
	anomalyendi = main.get_start_step(planlengths, anomalyend) #+ 50
	for epsilon in epsilons:
		if intensity > 0:
			res.add(epsilon, intensity, main.correctness_distribution(main.get_adist_bool_vector(dists, epsilon), anomalystarti, anomalyendi))
		else: #no anomaly
			res.add(epsilon, intensity, main.correctness_distribution(main.get_adist_bool_vector(dists, epsilon), anomalystarti, anomalystarti))

def run_trials(num, numplans, anomalystart, anomalyend, missingops = ["unload-airplane"], windowsize = 100, epsilons = defEpsilons, intensities = defIntensities, goaltypes = defGoalTypes):
	res = main.Result()
	for i in range(num):
		for intensity in intensities:
			run_trial(i, numplans, anomalystart, anomalyend, intensity, res, missingops = missingops)
	res.save_results("./", "all_res_plane")
	

if __name__ == "__main__":
	run_trials(5, 500, 100, 200)