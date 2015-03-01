import random

class WorldState:
	
	def __init__(self, territories):
		self.owners = {territory: None for territory in territories}
		self.armies = {territory: 0 for territory in territories}
	
	def setOwner(self, territory, owner):
		self.owners[territory] = owner
	
	def getOwner(self, territory):
		return self.owners[territory]
	
	def addArmies(self, territory, num):
		self.armies[territory] += num
	
	def removeArmies(self, territory, num):
		assert self.armies[territory] >= num
		self.armies[territory] -= num

class PlayerState:
	
	def __init__(self, name):
		self.name = name
		self.territories = set()
		self.cards = set()
		self.troopsToPlace = 0
	
class GameState:
	
	SETUP_PHASE = 0
	PLACE_PHASE = 1
	ATTACK_PHASE = 2
	MOVE_PHASE = 3
	
	def __init__(self, players, randomOrder = False):
		self.players = list(players)
		if randomOrder:
			random.shuffle(self.players)
		self.currentPlayeri = 0
		self.phase = self.SETUP_PHASE
	
	def assignTroopsToPlayer(self, player, num):
		player.troopsToPlace = num
	
	def assignStartingTroops(self, num):
		for player in self.players:
			self.assignTroopsToPlayer(player, num)
		
	def hasTroopsToPlace(self, player):
		return player.troopsToPlace > 0
	
	def currentPlayer(self):
		return self.players[self.currentPlayeri]
	
	def setCurrentPlayer(self, player):
		self.currentPlayeri = self.players.index(player)
	
	def nextPlayer(self):
		self.currentPlayeri = (currentPlayeri + 1) % len(self.players)
	
	def goToPhase(self, phase):
		self.phase = phase

class ActionType:
	
	'''
	this is an enum
	'''
	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return name

PLACE = ActionType("Place troops")
ATTACK = ActionType("Attack or pass")
CONQUER = ActionType("Move into conquered territory")
MOVE = ActionType("Move troops")
VICTORY = ActionType("A player has won")

class DisplayEventType:
	
	'''
	this is an enum
	'''
	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return name

TROOP_NUM_CHANGE = DisplayEventType("troop num change")
OWNER_CHANGE = DisplayEventType("owner change")

class DisplayEvent:
	
	def __init__(self, type, territory = None, player = None, num = None):
		self.type = type
		self.territory = territory
		self.player = player
		self.num = num
		
class State:
	
	def __init__(self, territories, playerNames, randomOrder = False):
		self.worldState = WorldState(territories)
		players = [PlayerState(name) for name in playerNames]
		self.gameState = GameState(players, randomOrder)
		self.occupying = None
		self.displayEvents = []
	
	def place(self, player, territory, num):
		if player != self.gameState.currentPlayer():
			raise Exception("Wrong player placing troops")
		if self.worldState.owners[territory] and self.world.owners[territory] != player:
			raise Exception("Trying to place in someone else's territory")
		elif not self.worldState.owners[territory]:
			self.displayEvents.append((OWNER_CHANGE, territory, player))
			self.worldState.setOwner(territory, player)
		self.worldState.addArmies(territory, num)
		self.displayEvents.append((TROOP_NUM_CHANGE, territory, self.worldState.armies[territory]))
		
		
		phase = self.gameState.phase
		if phase == GameState.SETUP_PHASE:
			for i in range(len(self.gameState.players)):
				self.gameState.nextPlayer()
				player = self.gameState.currentPlayer()
				if player.troopsToPlace > 0:
					break
		elif phase == GameState.PLACE_PHASE:
			if player.troopsToPlace == 0:
				self.gameState.goToPhase(GameState.ATTACK_PHASE)
		else:
			raise Exception("Placing troops in wrong phase")
	
	def attack(self, source, dest, attackerLosses, defenderLosses):
		if self.gameState.phase != GameState.ATTACK_PHASE:
			raise Exception("Attack occuring during wrong phase")
		if self.worldState.getOwner(source) != self.gameState.currentPlayer():
			raise Exception("Wrong player attacking")
		if attackerLosses > self.worldState.armies[source] or defenderLosses > self.worldState.armies[dest]:
			raise Exception("Too many troops lost")
		if attackerLosses > 0:
			self.worldState.removeArmies(source, attackerLosses)
			self.displayEvents.append((TROOP_NUM_CHANGE, source, self.worldState.armies[source]))
		if defenderLosses > 0:
			self.worldState.removeArmies(dest, defenderLosses)
			self.displayEvents.append((TROOP_NUM_CHANGE, dest, self.worldState.armies[dest]))
	
	def getNextAction(self):
		player = self.gameState.currentPlayer()
		phase = self.gameState.phase
		if phase == GameState.SETUP_PHASE:
			return self._nextActionSetup(player)
		elif phase == GameState.PLACE_PHASE:
			return self._nextActionPlace(player)
		elif phase == GameState.ATTACK_PHASE:
			return (ATTACK, player)
		elif phase == GameState.MOVE_PHASE:
			
	
	def _nextActionSetup(self, player):
		action = None
		for i in range(len(self.gameState.players)):
			if player.troopsToPlace > 0:
				action = (PLACE, player)
				self.gameState.nextPlayer()
				break
			self.gameState.nextPlayer()
			player = self.gameState.currentPlayer()
		if not action:
			self.gameState.goToPhase(GameState.PLACE_PHASE)
			return self.getNextAction()
		else:
			return action
	
	def _nextActionPlace(self, player):
		if player.troopsToPlace > 0:
			action = (PLACE, player)
		else:
			self.gameState.goToPhase(GameState.ATTACK_PHASE)
			action = (ATTACK, player)
		return action
	
	def _nextActionMove(self, player):
		
	