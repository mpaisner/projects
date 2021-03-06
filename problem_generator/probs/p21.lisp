(setf (current-problem) 
	(create-problem
		(name p21)
		 (objects
			(rmA rmB ROOM)
			(boxA boxB boxC BOX)
			(drA DOOR)
			(keyA KEY)
)
		(state
			(and
				(pushable boxA)
				(inroom boxA rmB)
				(pushable boxB)
				(inroom boxB rmB)
				(pushable boxC)
				(inroom boxC rmB)
				(dr-to-rm drA rmA)
				(dr-to-rm drA rmB)
				(connects drA rmA rmB)
				(connects drA rmB rmA)
				(locked drA)
				(dr-closed drA)
				(is-key keyA drA)
				(carriable keyA)
				(inroom keyA rmA)
				(inroom robot rmA)
				(arm-empty)
))
		(goal
			(and
				(inroom boxA rmB)
))))