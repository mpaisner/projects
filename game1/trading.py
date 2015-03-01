class Learner:
	
	def __init__(self, num, skill, potential):
		self.agerange = 30
		self.num = num
		self.skill = skill
		self.potential = potential

	def update(self, num, skill, dtime):
		self.skill += self.potential * 1.0 / self.agerange * dtime
		self.potential *= (1 - 1.0 / self.agerange * dtime)
		self.num -= int(self.num * float(1) / self.agerange)
		self.potential *= 1 - 1.0 / self.agerange * dtime  
		self.potential += float(num) / self.num * (skill - self.skill)
		self.num += num

'''		
l = Learner(1000, 40.0, 0.0)
for i in range(15):
	l.update(35, 45, 1.0)
	#print l.num, l.skill, l.potential
for i in range(15):
	l.update(35, 45, 1.0)
	#print l.num, l.skill, l.potential
for i in range(15):
	l.update(35, 45, 1.0)
	print l.num, l.skill, l.potential
'''
'''
Example:

Province(2 squares):
	
	Square 1:
		dominant terrain = "flood plains"
		Farmland(20.4 units, value = fFarm1(unit), devcost = fFramcost1())
		Pasture(8.4 units, value = fPasture1(unit), devcost = ...)
		Fresh Water(10.2 units, devcost = fWaterCost1()
		...
	...
	

Resource Trading:

	1) All resource sources are calculated. Each has a quantity and quality.
	2) Transport costs between all sources and destinations are calculated.
	3) Each territory bids a price for each good it demands. The price is the price last cycle, increased or decreased depending on whether there was a shortage or surplus last cycle (and the quantity thereof).
	4) Each source allocates its goods based on profit.
	5) repeat.

'''

import heapq, random
from ztable import *
	
class Path:
	
	def __init__(self, stops, cost):
		self.stops = stops
		self.cost = cost
	
	def extend(self, dest, cost):
		return Path(self.stops + [dest], self.cost + cost)
	
	def __len__(self):
		if self.cost != float("inf"):
			return len(self.stops)
		return self.cost

class TransportCosts:
	
	def __init__(self, territories, knowncosts):
		self.territories = set(territories)
		for start in knowncosts:
			for dest in knowncosts[start]:
				knowncosts[start][dest] = Path([start, dest], knowncosts[start][dest])
		self.allpaths = self.dijkstra(territories, knowncosts)
	
	def dijkstra(self, territories, knowncosts):
		allpaths = {}
		for territory in territories:
			paths = {}
			open = [(0, Path([territory], 0))]
			while open and len(paths) < len(territories):
				cost, nextpath = heapq.heappop(open)
				terr = nextpath.stops[-1]
				if terr in paths:
					continue
				paths[terr] = nextpath
				for dest, path in knowncosts[terr].items():
					newpath = nextpath.extend(dest, path.cost)
					heapq.heappush(open, (newpath.cost, newpath))
			for terr in territories:
				if terr not in paths:
					infpath = Path([territory], 0)
					paths[terr] = infpath.extend(terr, float("inf"))
			allpaths[territory] = paths
		return allpaths
	
	def cost(self, source, dest):
		return self.allpaths[source][dest].cost
	
	def route(self, source, dest):
		return self.allpaths[source][dest].stops
	
	#rather than counting only direct paths, for efficiency, might keep old paths under certain conditions.
	def direct_paths(self):
		allpaths = {}
		for start in self.territories:
			allpaths[start] = {}
			for dest in self.territories:
				if len(self.allpaths[start][dest]) == 2:
					allpaths[start][dest] = self.allpaths[start][dest]
		return allpaths
	
	#maybe make more efficient later
	def update(self, newcosts):
		for start in newcosts:
			for dest in newcosts[start]:
				newcosts[start][dest] = Path([start, dest], newcosts[start][dest])
		costs = self.direct_paths()
		for start in newcosts:
			costs[start].update(newcosts[start])
		self.allpaths = self.dijkstra(territories, costs)

