from things import Knowledge

AT = 0
	HAS_ABILITY = 1
	HAS_ATTR = 2
	HAS_OBJ = 3
	HAS_KNOWLEDGE = 4
	HAS_DESIRE = 5

def get_relevant_keys(item, level = 1, keys = {}):
	if level < 0 or item in keys:
		return
	else:
		keys[item] = True
	if not hasattr(item, "args"):
		return #final values
	for arg in item.args:
		get_relevant_keys(arg, 

def is_believable(assessor, other, fact):
	