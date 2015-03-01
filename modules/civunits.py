import civtech

attrs = ["name", "attack", "defense", "movement", "hp", "fire power", "prereq", "obsolete", "domain", "cost", "special"]

def attr_key(attr, attrlist = attrs):
	if attr in attrlist:
		return attrlist.index(attr)
	return len(attrlist)
	
def get_attr_key(attrlist):
	return lambda attr: attr_key(attr, attrlist)

class Unit:
	
	def __init__(self, args):
		self.data = {}
		for key in args:
			self.data[key] = args[key]
	
	def set(self, args):
		for key in args:
			self.data[key] = args[key]
	
	def get(self, key):
		if key in self.data:
			return self.data[key]
		return []
	
	def long_str(self, attrs=None):
		s = self.get("name") + ": \n"
		for attr in self.data:
			if attr != "name":
				s += "\t" + attr + " = " + str(self.get(attr)) + "\n"
		return s
	
	def __str__(self):
		return self.get("name")
			

DEFAULT_UNITS = {
"aegis cruiser": {
	"attack": 		8,
	"defense": 		8,
	"movement":		5,
	"hp": 			3,
	"fire power":	2,
	"domain":		"sea",
	"prereq":		"rocketry",
	"obsolete":		None,
	"cost":			80,
	"role":			"air defense",
	"special":		["detect", "sight", "vs bonus"],
	"detects":		["sub"],
	"sight":		2,
	"bonus type":	[("air", 2), ("missile", 4)]
	},
"alpine troops": {
	"attack": 		5,
	"defense": 		5,
	"movement":		1,
	"hp": 			2,
	"fire power":	1,
	"domain":		"land",
	"prereq":		"tactics",
	"obsolete":		None,
	"cost":			50,
	"role":			"defense",
	"special":		["move constant"],
	"move cost":	-3 # -3 -> 1/3
	},
"archers": {
	"attack": 		3,
	"defense": 		2,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"warrior code",
	"obsolete":		"gunpowder",
	"cost":			30,
	"role":			"defend",
	"special":		[]
	},
"armor": {
	"attack": 		10,
	"defense": 		5,
	"movement":		3,
	"hp": 			3,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"mobile warfare",
	"obsolete":		None,
	"cost":			80,
	"role":			"attack",
	"special":		[]
	},
"artillery": {
	"attack": 		10,
	"defense": 		1,
	"movement":		1,
	"hp": 			2,
	"fire power":	2,
	"domain":		"ground",
	"prereq":		"machine tools",
	"obsolete":		"robotics",
	"cost":			50,
	"role":			"attack",
	"special":		[]
	},
"battleship": {
	"attack": 		12,
	"defense": 		12,
	"movement":		4,
	"hp": 			4,
	"fire power":	2,
	"domain":		"sea",
	"prereq":		"automobile",
	"obsolete":		None,
	"cost":			160,
	"role":			"sea",
	"special":		["sight"],
	"sight":		2
	},
"bomber": {
	"attack": 		12,
	"defense": 		1,
	"movement":		8,
	"hp": 			2,
	"fire power":	2,
	"domain":		"air",
	"prereq":		"advanced flight",
	"obsolete":		"stealth",
	"cost":			120,
	"role":			"bomb",
	"special":		["sight", "attack ends turn"],
	"sight":		2,
	"range":		2
	},
"cannon": {
	"attack": 		8,
	"defense": 		1,
	"movement":		1,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"metallurgy",
	"obsolete":		"machine tools",
	"cost":			40,
	"role":			"attack",
	"special":		[]
	},
"caravan": {
	"attack": 		0,
	"defense": 		1,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"trade",
	"obsolete":		"the corporation",
	"cost":			50,
	"role":			"trade",
	"special":		["no zoc", "trade route", "build wonder"]
	},
"caravel": {
	"attack": 		2,
	"defense": 		1,
	"movement":		3,
	"hp": 			1,
	"fire power":	1,
	"domain":		"sea",
	"prereq":		"navigation",
	"obsolete":		"magnetism",
	"cost":			30,
	"role":			"ancient sea",
	"special":		["transport"],
	"trans type":	"ground",
	"trans num":	3
	},
"carrier": {
	"attack": 		1,
	"defense": 		9,
	"movement":		5,
	"hp": 			4,
	"fire power":	2,
	"domain":		"sea",
	"prereq":		"advanced flight",
	"obsolete":		None,
	"cost":			160,
	"role":			"carrier",
	"special":		["transport", "sight"],
	"sight":		2,
	"trans type":	"air",
	"trans num":	8
	},
"catapult": {
	"attack": 		6,
	"defense": 		1,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"mathematics",
	"obsolete":		"metallurgy",
	"cost":			40,
	"role":			"attack",
	"special":		[]
	},
"cavalry": {
	"attack": 		8,
	"defense": 		3,
	"movement":		2,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"tactics",
	"obsolete":		"mobile warfare",
	"cost":			60,
	"role":			"attack",
	"special":		["horse"]
	},
"chariot": {
	"attack": 		3,
	"defense": 		1,
	"movement":		2,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"the wheel",
	"obsolete":		"polytheism",
	"cost":			30,
	"role":			"attack",
	"special":		["horse"]
	},
"cruise missile": {
	"attack": 		18,
	"defense": 		0,
	"movement":		12,
	"hp": 			1,
	"fire power":	3,
	"domain":		"air",
	"prereq":		"rocketry",
	"obsolete":		None,
	"cost":			80,
	"role":			"cruise missile",
	"special":		["kamikaze"],
	"range":		1
	},
"cruiser": {
	"attack": 		6,
	"defense": 		6,
	"movement":		5,
	"hp": 			3,
	"fire power":	2,
	"domain":		"sea",
	"prereq":		"steel",
	"obsolete":		"rocketry",
	"cost":			80,
	"role":			"sea",
	"special":		[]
	},
"crusaders": {
	"attack": 		5,
	"defense": 		1,
	"movement":		2,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"monotheism",
	"obsolete":		"leadership",
	"cost":			40,
	"role":			"attack",
	"special":		["horse"]
	},
"destroyer": {
	"attack": 		4,
	"defense": 		4,
	"movement":		6,
	"hp": 			3,
	"fire power":	1,
	"domain":		"sea",
	"prereq":		"electricity",
	"obsolete":		None,
	"cost":			60,
	"role":			"sea",
	"special":		["detect", "sight"],
	"sight":		2,
	"detects":		["sub"]
	},
"diplomat": {
	"attack": 		0,
	"defense": 		0,
	"movement":		2,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"writing",
	"obsolete":		"espionage",
	"cost":			30,
	"role":			"diplomat",
	"special":		["no zoc", "embassy", "steal tech", 
					"destroy improvement", "investigate city"],
	"spy skill":	1
	},
"dragoons": {
	"attack": 		5,
	"defense": 		2,
	"movement":		2,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"leadership",
	"obsolete":		"tactics",
	"cost":			50,
	"role":			"attack",
	"special":		["horse"]
	},
"elephant": {
	"attack": 		4,
	"defense": 		1,
	"movement":		2,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"polytheism",
	"obsolete":		"monotheism",
	"cost":			40,
	"role":			"attack",
	"special":		[]
	},
"engineers": {
	"attack": 		0,
	"defense": 		2,
	"movement":		2,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"explosives",
	"obsolete":		None,
	"cost":			40,
	"role":			"settle",
	"special":		["build city", "build road", "build railroad", 
					"irrigate", "mine", "transform", "join city", "costs pop"],
	"pop cost":		1,
	"build speed":	2
	},
"explorer": {
	"attack": 		0,
	"defense": 		1,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"seafaring",
	"obsolete":		"guerilla warfare",
	"cost":			30,
	"role":			"explore",
	"special":		["no-zoc", "move constant"],
	"move cost":	-3
	},
"fanatics": {
	"attack": 		4,
	"defense": 		4,
	"movement":		1,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"fundamentalism",
	"obsolete":		None,
	"cost":			20,
	"role":			"defend",
	"special":		["only gov"],
	"gov":			"fundamentalism"
	},
"fighter": {
	"attack": 		4,
	"defense": 		3,
	"movement":		10,
	"hp": 			2,
	"fire power":	2,
	"domain":		"air",
	"prereq":		"flight",
	"obsolete":		"stealth",
	"cost":			60,
	"role":			"fighter",
	"special":		["sight", "air attack", "scramble"],
	"sight":		2,
	"scramble":		4
	},
"freight": {
	"attack": 		0,
	"defense": 		1,
	"movement":		2,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"the corporation",
	"obsolete":		None,
	"cost":			50,
	"role":			"trade",
	"special":		["no zoc", "trade route", "build wonder"]
	},
"frigate": {
	"attack": 		4,
	"defense": 		2,
	"movement":		4,
	"hp": 			2,
	"fire power":	1,
	"domain":		"sea",
	"prereq":		"magnetism",
	"obsolete":		"electricity",
	"cost":			50,
	"role":			"sea",
	"special":		[]
	},
"galleon": {
	"attack": 		0,
	"defense": 		2,
	"movement":		4,
	"hp": 			2,
	"fire power":	1,
	"domain":		"sea",
	"prereq":		"magnetism",
	"obsolete":		"industrialization",
	"cost":			40,
	"role":			"sea trans",
	"special":		["transport"],
	"trans type":	"land",
	"trans num":	4
	},
"helicopter": {
	"attack": 		10,
	"defense": 		3,
	"movement":		6,
	"hp": 			2,
	"fire power":	2,
	"domain":		"ground",
	"prereq":		"polytheism",
	"obsolete":		"monotheism",
	"cost":			40,
	"role":			"attack",
	"special":		["sight", "detects"],
	"sight":		2,
	"detects":		["sub"],
	"range":		0
	},
"horsemen": {
	"attack": 		2,
	"defense": 		1,
	"movement":		2,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"horseback riding",
	"obsolete":		"chivalry",
	"cost":			20,
	"role":			"attack",
	"special":		["horse"]
	},
"howitzer": {
	"attack": 		12,
	"defense": 		2,
	"movement":		2,
	"hp": 			3,
	"fire power":	2,
	"domain":		"ground",
	"prereq":		"robotics",
	"obsolete":		None,
	"cost":			70,
	"role":			"attack",
	"special":		["no walls"]
	},
"ironclad": {
	"attack": 		4,
	"defense": 		4,
	"movement":		4,
	"hp": 			3,
	"fire power":	1,
	"domain":		"sea",
	"prereq":		"steam engine",
	"obsolete":		"electricity",
	"cost":			60,
	"role":			"sea",
	"special":		[]
	},
"knight": {
	"attack": 		4,
	"defense": 		2,
	"movement":		2,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"chivalry",
	"obsolete":		"leadership",
	"cost":			40,
	"role":			"attack",
	"special":		["horse"]
	},
"legion": {
	"attack": 		4,
	"defense": 		2,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"iron working",
	"obsolete":		"gunpowder",
	"cost":			40,
	"role":			"attack",
	"special":		[]
	},
"marine": {
	"attack": 		8,
	"defense": 		5,
	"movement":		1,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"amphibious warfare",
	"obsolete":		None,
	"cost":			60,
	"role":			"marine",
	"special":		["amphibious"]
	},	
"mechanized infantry": {
	"attack": 		6,
	"defense": 		6,
	"movement":		3,
	"hp": 			3,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"labor union",
	"obsolete":		None,
	"cost":			50,
	"role":			"defend",
	"special":		[]
	},	
"musketeers": {
	"attack": 		3,
	"defense": 		3,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"warrior code",
	"obsolete":		"gunpowder",
	"cost":			30,
	"role":			"defend",
	"special":		[]
	},
"nuclear missile": {
	"attack": 		99,
	"defense": 		0,
	"movement":		16,
	"hp": 			1,
	"fire power":	1,
	"domain":		"air",
	"prereq":		"rocketry",
	"obsolete":		None,
	"cost":			160,
	"role":			"nuke",
	"special":		["kamikaze", "nuke", "needs wonder"],
	"wonder":		"manhattan project"
	},
"paratrooper": {
	"attack": 		6,
	"defense": 		4,
	"movement":		1,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"combined arms",
	"obsolete":		None,
	"cost":			60,
	"role":			"paratrooper",
	"special":		["paradrop"],
	"para range":	8
	},
"partisans": {
	"attack": 		4,
	"defense": 		4,
	"movement":		1,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"guerilla warfare",
	"obsolete":		None,
	"cost":			50,
	"role":			"defend",
	"special":		["no zoc", "move constant"],
	"move cost":	-3
	},
"phalanx": {
	"attack": 		1,
	"defense": 		2,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"bronze working",
	"obsolete":		"feudalism",
	"cost":			20,
	"role":			"defend",
	"special":		[]
	},
"pikeman": {
	"attack": 		1,
	"defense": 		2,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"feudalism",
	"obsolete":		"gunpowder",
	"cost":			20,
	"role":			"defend",
	"special":		["vs bonus"],
	"bonus type":	"horse",
	"bonus %":		50
	},
"rifleman": {
	"attack": 		5,
	"defense": 		4,
	"movement":		1,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"conscription",
	"obsolete":		"labor union",
	"cost":			40,
	"role":			"defend",
	"special":		[]
	},
"settlers": {
	"attack": 		0,
	"defense": 		1,
	"movement":		1,
	"hp": 			2,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		None,
	"obsolete":		"explosives",
	"cost":			40,
	"role":			"settle",
	"special":		["build city", "build road", "build railroad", 
					"irrigate", "mine", "join city", "costs pop"],
	"pop cost":		1,
	"build speed":	1
	},
"spy": {
	"attack": 		0,
	"defense": 		0,
	"movement":		3,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		"espionage",
	"obsolete":		None,
	"cost":			30,
	"role":			"spy",
	"special":		["no zoc", "embassy", "steal tech", 
					"destroy improvement", "investigate city", "plant nuke"],
	"spy skill":	2
	},
"stealth bomber": {
	"attack": 		14,
	"defense": 		5,
	"movement":		12,
	"hp": 			2,
	"fire power":	2,
	"domain":		"air",
	"prereq":		"stealth",
	"obsolete":		None,
	"cost":			160,
	"role":			"bomb",
	"special":		["sight", "attack ends turn"],
	"sight":		2,
	"range":		2
	},
"stealth fighter": {
	"attack": 		8,
	"defense": 		4,
	"movement":		14,
	"hp": 			2,
	"fire power":	2,
	"domain":		"air",
	"prereq":		"stealth",
	"obsolete":		None,
	"cost":			80,
	"role":			"fighter",
	"special":		["sight", "air attack", "scramble"],
	"sight":		2,
	"scramble":		4
	},
"submarine": {
	"attack": 		10,
	"defense": 		2,
	"movement":		3,
	"hp": 			3,
	"fire power":	2,
	"domain":		"air",
	"prereq":		"combustion",
	"obsolete":		None,
	"cost":			60,
	"role":			"sub",
	"special":		["sight", "sub"],
	"sight":		2
	},
"galleon": {
	"attack": 		0,
	"defense": 		3,
	"movement":		5,
	"hp": 			3,
	"fire power":	1,
	"domain":		"sea",
	"prereq":		"industrialization",
	"obsolete":		None,
	"cost":			50,
	"role":			"sea trans",
	"special":		["transport"],
	"trans type":	"land",
	"trans num":	8
	},
"trireme": {
	"attack": 		1,
	"defense": 		1,
	"movement":		3,
	"hp": 			1,
	"fire power":	1,
	"domain":		"sea",
	"prereq":		"map making",
	"obsolete":		None,
	"cost":			40,
	"role":			"sea trans",
	"special":		["transport", "no ocean"],
	"trans type":	"land",
	"trans num":	2,
	"sink chance":	0.5
	},
"warriors": {
	"attack": 		1,
	"defense": 		1,
	"movement":		1,
	"hp": 			1,
	"fire power":	1,
	"domain":		"ground",
	"prereq":		None,
	"obsolete":		"feudalism",
	"cost":			10,
	"role":			"attack",
	"special":		[]
	},		
}




#requires techs to have been initialized (done automatically for base civ techs on import)
def init_units(unitdict):
	unittypes = {}
	for name in unitdict:
		unit = Unit(unitdict[name])
		unittypes[name] = unit
		unit.set({"name": name})
		if unit.get("prereq"):
			unit.set({"prereq": civtech.techs[unit.get("prereq")]})
		if unit.get("obsolete"):
			unit.set({"obsolete": civtech.techs[unit.get("obsolete")]})
	return unittypes

units = init_units(DEFAULT_UNITS)

for unit in units.values():
	print unit.long_str()