'''
Industry fields:
	1) Inputs: (Resource, Number) - all inputs must be present
	2) Outputs: (Resource, Number) - all outputs will be produced
	3) Labor: (Number, Skill) - Skill is the relevant skill category. Relevant specialization will be task-specific.
	Note: All values will generally be normalized for one unit of primary output.
'''

class Resource:
	
	def __init__(self, name, transportcost, startprice):
		self.name = name
		self.transportcost = transportcost
		self.startprice = startprice
	
	def __str__(self):
		return self.name



class Skill:
	
	def __init__(self, name, id, learningfunc, agingfunc, percentvariance):
		self.name = name
		self.id = id #used for replacement
		self.learningfunc = learningfunc
		self.agingfunc = agingfunc
		self.percentvariance = percentvariance
	
	def apply_learning(self, oldskill, employpercent, dtime):
		return self.learningfunc(oldskill, employpercent, dtime)
	
	def apply_aging(self, oldskill, age, dtime):
		return self.agingfunc(oldskill, age + dtime / 2, dtime)

class BuildingType:
	
	def __init__(self, name):
		self.name = name
		self.allowedtasks = {}
	
	def add_task(self, task):
		self.allowedtasks[task.id] = task
	
	def update_task(self, task):
		if task.id in self.allowedtasks:
			self.allowedtasks[task.id] = task
		else:
			raise IndexError("No task with id " + task.id + " allowed by building type " + self.name + ". Use add_task() to add a new one.")
	
	def update_construction_task(self, task):
		self.constructiontask = task

def gen_simple_func(resourceweight, exponent):
	return lambda resquality, laborskill: (resquality * resourceweight + laborskill * (1 - resourceweight)) ** exponent

#normally, resource quality does not effect output quantity. Skill has an effect proportional to its square root.
def NORMAL_EFF_FUNC():
	return gen_simple_func(0, 0.5)

#specific skill matters more for quality. Resource quality matters a lot more.
def NORMAL_QUAL_FUNC():
	return gen_simple_func(0.55, 0.5)
	

'''
TENT = BuildingType("tent")
OUTDOORSMAN_SKILL = Skill("Outdoorsman")
SETUP_TENT = IndustryTask("setup tent", "cheap no resource housing construct", [], [Output(TENT, 1.0)], LaborCost(OUTDOORSMAN_SKILL, 0.1), 
NORMAL_EFF_FUNC(), NORMAL_QUAL_FUNC())

WOOD = Resource("wood", 2.5)
LOG_CABIN = BuildingType("log cabin")
BUILD_CABIN = IndustryTask("build log cabin", "cheap wood housing construct", [Input(WOOD, 5.0)], [Output(LOG_CABIN, 1.0)], LaborCost(OUTDOORSMAN_SKILL, 0.8), NORMAL_EFF_FUNC(), NORMAL_QUAL_FUNC())

CUT_WOOD = IndustryTask("fishing", "fishing", [], [Output(WOOD, 1.0)], LaborCost(OUTDOORSMAN_SKILL, 0.7), NORMAL_EFF_FUNC(), NORMAL_QUAL_FUNC())

FISH = Resource("fish", 1.0)
GO_FISHING = IndustryTask("fishing", "fishing", [], [Output(FISH, 1.0)], LaborCost(OUTDOORSMAN_SKILL, 0.5), NORMAL_EFF_FUNC(), NORMAL_QUAL_FUNC())

'''


