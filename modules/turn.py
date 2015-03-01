def match_class(obj1, obj2):
	return obj1 and obj2 and obj1.__class__() == obj2.__class__()


class Epoch:
	
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "Septmeber", "October", "November", "December"]
	
	#all turn values in epoch class methods are from start of epoch
	def __init__(self, startturn, starttime, displayunit, increment, partial=None):
		self.startturn = startturn
		self.starttime = starttime
		self.unit = displayunit
		self.inc = increment
		self.partial = partial #i.e. ("Minutes", 1.0/3600) or ["Jan.", "Feb...] - 2nd meaning divide among all elts evenly
	
	def get_time(self, turn):
		return self.starttime + turn * self.inc
	
	def get_s(self, turn):
		val = self.get_time(turn)
		if self.partial:
			if self.partial.__class__() == (()).__class__():
				s = str(int(val)) + self.unit + str(int((val - int(val)) / self.partial[1])) + self.partial[0]
			elif self.partial.__class__() == [].__class__():
				s = str(int(val)) + self.unit + self.partial[int((val - int(val)) * len(self.partial))]
			return s
		return str(val) + self.unit
	
	def new_from_end(self, turns, increment, partial):
		return Epoch(self.startturn + turns, self.get_time(turns), self.unit, increment, partial)
	

class IncrementPlan:
	
	def __init__(self, epochs, start):
		#[(startturn, inc), (startturn, inc)]
		if epochs.__class__() == [].__class__():
			self.epochs = epochs
		else:
			self.epochs = [epochs]
		self.turn = 0
		self.time = start
	
	#adds to end. This is meant to used once at setup for each epoch.
	def add_epoch(self, epoch):
		self.epochs.append(epoch)
	
	def set_end(self, turn):
		self.end = turn
	
	def turns_to_end(self):
		if hasattr(self, "end"):
			return self.end - self.turn #can be negative
		else:
			return None
	
	def current_epoch(self):
		i = len(self.epochs) - 1
		while i >= 0:
			if self.epochs[i].startturn <= self.turn:
				return self.epochs[i]
			i -= 1
	
	def turns_to_epoch(self):
		for epoch in self.epochs:
			if epoch.startturn > self.turn:
				return epoch.startturn - self.turn
		return self.turns_to_end()
	
	def turns_since_epoch(self):
		last = self.epochs[0]
		for epoch in self.epochs[1:]:
			if epoch.startturn > self.turn:
				break
			last = epoch
		return self.turn - last.startturn
	
	def time_to_epoch(self):
		return self.turns_to_epoch() * self.current_epoch().inc
	
	def time_since_epoch(self):
		return self.turns_since_epoch() * self.current_epoch().inc
	
	def get_time(self):
		currentepoch = self.current_epoch()
		return currentepoch.get_time(self.turn - currentepoch.startturn)
	
	def next_turn(self):
		self.turn += 1
	
	def get_s(self):
		currentepoch = self.current_epoch()
		return currentepoch.get_s(self.turn - currentepoch.startturn)
		
class TurnHandler:
	
	def __init__(self, incrementplan):
		self.incrementplan = incrementplan
		self.players = [] #(player, firstturn, frequency) - array is order
		self.current = 0
		self.turnjustended = False
	
	def add_player(self, player, frequency = 1):
		self.players.append((player, self.incrementplan.turn, frequency))
	
	def current_player(self):
		return self.players[self.current][0]
	
	def goes(self, index):
		player = self.players[index]
		return (self.incrementplan.turn - player[1]) % player[2] == 0
	
	def next_player(self):
		self.turnjustended = False
		while True:
			self.current += 1
			if self.current >= len(self.players):
				self.current = 0
				self.turnjustended = True
				self.incrementplan.next_turn()
			if self.goes(self.current):
				break
	
	def turn(self):
		return self.incrementplan.turn
	
	def get_time(self):
		return self.incrementplan.get_time()
	
	def get_time_s(self):
		return self.incrementplan.get_s()

####################################
## Parts of turn
####################################

playerdata = {} #any data that must be saved between turns (resources, etc.)
playerendfuncs = {} #what to do (saving resources, etc.) at the end of a turn. Can vary by player.
playerstartfuncs = {} #What to do (calculating growth/production, etc.) at start of turn. Can vary by player.

def set_end_func(player, func):
	playerendfuncs[player] = func

def set_start_func(player, func):
	playerstartfuncs[player] = func

'''Tests:

epochs = []
epochs.append(Epoch(0, 1, " A.D. ", 2))
epochs.append(epochs[-1].new_from_end(5, 0.2, Epoch.months))
plan = IncrementPlan(epochs, 0)
print plan.get_s()
plan.next_turn()
print plan.get_s()
for i in range(10):
	plan.next_turn()
	print plan.get_s()

print ""
handler = TurnHandler(plan)
handler.add_player("Sally")
handler.add_player("Mark")
handler.add_player("Jeff")
print "Turn " + str(handler.turn()) + ", " + handler.get_time_s()

i = 0
while i < 10:
	print handler.current_player()
	handler.next_player()
	if handler.turnjustended:
		print ""
		print "Turn " + str(handler.turn()) + ", " + handler.get_time_s()
		i += 1
print "End."
'''
