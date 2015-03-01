Actions:
	negotiate_to_buy
	negotiate_to_sell
	ask_about
	talk_about
	ask_true
	answer_true
	attack



Knowledge:
	is_a
	has_attr
	has_obj
	has_knowledge
	has_desire
	-has changeability level (affects knowledge trust and reevaluation)

Desire:
	wants_to_know_that...

Types:
	
class Method:
	
	def __init


class Result:
	
	self.type = "result"
	
	LOSE_ABILITY = 0
	GAIN_ABILITY = 1
	IMPROVE_ABILITY = 2
	REDUCE_ABILITY = 3
	SET_ABILITY = 4
	
	LOSE_ATTR = 5
	GAIN_ATTR = 6
	IMPROVE_ATTR = 7
	REDUCE_ATTR = 8
	SET_ATTR = 9
	
	LOSE_OBJ = 10
	GAIN_OBJ = 11
	CHANGE_OBJ = 12 #call secondary result on given obj
	
	MOVE = 13
	MOVE_TO = 14
	
	def __init__(self, kind, args):
		self.kind = kind
		self.args = args

class Ability:
	
	

class Attribute:
	
	BOOLEAN = 0
	DISCRETE = 1
	NUMERIC = 2

class Knowledge:
	
	type = "knowledge"
	
	AT = 0
	HAS_ABILITY = 1
	HAS_ATTR = 2
	HAS_OBJ = 3
	HAS_KNOWLEDGE = 4
	HAS_DESIRE = 5
	
	def __init__(self, kind, subject, object, evidencelevel)
		self.kind = type
		self.args = [subject, object]
		self.belief = evidencelevel
	
	

class Agent:
	
	def __init__(self):
		self.motivators = []
		self.knowledge = []
		
	