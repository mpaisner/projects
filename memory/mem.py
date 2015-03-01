from format import *
import numbers, datetime
from bisect import bisect

STARTTIME = datetime.datetime.today()

class TimeRange(object):
	
	def __init__(self, start, end, openstart = False, openend = False):
		if end < start:
			raise ValueError("A time range must be >= 0 in length")
		self.start = start
		self.end = end
		self.openstart = openstart
		self.openend = openend
	
	def __str__(self):
		if self.openstart:
			s = "("
		else:
			s = "["
		s += str(round(self.start, 2)) + "-"
		s += str(round(self.end, 2))
		if self.openend:
			s += ")"
		else:
			s += "]"
		return s		
	
	def __nonzero__(self):
		return self.end > self.start or (not (self.openend or self.openstart) and self.end == self.start)
	
	def __contains__(self, other):
		if isinstance(other, numbers.Number):
			if other > self.start and other < self.end:
				return True
			elif other == self.start and not self.openstart:
				return True
			elif other == self.end and not self.openend:
				return True
			else:
				return False
		elif isinstance(other, self.__class__):
			return other.start in self and other.end in self
		elif isinstance(other, RangeSet):
			return other in other.intersection(self)
		elif isinstance(other, TimeSet):
			return other in other.intersection(self)
	
	def __eq__(self, other):
		return self.contains(other) and other.contains(self)
	
	def intersects(self, other):
		if isinstance(other, self.__class__):
			return self.start in other or self.end in other or other.start in self or other.end in self
		elif isinstance(other, numbers.Number):
			return other in self
		elif isinstance(other, RangeSet):
			return other.intersects(self)
		elif isinstance(other, TimeSet):
			return other.intersects(self)
	
	def intersection(self, other):
		if not self.intersects(other):
			return RangeSet() #empty set
		if isinstance(other, self.__class__):
			if other.start in self:
				start = other.start
				openstart = other.openstart
			else:
				start = self.start
				openstart = self.openstart
			if other.end in self:
				end = other.end
				openend = other.openend
			else:
				end = self.end
				openend = self.openend
			return TimeRange(start, end, openstart, openend)
		elif isinstance(other, RangeSet):
			return other.intersection(self)
		elif isinstance(other, TimeSet):
			return other.intersection(self)
				
	
	def __add__(self, other):
		if isinstance(other, self.__class__):
			if self.intersects(other):
				if other.start in self:
					start = self.start
					openstart = self.openstart
				else:
					start = other.start
					openstart = other.openstart
				if other.end in self:
					end = self.end
					openend = self.openend
				else:
					end = other.end
					openend = other.openend
				return TimeRange(start, end, openstart, openend)
			else:
				return RangeSet([self, other], checked = True)
	
	def __sub__(self, other):
		if isinstance(other, TimeRange):
			if other.start in self:
				if other.end in self:
					ranges = [TimeRange(self.start, other.start, self.openstart, not other.openstart), TimeRange(other.end, self.end, not other.openend, self.openend)]
					return RangeSet([range for range in ranges if range]).consolidate()
				else:
					return TimeRange(self.start, other.start, self.openstart, not other.openstart)
			else:
				if other.end in self:
					return TimeRange(other.end, self.end, not other.openend, self.openend)
				else:
					return TimeRange(self.start, self.end, self.openstart, self.openend)
	
	def start_time(self):
		return self.start
						
		

