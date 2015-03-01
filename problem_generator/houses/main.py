import simulator, generator, planner, adistutil, copy

if __name__ == "__main__":
	generator.write_simple_problems("./probs", 1000)
	
	for i in range(1, 1000):
		f = open("./probs/p" + str(i) + ".lisp", "r")
		text = f.read()
		f.close()
		objects, state = simulator.parse_state(text)
		pworld = simulator.HouseWorld(objects, state)
		sworld = simulator.HouseWorld(objects, state)
		pworld.goals = simulator.parse_goals(text)
		generator.add_goals_from_state(sworld, 1)
		plan = planner.gen_plan(pworld)
		#print planner.prodigy_str(plan)
		step = 0
		while plan:
			f = open("./probs/plan_" + str(i) + "_step_" + str(step), "w")
			f.write(sworld.get_prob_str("p" + str(i) + "-" + str(step)))
			f.close()
			sworld.execute_action(plan.pop(0))
			sworld.goals = []
			generator.add_goals_from_state(sworld, 1)
			step += 1
		f = open("./probs/plan_" + str(i) + "_step_" + str(step), "w")
		f.write(sworld.get_prob_str("p" + str(i) + "-" + str(step)))
		f.close()
		
	
		