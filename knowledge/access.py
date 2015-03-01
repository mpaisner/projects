
class SortedList(list):
	
	def add(self, priority, value):
		for i in range(len(self)):
			if self[i][0] < priority:
				self.insert(i, (priority, value))
				return
		self.append((priority, value))
	
	def set_priority(self, index, priority):
		object = self.pop(index)[1]
		self.add(priority, object)
	
	def clean(self):
		seen = set()
		removed = set()
		for priority, value in self:
			if value in seen:
				removed.add((priority, value))
			else:
				seen.add(value)
		for item in removed:
			self.remove(item)
	
	def index(self, value, start = 0):
		for i in range(start, len(self)):
			if self[i][1] == value:
				return i

class Test:
	
	def __init__(self, l):
		self.l = l
	
	def get(self, i):
		return self.l[i]
		
class Memory(dict):
	pass

#this is important. Should be a list of tuples: (other_object, strength)
def get_associations(object):
	#actually, probably should be done like this:
	return object.get_associations()
	#return [(object.get(i), i) for i in range(len(object.l))]

def partial_store(memory, object, leaveout):
	if object not in memory:
		memory[object] = SortedList()
	associations = [(assoc, strength) for assoc, strength in get_associations(object) if assoc not in leaveout]
	for association, strength in associations:
		if association not in memory:
			partial_store(memory, association, leaveout + object)
		memory[association].add(strength, object)
		memory[object].add(strength, association)
			

def store(memory, object):
	partial_store(memory, object, [])

class Search:

	#query is SortedList<strength, term>
	def __init__(self, memory, query, targetresults = 10, maxdepth = 4, searchratio = 0.8, normalizeconst = 1.0):
		self.query = query
		self.searched = {} #{Object: strength}
		self.memory = memory.copy()
		self.queue = SortedList()
		for strength, term in self.query:
			self.queue.add(strength, term)
	
	def eval(self, object):
		#This is where an object is evaluated and added to searched, which eventually becomes the return value.
	
	def update_mem(self, object):
		store(self.memory, object)
		