class RangeSet:
	
	def __init__(self, ranges = [], checked = False):
		if checked:
			self.ranges = set(ranges)
		else:
			minset = set()
			for range in ranges:
				minset = self.add_to_min_set(minset, range)
			self.ranges = minset
	
	def __str__(self):
		sortedranges = sorted(self.ranges, cmp = lambda x, y: cmp(x.start, y.start))
		if not sortedranges:
			return "{}"
		s = "{"
		for range in sortedranges:
			s += str(range) + " ; "
		return s[:-3] + "}"
	
	def __nonzero__(self):
		for range in self.ranges:
			if range:
				return True
		return False
	
	def __eq__(self, other):
		return self.contains(other) and other.contains(self)
	
	#if includes only a single range, returns that range.
	def consolidate(self):
		if len(self.ranges) == 1:
			for r in self.ranges:
				return r
		return self
	
	def add_to_min_set(self, minset, range):
		for oldrange in minset:
			if range.intersects(oldrange):
				minset = minset.difference([oldrange])
				return self.add_to_min_set(minset, range + oldrange)
		return minset.union([range])
	
	def __add__(self, other):
		if isinstance(other, TimeRange):
			minset = self.ranges
			minset = self.add_to_min_set(minset, other)
			return RangeSet(minset, checked = True).consolidate()
		elif isinstance(other, RangeSet):
			minset = self.ranges
			for range in other.ranges:
				minset = self.add_to_min_set(minset, range)
			return RangeSet(minset, checked = True).consolidate()
			
	def intersects(self, other):
		if self.intersection(other):
			return True
		return False
	
	def intersection(self, other):
		if isinstance(other, TimeRange):
			minset = set()
			for range in self.ranges:
				if range.intersects(other):
					minset.add(range.intersection(other))
			return RangeSet(minset, checked = True).consolidate()
		elif isinstance(other, RangeSet):
			minset = set()
			for myrange in self.ranges:
				for otherrange in other.ranges:
					if myrange.intersects(otherrange):
						minset.add(myrange.intersection(otherrange))
			return RangeSet(minset, checked = True).consolidate()
		elif isinstance(other, TimeSet):
			times = set()
			for time in other.times:
				if time in self:
					times.add(time)
			return TimeSet(times, self.intersection(other.ranges))
	
	def __contains__(self, other):
		if isinstance(other, TimeRange):
			for range in self.ranges:
				if other in range:
					return True
			return False
		elif isinstance(other, RangeSet):
			for range in other.ranges:
				if range not in self:
					return False
			return True
		elif isinstance(other, numbers.Number):
			for range in self.ranges:
				if other in range:
					return True
		elif isinstance(other, TimeSet):
			for time in other.times:
				if time not in self:
					return False
			return other.ranges in self
			return False
	
	def __sub__(self, other):
		if isinstance(other, TimeRange):
			minset = set()
			for range in self.ranges:
				res = range - other
				if res:
					minset.add(res)
			return RangeSet(minset, checked = True).consolidate()
		elif isinstance(other, RangeSet):
			minset = set()
			for myrange in self.ranges:
				res = myrange
				print res, "orig"
				for otherrange in other.ranges:
					res -= otherrange
					print otherrange, res
				if res:
					if isinstance(res, TimeRange):
						minset.add(res)
					elif isinstance(res, RangeSet):
						for r in res.ranges:
							minset.add(r)
			return RangeSet(minset, checked = True).consolidate()
	
	def start_time(self):
		if not self: 
			return float("inf")
		return min([range.start_time() for range in self.ranges])

