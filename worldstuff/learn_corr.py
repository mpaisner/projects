import sys
sys.path.append("../")
from bored import bored

hero = bored.Hero()
hero.meleeskill = 4
hero.hitdice = [6]
hero.dmgdice = [4, 4]
hero.hp = 30

goblintype = bored.EnemyType("Goblin", 3, [5], [3], 10, bored.images["goblin"])
orctype = bored.EnemyType("Orc", 4, [8], [6], 20, bored.images["goblin"])
#name, meleeskill, hitdice, dmgdice, hp, img
goblin = bored.Enemy(goblintype)
orc = bored.Enemy(orctype)

def get_attrs(hero, enemy):
	attrs = {}
	attrs["hero.meleeskill"] = hero.meleeskill
	attrs["hero.hitdice"] = sum(hero.hitdice)
	attrs["hero.dmgdice"] = sum(hero.dmgdice)
	attrs["hero.hp"] = hero.hp
	attrs["hero.alive"] = 1 if hero.hp > 0 else 0
	attrs["enemy.meleeskill"] = enemy.type.meleeskill
	attrs["enemy.hitdice"] = sum(enemy.type.hitdice)
	attrs["enemy.dmgdice"] = sum(enemy.type.dmgdice)
	attrs["enemy.hp"] = enemy.type.hp - enemy.hplost
	attrs["enemy.alive"] = 1 if enemy.type.hp - enemy.hplost > 0 else 0
	return attrs

def get_attr_v(hero, enemy, sortedattrs):
	attrs = get_attrs(hero, enemy)
	v = []
	for attr in sortedattrs:
		if attr not in attrs:
			v.append(0)
		else:
			v.append(attrs[attr])
	return v

#with time as added attr
def get_attr_seq(hero, enemy, n):
	sortedattrs = get_attrs(hero, enemy).keys()
	sortedattrs.sort()
	seq = []
	seq.append(get_attr_v(hero, enemy, sortedattrs) + [0])
	for i in range(n):
		hero.attack([enemy])
		seq.append(get_attr_v(hero, enemy, sortedattrs) + [i + 1])
	return seq

seq1 = get_attr_seq(hero, goblin, 5)
seq2 = get_attr_seq(hero, orc, 5)

sortedattrs = get_attrs(hero, goblin).keys()
sortedattrs.sort()

from numpy import loadtxt, zeros, ones, array, linspace, logspace

def squared_error(values, coeffs, seq):
	error = 0
	for i in range(len(values)):
		predicted = coeffs[0] + sum([coeffs[var + 1] * seq[i][var] for var in range(len(seq[i]))])
		error += (predicted - values[i]) ** 2
	return error

def adjust_coeffs(values, coeffs, seq, delta):
	adjusted = False
	currentError = squared_error(values, coeffs, seq)
	oldcoeffs = list(coeffs)
	for coeff in range(len(coeffs)):
		oldcoeffs[coeff] += delta
		if squared_error(values, oldcoeffs, seq) < currentError:
			oldcoeffs[coeff] -= delta
			coeffs[coeff] += delta
			adjusted = True
			continue
		oldcoeffs[coeff] -= delta * 2
		if squared_error(values, oldcoeffs, seq) < currentError:
			oldcoeffs[coeff] += delta
			coeffs[coeff] -= delta
			adjusted = True
			continue
	return adjusted

def get_linear_func(seqs, index, delta):
	values = [[seq[i][index] for i in range(len(seq))] for seq in seqs]
	seqs = [[v[:index] + v[index:] for v in seq] for seq in seqs]
	coeffs = [0.0 for i in range(len(seqs[0][0]) + 1)]
	print sum([squared_error(values[seq], coeffs, seqs[seq]) for seq in range(len(seqs))])
	i = 0
	while i < 200:
		adjusted = False
		for seq in range(len(seqs)):
			if adjust_coeffs(values[seq], coeffs, seqs[seq], delta):
				adjusted = True
		print sum([squared_error(values[seq], coeffs, seqs[seq]) for seq in range(len(seqs))])
		print coeffs
		i += 1
		if not adjusted:
			break

get_linear_func([seq1, seq2], 3, 0.01)
print ["none"] + sortedattrs[:3] + sortedattrs[4:] + ["time"]