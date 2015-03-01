'''
1) Each business has n types of worker skills it needs, each with a given number per output.
2) They send out offers to each group of workers seeking employment in each skill they need. Offers are based on those workers' projected skill in the offering business.
3) Workers, using the same mechanics as buying/selling, choose from the offers. If no offer exceeds a certain minimum, they stay unemployed.
4) Workers come from two sources:
	A) New entrants to the work force (i.e. education grads)
	B) A certain percentage of workers from each business who seek new employment each cycle.
		-possibly, industries whose quality of work is declining should release a higher percentage.

'''

class TransferGroup:
	'''used only for tranfer between skill segments'''	
	def __init__(self, age, skilltype, skill, pop):
		self.age = age
		self.skilltype = skilltype
		self.skill = skill
		self.pop = pop

class WorkerSegment:
	
	def __init__(self, range, skilltype, skill = 0, pop = 0, mean = 0.5):
		self.skilltype = skilltype
		self.skill = skill
		self.range = range
		self.pop = pop
		self.mean = mean
	
	def __len__(self):
		return self.range[1] - self.range[0]
	
	def actual_mean(self):
		return self.range[1] * self.mean + self.range[0] * (1 - self.mean)
	
	def grads(self, dt):
		try:
			spread = max(2 * (0.5 - abs(0.5 - self.mean)), 0.001)
			newmean = self.mean + dt
			numGrads = self.pop * max(0, (newmean - (1 - spread / 2)) / spread)
		except ZeroDivisionError:
			numGrads = self.pop
		age = self.range[1] + dt / 2
		return TransferGroup(age, self.skilltype, self.skill, numGrads)
	
	def add_group(self, group):
		if group.pop == 0:
			return
		assert self.range[1] >= group.age >= self.range[0]
		newpop = self.pop + group.pop
		groupmean = (float(group.age) - self.range[0]) / len(self)
		self.mean = (self.mean * self.pop + groupmean * group.pop) / newpop
		#switch skills if necessary
		self.skill = (self.skill * self.pop + group.skill * group.pop) / newpop
		self.pop = newpop
	
	def remove_group(self, group):
		if group.pop == 0:
			return
		elif group.pop == self.pop:
			self.pop = 0
			self.mean = 0.5
			return
		newpop = self.pop - group.pop
		groupmean = (float(group.age) - self.range[0]) / len(self)
		self.mean = (self.mean * self.pop - groupmean * group.pop) / newpop
		self.skill = (self.skill * self.pop - group.skill * group.pop) / newpop
		self.pop = newpop
	
def annual_death_rate(age, leFact, k):
	return k ** age * leFact

#returns a dict of {age: death rate}, for each n years. leFactor represents an amalgam of medical tech, working conditions, etc. that determines life expectancy. K is the exponent base that determines how much age impacts death rate. n is assumed to be equal to the length of each workersegment age range.
def annual_death_rates(leFact, k, n = 3, maxage = 150):
	return {n * i: annual_death_rate(n * i, leFact, k) for i in range(maxage / n + 1)}
	
#n is the interval of death rates
def yearly_deaths(segment, deathrates):
	return (deathrates[segment.range[0]] * (1 - segment.mean) + deathrates[segment.range[1]] * segment.mean) * segment.pop
	
def advance_age(segment, dt, deathrates):
	numDeaths = yearly_deaths(segment, deathrates) * dt
	#dead += numDeaths #report deaths
	segment.pop -= numDeaths
	grads = segment.grads(dt)
	segment.pop -= grads.pop
	segment.mean += dt / 2 / len(segment)

def advance_all(segments, dt, leFact, k):
	deathrates = annual_death_rates(leFact, k)
	for segment in segments:
		advance_age(segment, dt, deathrates)
		segment.add_group(TransferGroup(0, None, 40, 3))
	
class Workforce:
	
	def __init__(self, segmentsize, agerange, skilltype):
		self.segsize = segmentsize
		self.agerange = agerange
		self.segments = []
		for i in range((agerange[1] - agerange[0]) / segmentsize):
			self.segments.append(WorkerSegment((i * segmentsize + agerange[0], (i + 1) * segmentsize + agerange[0]), skilltype))
	
	def advance_age(self, dt, deathrates):
		grads = []
		for i in range(len(self.segments)):
			segment = self.segments[i]
			numDeaths = yearly_deaths(segment, deathrates) * dt
			segment.pop -= numDeaths
			if i < len(self.segments) - 1:
				grads.append(segment.grads(dt))
				segment.remove_group(grads[-1])
		for i in range(len(self.segments)):
			segment = self.segments[i]
			segment.mean += float(dt) / len(segment)
			if i > 0:
				self.segments[i].add_group(grads[i-1])
			

leFact = 0.0003
k = 1.1
wf = Workforce(3, (18, 66), None)
deathrates = annual_death_rates(leFact, k)
while raw_input() != "q":
	for i in range(1):
		wf.segments[0].add_group(TransferGroup(18, None, 50, 40))
		wf.advance_age(0.4, deathrates)
	for segment in wf.segments:
		print segment.range, "(", segment.mean, ") :", int(segment.pop), "  ",
	
	