class TimeSet:
	
	def __init__(self, times = [], ranges = None):
		self.times = set(times)
		if ranges:
			self.ranges = ranges
		else:
			self.ranges = RangeSet()
	
	def __str__(self):
		if not self.times and not self.ranges:
			return "{}"
		s = "{t | t "
		if self.times:
			s += "in ["
			for t in self.times:
				s += str(round(t, 2)) + ", "
			s = s[:-2] + "]"
		if self.ranges:
			if self.times:
				s += " or t in " + str(self.ranges)
			else:
				s += "in " + str(self.ranges)
		return s + "}"
	
	def __nonzero__(self):
		if self.times or self.ranges:
			return True
		return False
	
	def __eq__(self, other):
		return self.contains(other) and other.contains(self)
	
	def __add__(self, other):
		if isinstance(other, TimeSet):
			return TimeSet(self.times | other.times, self.ranges + other.ranges)
		elif isinstance(other, RangeSet) or isinstance(other, TimeRange):
			return TimeSet(set(self.times), self.ranges + other)
		elif isinstance(other, numbers.Number):
			return TimeSet(self.times.union([other]), self.ranges)
	
	def __sub__(self, other):
		if isinstance(other, TimeSet):
			return TimeSet(self.times - other.times, self.ranges - other.ranges)
		elif isinstance(other, RangeSet) or isinstance(other, TimeRange):
			return TimeSet(set(self.times), self.ranges - other)
		elif isinstance(other, numbers.Number):
			return TimeSet(self.times - set([other]), self.ranges)
	
	#does not handle special case where range.start == range.end and both ends are closed, so range is a single point and could be in discrete time set. This should probably be handled with a consolidate call on range objects.
	def __contains__(self, other):
		if isinstance(other, TimeSet):
			for time in other.times:
				if time not in self:
					return False
			return other.ranges in self
		elif isinstance(other, RangeSet) or isinstance(other, TimeRange):
			return other in self.ranges
		elif isinstance(other, numbers.Number):
			return other in self.times or other in self.ranges
	
	def intersection(self, other):
		if isinstance(other, TimeSet):
			times = {time for time in self.times if time in other.times or time in other.ranges}.union({time for time in other.times if time in self.ranges})
			return TimeSet(times, self.ranges.intersection(other.ranges))
		elif isinstance(other, RangeSet) or isinstance(other, TimeRange):
			times = {time for time in self.times if time in other}
			return TimeSet(times, self.ranges.intersection(other))
		
	def intersects(self, other):
		if self.intersection(other):
			return True
		return False
	
	def start_time(self):
		return min(min(self.times), self.ranges.start_time())

ALL_OF = -1
EQUALS = 0
SOME_OF = 1

class Time:
	
	def __init__(self, quantifier, times):
		self.quantifier = quantifier
		self.times = times
		
class Object:
	
	def __init__(self, name):
		self.name = name

class Predicate:
	
	def __init__(self, name):
		self.name = name

class Atom:
	
	def __init__(self, predicate, *args):
		self.predicate = predicate
		self.args = args
	
	def __str__(self):
		s = str(self.predicate) + "("
		for arg in self.args:
			s += str(arg) + ", "
		if self.args:
			s = s[:-2]
		return s + ")"
	
	def __eq__(self, other):
		if self.predicate != other.predicate:
			return False
		for i in range(len(self.args)):
			if i >= len(other.args) or self.args[i] != other.args[i]:
				return False
		return True

class Memory:
	
	def __init__(self, atom, truefalse, timelearned, timetrue, etiology):
		self.atom = atom
		self.truefalse = truefalse
		self.timelearned = timelearned
		self.timetrue = timetrue
		self.etiology = etiology
	
	def __str__(self):
		s = "Memory: " + str(self.atom) + ", " + str(self.timetrue)
		if not self.truefalse:
			s += " - False"
		return s

def current_time():
	return (datetime.datetime.today() - STARTTIME).total_seconds()

class MemByTime:
	
	def __init__(self, meminterval = 10):
		self.meminterval = meminterval
		#self.timeinterval - later, possibly track intervals in time.
		self.intervals = []
		self.mems = []
	
	def store(self, mem):
		#first, store mem count interval, if applicable
		if len(self.mems) % self.meminterval == 0:
			self.intervals.append(mem.timelearned)
		self.mems.append(mem)
	
	def recall(self, n, t = -0.1):
		insertpoint = max(0, bisect(self.intervals, t) - 1)
		i = insertpoint * self.meminterval
		while i < len(self.mems) and self.mems[i].timelearned <= t:
			i += 1
		return self.mems[i:i + n]