class SkillProfile:
	
	def __init__(self, numworkers, skill, mean):
		self.num = numworkers
		self.skill = skill
		self.mean = mean
	
	def __str__(self):
		return str(self.num) + " people with skill " + str(round(self.mean, 1)) + " at " + self.skill.name
	
	def copy(self):
		return SkillProfile(self.num, self.skill, self.mean)
	
	def change_skill(self, skill):
		self.mean *= .67
		self.skill = skill
	
	def add_workers(self, prof):
		if prof.skill != self.skill:
			prof.change_skill(self.skill)
		total = self.num + prof.num
		if total > 0:
			self.mean = (self.mean * self.num + prof.mean * prof.num) / total
		else:
			self.mean = 0
		self.num = total
	
	def remove_workers(self, prof):
		self.num -= prof.num
	
	def fraction(self, fraction):
		return SkillProfile(int(round(self.num * fraction)), self.skill, self.mean)
	
	def variance(self):
		return self.mean * self.skill.percentvariance
	
	def val_to_fraction_in_tail(self, val):
		sd = self.variance() ** 0.5
		z = abs(val - self.mean) / sd
		return z_to_fraction(z)
	
	def num_in_interval(self, start, end):
		if start > end:
			raise ValueError("start of interval must be <= end")
		if start < self.mean and end < self.mean:
			fraction = self.val_to_fraction_in_tail(end) - self.val_to_fraction_in_tail(start)
		elif start < self.mean and end >= self.mean:
			fraction = 1 - self.val_to_fraction_in_tail(start) - self.val_to_fraction_in_tail(end)
		else: #both are >= mean
			fraction = self.val_to_fraction_in_tail(start) - self.val_to_fraction_in_tail(end)
		return fraction * self.num
	
	def distribution(self, numtiers = 100):
		total = 0
		dist = []
		for i in range(numtiers):
			dist.append(int(round(self.num_in_interval(i, i + 1), 0)))
			total += dist[-1]
		unassigned = self.num - total
		while unassigned != 0:
			i = int(round(random.gauss(self.mean, self.variance())))
			if unassigned > 0:
				dist[i] += 1
				unassigned -= 1
			elif dist[i] > 0:
				dist[i] -= 1
				unassigned += 1
		return dist

archery = Skill("hunting", "hunting", lambda oldskl, employper, dtime: oldskl + 0.5 * employper * dtime, lambda oldskl, age, dtime: oldskl - max(0, (age - 30) / 300), 0.3)
sp = SkillProfile(50, archery, 45)

'''
Order:
1) Price adjustment
2) Salary adjustment
3) Worker Movement
	-Workers bid on jobs just like industries bid on goods.
	-A certain percentage (with a minimum total number) of workers in each industry have flexibility to leave (per time). These are the bidders. The percentage is determined in part by salary decreases.
4) Production (construction does not take effect until next update)
5) Apply transport costs, generate list of sellers for each good for each market. Cutoff at some price point (modified by quality) to reduce size of list.
6) 
'''

class ValueMem:
	
	memT = 10.0
	maxDif = 1.0
	
	def __init__(self):
		self.knownvalues = [] #[quality, value, dVdQ, tLearned]
	
	def update(self, quality, value, dVdQ, t):
		self.knownvalues = [(oldquality, oldvalue, olddVdQ, tLearned) for oldquality, oldvalue, olddVdQ, tLearned in self.knownvalues if t - tLearned < self.memT and abs(quality - oldquality) > self.maxDif]
		self.knownvalues.append((quality, value, dVdQ, t))
	
	def estimate_dValue(self, quality):
		for knownquality, value, dVdQ, dt in self.knownvalues:
			if abs(quality - knownquality) < self.maxDif:
				return value + (quality - knownquality) * dVdQ
		return None

#qualfunc and quantfunc should be functions of resource quality
def resource_values(qualfunc, quantfunc, percentofproduct, productprice):
	pass

#resourceValues must be calculated based on quality and local factors. When constructing spaceships, any low-quality material may have value 0, whereas for chairs, quality may only have a marginal impact except at very low or high values.
#returns top numbids {Stockpile: spreadfunc(percent of total value)}
#first 2 inputs are dicts{Stockpile: value}
def calculate_bids(resourceValues, resourceCosts, numbids, spreadfunc):
	offerqualities = {float(spreadfunc(resourceValues[stockpile] - resourceCosts[stockpile])): stockpile for stockpile in resourceValues if resourceValues[stockpile] >= resourceCosts[stockpile]}
	topN = sorted(offerqualities.keys())[-numbids:]
	total = sum(topN)
	return {offerqualities[quality]: quality / total for quality in topN}
	
