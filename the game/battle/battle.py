
class Unit:
	
	def freeze(self):
		raise Exception("not implemented")
		#creates a static copy of the unit. The copy's "original()" method will return this unit
	
	def original(self):
		return self

RESERVE = -2 #meaning of reserve changes depending on unit's owner (i.e. your reserve or mine)
DEPLOYING = -1 #troops who are leaving the reserve to deploy, but have not yet done so.

class BattleParticipant:

	def __init__(self, player, units, role):
		self.player = player
		self.role = role
		self.units = units
		self.visibleEnemies = {}

class Battle:
	
	'''
	note: battles do not check inputs. For example, if a player declares he is deploying 3 units, even though max deployment is 2 and one of the units declared is not in the battle, the deployment will still be honored. This is to allow rules to be broken by later changes
	'''
	
	def __init__(self, participants, location):
		self.participants = participants
		self.location = location
		self.round = 0
	
	def redraw(self):
		pass
	
	def log(self):
		pass #should save the battle's state immutably
	
	def getMaxDeployable(self, participant):
		return 2
	
	def deployingTroopsChosen(self, particpant, troops):
		for troop in troops:
			troop.battleLocation = DEPLOYING
		participant.units = participant.units | troops
		self.redraw()
	
	def 