class SearchResult:
	
	TRUE = True
	FALSE = False
	UNKNOWN = "unknown"
	TRUE_SO_FAR = "true so far" #for universal quantifiers that have been supported and not disproven.
	FALSE_SO_FAR = "false so far" #for existential quantifiers that have evidence against and not proven.
	
	def __init__(self, atom, truefalse, time, quantifier):
		self.atom = atom
		self.time = time
		self.truefalse = truefalse
		self.checktype = quantifier
		self.memories = {}
	
	#assumes only matching atoms will be added here. Might be better to do that check in this method.
	def add_result(self, memory):
		self.memories[memory.timetrue.start_time()] = memory
	
	def final(self):
		return self.res() in [self.TRUE, self.FALSE]
	
	#assumes no conflicting information. At some point will need to deal with this possibility. Also, only checks memories indivudally. If several memories over the inquiry time range, this method will not figure that out.
	def res(self):
		if not self.memories:
			return self.UNKNOWN
		elif self.checktype == ALL_OF:
			for mem in self.memories.values():
				if self.truefalse != mem.truefalse:
					return self.FALSE
				elif self.time in mem.timetrue:
					return self.TRUE
			return self.TRUE_SO_FAR
		elif self.checktype == SOME_OF:
			for mem in self.memories.values():
				if self.truefalse == mem.truefalse:
					return self.TRUE
				elif self.time in mem.timetrue:
					return self.FALSE
			return self.FALSE_SO_FAR

class MemSearch:
	
	def __init__(self, atom, truefalse, time, memstore, quantifier = ALL_OF, starttime = 0):
		self.memstore = memstore
		self.result = SearchResult(atom, truefalse, time, quantifier)
		self.atom = atom
		self.time = time
		self.relevantmems = []
		self.memschecked = []
		self.memsgathereduntil = starttime - 0.1
		self.finished = False
	
	#this is currently doing things fairly stupidly, just iterating through all memories to find the relevant ones.
	def get_relevant_mems(self, dt, memsper = 10):
		tstart = current_time()
		while current_time() < tstart + dt:
			nextmems = self.memstore.recall(memsper, self.memsgathereduntil)
			if not nextmems:
				break
			self.memsgathereduntil = nextmems[-1].timelearned			
			nextmems = [mem for mem in nextmems if mem.timetrue.intersects(self.time)]
			self.relevantmems += nextmems
	
	def search_mems(self, dt, memsper = 10):
		tstart = current_time()
		while not self.finished and current_time() < tstart + dt:
			if not self.relevantmems:
				break
			for mem in self.relevantmems[:memsper]:
				print "Checking: ", mem
				if mem.atom == self.atom:
					self.result.add_result(mem)
			self.relevantmems = self.relevantmems[memsper:]
			if self.result.final():
				self.finished = True
	
	def res(self):
		return self.result.res()
	
	def go(self, dt = 0.2):
		self.get_relevant_mems(dt / 2)
		self.search_mems(dt / 2)

#unlike memsearch, which is designed to return a truth value, this search returns all relevant memories (found in alotted time). atom may contain "None" values for predicate or args, signifying variables.
class SearchPartial(MemSearch):
		
	def fits(self, atom):
		if self.atom.predicate and self.atom.predicate != atom.predicate:
			return False
		if len(self.atom.args) > len(atom.args):
			return False
		for i in range(len(self.atom.args)):
			if self.atom.args[i] and self.atom.args[i] != atom.args[i]:
				return False
		return True
	
	def search_mems(self, dt, memsper = 10):
		tstart = current_time()
		while not self.finished and current_time() < tstart + dt:
			if not self.relevantmems:
				self.finished = True
				break
			for mem in self.relevantmems[:memsper]:
				print "Checking: ", mem
				if self.fits(mem.atom):
					self.result.add_result(mem)
			self.relevantmems = self.relevantmems[memsper:]
	
	def res(self):
		return self.result.memories.values()
		
'''
Inference
'''

def try_mp(atom, truefalse, time, store):
	implymem = Atom("implies", None, atom)
	search = SearchPartial(implymem, truefalse, time, store)
	
'''
Demo
'''

def quick_check(atom, truefalse, time, store, partial = False):
	if partial:
		search = SearchPartial(atom, truefalse, time, store)
	else:
		search = MemSearch(atom, truefalse, time, store)
	search.go()
	return search.res()