coal1 = Stockpile(Resource("Coal", 1), 55, 102)	
coal2 = Stockpile(Resource("Coal", 1), 40, 300)
vals = {coal1: 85, coal2: 60}
costs = {coal1: 70, coal2: 41}
print calculate_bids(vals, costs, 2, lambda x: x ** 2)

sys

#will raise an exception if any item is in the weightdict and not the valdict
def weighted_sum(weightdict, valdict, normalize = False):
	total = 0
	for item, weight in weightdict.items():
		total += weight * valdict[item]
	if normalize:
		total /= sum([weight for weight in weightdict.values()])
	return total

#dprofit / dworkers = weightedsum(productprices) * dProductivitydW / (salary + weightedsum(resourceprices) * dProductivitydW)
def d_profit_d_worker(productquantitites, productprices, productivityfunc, salary, resourcequantities, resourceprices, numworkers):
	dProductivitydW = productivityfunc(numworkers + 1) - productivityfunc(numworkers)
	dRevenuedW = weighted_sum(productquantities, productprices) * dProductivitydW
	dCostdW = weighted_sum(resourcequantities, resourceprices) * dProductivitydW + salary
	return dRevenuedW - dCostdW
	

#signed value signifying whether more goods are demanded than available (positive) or vice versa (negative). Will have value -1 <= v <= 1.
def demand(numbidlast, stockpile, productionlast):
	return (numbidlast - stockpile - productionlast) / (numbidlast + stockpile + productionlast)

#dproductprice / time = price * pricestabilityconstant * ((product bid on last turn - (stockpile + production last turn)) / (product bid on last turn + stockpile + production last turn)
def natural_d_product_price(oldprice, demand, dt, pricestability):
	dPdT = pricestability * oldprice * demand
	return dPdT * dt

#dsalary / dt = employment flexibility constant * dprofit/dworkers * demand -> [salary adjustment is proportional to profit per worker and does not include old salary, since the actual calculation both multiplies and divides by it. Demand also effects salary adjustments, since an industry with room for growth is willing to pay more.]
#weight of profit vs. demand may need to be adjusted.
def natural_d_salary(oldsalary, dProfitdWorker, dt, salarychangeconst):
	dSdT = salarychangeconst * (dProfitdWorker + demand * oldsalary)
	return dSdT * dt


class BusinessMem:
	
	memlearnrate = 20
	
	def __init__(self, resourceprices, productprices, salarymultiplier):
		self.turns = 0
				
		self.lastusage = 10.0 #usage capped at, say 10.0
		
		self.resourceprices = resourceprices
		self.resourcesoffered = {resource: 1.0 for resource in resourceprices} #fraction (can be > 1) of needed resources that were offered by sellers.
		
		self.lastprices = resourceprices
		self.productprices = productprices
		self.lastsalary = salarymultiplier

class BusinessProfile:
	'''
	1) Raise salaries if: (profits up) and (capacity left)
	   Lower salaries if: (over capacity) or (prices drop)
	   Raise/lower resource bids depending on needs of workforce
	   Invest in infrastructure if at capacity
	   Eliminate infrastructure if it is unused for period x
	'''
	def __init__(self, industrytask, skillprofile, building):
		self.task = industrytask
		self.workerprofile = skillprofile
		self.buildings = {building: 0.0} #partial buildings may not be used, but may be completed over several turns
	
	def update(self):
		pass

'''
assumptions: 
	1) All pop inside a segment is evenly distributed, so that each year, 1/len(range) graduates to the next segment [minus deaths]
	2) All demographic effects apply equally to all members of a segment, so 82 and 84-years-olds have identical death rates.
	3) Each time step, graduates from lower segment(s) are added and graduations subtracted for all segments, then aging/training effects are applied and births added.
'''

