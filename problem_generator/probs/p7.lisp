(setf (current-problem) 
	(create-problem
		(name p7)
		 (objects
			(rmA rmB ROOM)
			(boxA boxB boxC BOX)
			(drA DOOR)
			(keyA KEY)
)
		(state
			(and
				(carriable boxA)
				(inroom boxA rmA)
				(carriable boxB)
				(inroom boxB rmB)
				(pushable boxC)
				(inroom boxC rmA)
				(dr-to-rm drA rmA)
				(dr-to-rm drA rmB)
				(connects drA rmA rmB)
				(connects drA rmB rmA)
				(unlocked drA)
				(dr-closed drA)
				(is-key keyA drA)
				(carriable keyA)
				(inroom keyA rmB)
				(inroom robot rmA)
				(arm-empty)
))
		(goal
			(and
				(unlocked drA)
))))