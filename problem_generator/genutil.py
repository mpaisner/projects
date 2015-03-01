import pygame, sys 
from strippsgen import Goal
from pygame.locals import *

def file_to_state(file):
	states = []
	lines = file.readlines()
	started = False
	parencount = 0
	for line in lines:
		if started:
			foundclosed = False
			parencount += line.count("(")
			if line.count(")") > 0:
				parencount -= line.count(")")
				foundclosed = True
			if parencount == 2 and foundclosed:
				line = line[line.index("(") + 1 : line.index(")")]
				piece = line.split(" ")
				if len(piece) == 1:
					states[-1].append(Goal(piece[0]))
				elif len(piece) == 2:
					states[-1].append(Goal(piece[0], piece[1]))
				elif len(piece) == 3:
					states[-1].append(Goal(piece[0], piece[1], piece[2]))
				elif len(piece) == 1:
					states[-1].append(Goal(piece[0], piece[1], piece[2], piece[3]))
			elif parencount == 0:
				started = False
		elif "state" in line:
			started = True
			parencount = 1
			states.append([])
	return states

def show_stripps(state):
	pass

f = open("./probs/p2.lisp", 'r')
for goal in file_to_state(f)[0]:
	s = goal.predicate + "("
	if goal.obj1:
		s += goal.obj1 + " "
	if goal.obj2:
		s += goal.obj2 + " "
	if goal.obj3:
		s += goal.obj3 + " "
	s += ")"
	print s