class PopSegment:
	
	#agemin is inclusive, agemax is not.
	def __init__(self, agemin, agemax):
		self.range = (agemin, agemax)
		self.workerprofiles = {}
	
	def copy(self):
		cpy = PopSegment(self.range[0], self.range[1])
		for prof in self.workerprofiles.values():
			cpy.add_profile(prof)
		return cpy
	
	def __len__(self):
		return self.range[1] - self.range[0] + 1
	
	def add_profile(self, profile):
		if profile.skill not in self.workerprofiles:
			self.workerprofiles[profile.skill] = profile
	
	def add_skill(self, skill):
		self.add_profile(SkillProfile(0, skill, 0.0))
	
	#throws KeyError if segment does not possess skill1
	def move_workers(self, skill1, skill2, shifttype, num):
		prof1 = self.workerprofiles[skill1]
		try:
			prof2 = self.workerprofiles[skill2]
		except KeyError:
			self.add_skill(skill2)
			prof2 = self.workerprofiles[skill2]
		if shifttype == "worst":
			workers = prof1.get_worst_workers(num)
		elif shifttype == "average":
			workers = prof1.workers_with_mean(num, prof1.mean)
		elif shifttype == "best":
			workers = prof1.get_best_workers(num)
			print workers.mean, workers.num
		if prof1.can_remove(workers):
			prof1.remove_workers(workers)
			prof2.add_workers(workers)

def test_pop_seg():
	seg = PopSegment(20, 25)
	archery = Skill("archery")
	fishing = Skill("fishing")
	archeryprof = SkillProfile(2300, archery, 18.0, 6.0)
	fishingprof = SkillProfile(5000, fishing, 14.0, 3.0)
	seg.add_profile(archeryprof)
	seg.add_profile(fishingprof)
	seg.move_workers(archery, fishing, "best", 2000)
	for prof in seg.workerprofiles.values():
		print prof

#test_pop_seg()

class Population:
	
	def __init__(self, segmentrange, numsegments):
		self.segments = [PopSegment(i * segmentrange, (i + 1) * segmentrange - 1) for i in range(numsegments)]
	
	def copy(self):
		cpy = Population(1, 1)
		cpy.segments = [seg.copy() for seg in self.segments]
		return cpy
	
	def graduate(self, yearfraction):
		for i in range(len(self.segments) - 1):
			i = len(self.segments) - i - 2
			source = self.segments[i]
			dest = self.segments[i + 1]
			for skill, profile in source.workerprofiles.items():
				workers = profile.fraction(float(yearfraction / len(source)))
				if skill not in dest.workerprofiles:
					dest.add_skill(skill)
				profile.remove_workers(workers)
				dest.workerprofiles[skill].add_workers(workers)
	
	

def test_pop():
	pop = Population(5, 5)
	pop.segments[0].add_profile(SkillProfile(2300, archery, 22.0))
	for i in range(20):
		print i
		for seg in pop.segments:
			try:
				print seg.workerprofiles[archery]
			except:
				print None
		pop.graduate(0.4)
test_pop()
sys

class Territory:
	
	def __init__(self, loc, popstart):
		self.loc = loc
		self.population = popstart.copy()
	
	def add_industry(self, industry):
		pass

	
if __name__ == "__main__":
	import random	
	territories = [(x, y) for x in range(10) for y in range(10)]
	costs = {}
	for territory in territories:
		costs[territory] = {}
		for other in territories:
			if 0 < abs(territory[0] - other[0]) + abs(territory[1] - other[1]) < 2 and random.random() < 1:
				costs[territory][other] = random.random() * 5
	t = TransportCosts(territories, costs)
	for territory in territories:
		print territory, t.cost((4, 4), territory)
	t.update({(4, 4): {(4, 3): t.cost((4, 4), (4, 3)) - 0.5}})
	for territory in territories:
		print territory, t.cost((4, 4), territory), len(t.route((4, 4), territory))

	