#will break if sentence ends in an article.
def combine_articles(words):
	newwords = []
	i = 0
	while i < len(words):
		if words[i] in ["the", "an", "a"]:
			newwords.append(words[i] + " " + words[i + 1])
			i += 1
		else:
			newwords.append(words[i])
		i += 1
	return newwords

def false(words):
	if "not" in words:
		words.remove("not")
		return True
	return False

def is_pred_search(words):
	return words[0].lower() == "what"

def is_q(words):
	val = words[0] in ["is", "was", "does", "did"]
	return val

def time_word_index(words):
	for i in range(len(words)):
		if words[i] in ["at", "from", "always"]:
			return i

def get_time(timewords):
	if timewords[0] == "from":
		time = TimeRange(float(timewords[1]), float(timewords[3]))
	elif timewords[0] == "at":
		time = TimeSet([float(timewords[1])])
	elif timewords[0] == "always":
		time = TimeRange(-float("inf"), float("inf"))
	return time

def parse_input_line(line, store):
	words = combine_articles([word.lower() for word in line.split()])
	isfalse = false(words)
	if is_q(words):
		atomwords = words[1:time_word_index(words)]
		if len(atomwords) == 2:
			atom = Atom(atomwords[1], atomwords[0])
		elif len(atomwords) == 3:
			atom = Atom(atomwords[1], atomwords[0], atomwords[2])
		elif len(atomwords) == 4:
			atom = Atom(atomwords[0], *atomwords[1:])
		timewords = words[time_word_index(words):]
		#print timewords
		timewordsegs = []
		while "and" in timewords:
			timewordsegs.append(timewords[0:timewords.index("and")])
			timewords = timewords[timewords.index("and") + 1:]
		time = get_time(timewords)
		for seg in timewordsegs:
			time = time + get_time(seg)
		#print atom
		res = quick_check(atom, not isfalse, time, store)
		if res == True:
			print "Yes."
		elif res == False:
			print "No."
		elif res == SearchResult.TRUE_SO_FAR:
			print "I don't know for sure, but it seems like it."
		elif res == SearchResult.FALSE_SO_FAR:
			print "I don't know for sure, but it seems unlikely."
		else:
			print "I don't know."
	elif is_pred_search(words):
		atomwords = words[2:time_word_index(words)]
		atom = Atom(atomwords[0], None, None, None)
		timewords = words[time_word_index(words):]
		#print timewords
		timewordsegs = []
		while "and" in timewords:
			timewordsegs.append(timewords[0:timewords.index("and")])
			timewords = timewords[timewords.index("and") + 1:]
		time = get_time(timewords)
		for seg in timewordsegs:
			time = time + get_time(seg)
		#print atom
		res = quick_check(atom, not isfalse, time, store, True)
		for mem in res:
			print mem.atom.args
	else:
		#print words
		tindex = time_word_index(words)
		atomwords = [words[0]] + words[2:tindex]
		#print atomwords
		if len(atomwords) == 2:
			atom = Atom(atomwords[1], atomwords[0])
		elif len(atomwords) == 3:
			atom = Atom(atomwords[1], atomwords[0], atomwords[2])
		elif len(atomwords) == 4:
			atom = Atom(atomwords[0], *atomwords[1:])
		timewords = words[time_word_index(words):]
		#print timewords
		timewordsegs = []
		while "and" in timewords:
			timewordsegs.append(timewords[0:timewords.index("and")])
			timewords = timewords[timewords.index("and") + 1:]
		time = get_time(timewords)
		for seg in timewordsegs:
			time = time + get_time(seg)
		mem = Memory(atom, not isfalse, current_time(), time, None)
		store.store(mem)
		print "stored: " + str(mem)

if __name__ == "__main__":	
	store = MemByTime()
	while True:
		#try:
		input = raw_input()
		if input == "q":
			break
		parse_input_line(input, store)
		#except:
		#print "not understood"




	











