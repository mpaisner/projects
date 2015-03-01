
class SelectState:
	
	def __init__(self, numturns, firstplayer = 0):
		self.players = []
		self.currentplayer = firstplayer
		self.firstplayer = firstplayer
		self.turn = 0
		self.maxturns = numturns
		
	def add_player(self, player):
		self.players.append(player)
	
	def get_current_player(self):
		return self.players[currentplayer]
	
	def next_player(self):
		self.currentplayer = (self.currentplayer + 1) % len(self.players)
		if self.currentplayer == self.firstplayer:
			self.turn += 1
	
	def finished(self):
		return self.turn >= self.maxturns
	
class GameState:
	
	def __init__(self, players, firstplayer == 0):
		self.players = players
		self.firstplayer = firstplayer
		self.currentplayer = currentplayer
		self.turn = 0
	