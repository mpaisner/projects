(setf (current-problem)
	(create-problem
		(name p4)
			(objects
				(h2 h3 h1 h4 h5 HOUSE)
				(w3 CONSTRUCTION-WORKER)
				(w4 w1 FIREMAN)
				(w2 TEAMSTER)
				(m4 m6 m1 m9 CONCRETE)
				(m7 WOOD)
				(m10 m5 m2 BRICK)
				(m3 m8 SHINGLE)
			)
			(state
				(and
					(has-foundation h2)
					(at m10 h1)
					(unused m10)
					(at m5 h3)
					(unused m5)
					(at m4 h3)
					(unused m4)
					(at m7 h5)
					(unused m7)
					(at m6 hq)
					(unused m6)
					(at m1 h3)
					(unused m1)
					(at m3 h5)
					(unused m3)
					(at m2 h5)
					(unused m2)
					(at m9 h4)
					(unused m9)
					(at m8 h5)
					(unused m8)
					(at w4 h5)
					(at w3 h4)
					(at w2 h2)
					(at w1 h3)
				)
			)
			(goal
				(and
					(complete h5)
					(has-brick-walls h1)
					(has-roof h3)
					(has-foundation h4)
					(has-brick-walls h2)
				)
			)
	)
)