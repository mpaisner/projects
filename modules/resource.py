import random

''' Docs:
ResourceCollector(e.g. Civ city) ->
	Def:
		world: must have a method deep_copy, which returns a copy (obviously)
		collectfunc(self, world) -> resources
		storefunc(self, resources, world) -> None
		sideeeffectfunc, modifyfunc same signature as storefunc.
	Use:
		Use get() to return resources and modify world correspondingly
		Use poll() to return (self[copy], resources, world[copy]) without changing underlying states. To iterate, thing.poll()[0].poll()[0]...poll()[0].get()
	
ResourceModifier (e.g. Civ improvement; these can be type or object) ->
	Def:
		modify(self, resources, collector) -> resources
		poll(self, resources, collector) -> resources [no effects]
'''

class ResourceCollector:
	
	#if resources are stored between turns, define storefunc
	#if collecting resources has side effects, define sideeffectfunc
	#if there are modifiers that should be applied, define modifyfunc
	def __init__(self, world, collectfunc, storefunc = None, sideeffectfunc = None, modifyfunc = None):
		self.world = world
		self.collect = collectfunc
		self.add_side_effects = sideeffectfunc
		self.store = storefunc
		self.modify = modifyfunc
	
	#uses input world. Returns resources.
	def get_changed(self, world):
		resources = self.collect(self, world)
		if self.modify:
			resources = self.modify(self, resources, world)
		if self.add_side_effects:
			self.add_side_effects(self, resources, world)
		if self.store:
			self.store(self, resources, world)
		return resources
	
	#get resources, apply side effects
	def get(self):
		return self.get_changed(self.world)
	
	#get (self, resources, world) using copies
	def poll(self):
		scopy = self.deep_copy()
		resources = scopy.get()
		return (scopy, resources, scopy.world)
	
	#get (self, resources, world) given world, using copies
	def poll_changed(self, world):
		scopy = self.deep_copy() #right now this makes an unnecessary world copy.
		wcopy = world.deep_copy() 
		resources = scopy.get_changed(wcopy)
		return (scopy, resources, wcopy)
	
	def deep_copy(self):
		return ResourceCollector(self.world.deep_copy(), self.collect, self.store, self.add_side_effects, self.modify)
			
	

class ResourceModifier:
	
	#define collector to make this an object rather than type - i.e. associate it with a particular collector.
	def __init__(self, modifyfunc, sideeffectfunc = None, collector = None):
		self.modify = modifyfunc
		self.add_side_effects = sideffectfunc
		self.collector = collector
	
	#applies changes to collector, side effects to world
	def mod(self, resources, collector = None):
		if not collector:
			collector = self.collector
		if self.add_side_effects:
			self.add_side_effects(self, resources, collector)
		return self.modify(self, resources, collector)
	
	#returns resources without adding side effects
	def poll(self, resources, collector = None):
		if not collector:
			collector = self.collector
		return self.modify(self, resources, collector)



#Test stuff	
def take_second(self, world):
	if len(world.list) > 1:
		return world.list[1]
	return None

def get_random(self, world):
	if world.list:
		return random.choice(world.list)

def remove_resource(self, resources, world):
	if resources:
		world.list.remove(resources)
	
	

class CopyList:
	
	def __init__(self, list):
		self.list = list
	
	def deep_copy(self):
		return CopyList(list(self.list))
		
l = [5, 6, 7, 8, 9]
world = CopyList(l)
r = ResourceCollector(world, get_random, sideeffectfunc = remove_resource)

print r.poll()[1]
w = r.world
s = r
for i in range(4):
	s, res, w = s.poll_changed(w)
	print w.list, res
	print s.poll_changed(w)[1]
for i in range(4):
	print r.get()