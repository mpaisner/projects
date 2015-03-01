import math

class Person:
	
	def __init__(self):
		self.age = 0.0
	
#k is a contant, n is an exponent	
def death_chance(age, dt, le, k, n):
	return math.exp((age - le) * n) * k * dt

def death_chance_2(age, dt, k, n):
	return n ** age * k * dt

import random
def possibly_die(person, dt, le, k, n):
	return death_chance_2(person.age, dt, k, n) > random.random()

living = set()
dead = set()

def age(dt, le, k, n):
	newlydead = set()
	for person in living:
		person.age += dt
		if possibly_die(person, dt, le, k, n):
			newlydead.add(person)
			dead.add(person)
	for person in newlydead:
		living.remove(person)

def mean_age(s):
	try:
		return sum([person.age for person in s]) / len(s)
	except ZeroDivisionError:
		return 0

def num_at_age(age, s):
	return len([person for person in s if abs(person.age - age) < 0.5])

#test1
le = 80
k = 0.0003
n = 1.1

for i in range(2000):
	age(0.1, le, k, n)
	for p in range(10):
		living.add(Person())
	if i % 20 == 0:
		print "year", i * 0.1, "- living: ", len(living), "|", mean_age(living), " ; ", "- dead: ", len(dead), "|", mean_age(dead)
print max([person.age for person in living]), max([person.age for person in dead]), min([person.age for person in living]), min([person.age for person in dead])

for age in range(100):
	print age, num_at_age(age, living)