

class Building:
	
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

DEFAULT_IMPROVEMENTS = {
"palace": {
	"cost":				100,
	"upkeep":			0,
	"prereq":			"masonry",
	"effects":			["capital"]
	},
"barracks": {
	"cost":				40,
	"upkeep":			1,
	"prereq":			None,
	"effects":			["new unit mod", "unit heal rate+%"],
	"mod type":			"ground",
	"mod effect":		"veteran",
	"heal type":		"ground",
	"heal%":			100
	},
"granary": {
	"cost":				60,
	"upkeep":			1,
	"prereq":			"pottery",
	"effects":			["growth food+%", "no famine"],
	"food%":			50
	},
"temple": {
	"cost":				40,
	"upkeep":			1,
	"prereq":			"ceremonial burial",
	"effects":			["content+", "content+ tech"],
	"content+":			1,
	"content+ tech":		"mysticism",
	"content+ change":	1
	},
"marketplace": {
	"cost":				80,
	"upkeep":			1,
	"prereq":			"currency",
	"effects":			["tax+%", "lux+%"],
	"tax+%":			50,
	"lux+%":			50
	},
"library": {
	"cost":				80,
	"upkeep":			1,
	"prereq":			"writing",
	"effects":			["research+%"],
	"research+%":		50
	},
"courthouse": {
	"cost":				80,
	"upkeep":			1,
	"prereq":			"code of laws",
	"effects":			["corruption-%", "waste-%", "bribe cost+%"],
	"corruption-%":		50,
	"waste-%":			50,
	"bribe cost+%":		100
	},
"city walls": {
	"cost":				80,
	"upkeep":			1,
	"prereq":			"masonry",
	"effects":			["defense vs+%"],
	"defence vs":		"ground",
	"defence +%":		200
	},
"aqueduct": {
	"cost":				80,
	"upkeep":			2,
	"prereq":			"construction",
	"effects":			["size bound"],
	"bound":			1 #ordinal, not pop
	},
"bank": {
	"cost":				120,
	"upkeep":			3,
	"prereq":			"banking",
	"effects":			["tax+%", "lux+%", "prereq build"],
	"tax+%":			50,
	"lux+%":			50,
	"prereq build":		"marketplace"
	},
"cathedral": {
	"cost":				120,
	"upkeep":			3,
	"prereq":			"monotheism",
	"effects":			["content+", "content+ tech"],
	"content+":			3,
	"content+ tech":		"theology",
	"content+ change":	1
	},
"university": {
	"cost":				160,
	"upkeep":			3,
	"prereq":			"university",
	"effects":			["research+%", "prereq build"],
	"research+%":		50,
	"prereq build":		"library"
	},
"mass transit": {
	"cost":				160,
	"upkeep":			4,
	"prereq":			"mass production",
	"effects":			["pollution from pop-%"],
	"pollution -%":		100,
	},
"coliseum": {
	"cost":				100,
	"upkeep":			4,
	"prereq":			"construction",
	"effects":			["content+", "content+ tech", "content- tech"],
	"content+":			3,
	"content+ tech":	"electronics",
	"content+ change":	1,
	"content- tech":	"communism",
	"content- change":	1
	},
"factory": {
	"cost":				200,
	"upkeep":			4,
	"prereq":			"industrialization",
	"effects":			["production+%"],
	"production+%":		50
	},
"manufacturing plant": {
	"cost":				320,
	"upkeep":			6,
	"prereq":			"robotics",
	"effects":			["production+%", "prereq build"],
	"production+%":		50,
	"prereq build":		"factory"
	},
"sdi defence": {
	"cost":				200,
	"upkeep":			4,
	"prereq":			"the laser",
	"effects":			["nuke protect"],
	"protect range":	3
	},
"recycling center": {
	"cost":				200,
	"upkeep":			2,
	"prereq":			"recycling",
	"effects":			["pollution from prod-%"],
	"pollution -%":		67
	},
"power plant": {
	"cost":				160,
	"upkeep":			4,
	"prereq":			"refining",
	"effects":			["production+%", "prereq build", "xor builds"],
	"production+%":		50,
	"prereq build":		"factory",
	"xor builds":		["hydro plant", "nuclear plant", "solar plant"],
	},
"hydro plant": {
	"cost":				240,
	"upkeep":			4,
	"prereq":			"electronics",
	"effects":			["production+%", "prereq build", "xor builds",
						"pollution from prod-%"],
	"production+%":		50,
	"prereq build":		"factory",
	"xor builds":		["power plant", "nuclear plant", "solar plant"],
	"pollution -%":		50
	},
"nuclear plant": {
	"cost":				160,
	"upkeep":			2,
	"prereq":			"nuclear power",
	"effects":			["production+%", "prereq build", "xor builds",
						"pollution from prod-%", "meltdown until tech"],
	"production+%":		50,
	"prereq build":		"factory",
	"xor builds":		["power plant", "hydro plant", "solar plant"],
	"pollution -%":		50,
	"no melt tech":		"nuclear fusion"
	},
"stock exchange": {
	"cost":				160,
	"upkeep":			4,
	"prereq":			"economics",
	"effects":			["tax+%", "lux+%", "prereq build"],
	"tax+%":			50,
	"lux+%":			50,
	"prereq build":		"bank"
	},
"sewer system": {
	"cost":				120,
	"upkeep":			2,
	"prereq":			"sanitation",
	"effects":			["size bound", "prereq build"],
	"prereq build":		"aqueduct",
	"bound":			2 #ordinal, not pop
	},
"supermarket": {
	"cost":				80,
	"upkeep":			3,
	"prereq":			"refrigeration",
	"effects":			["use terraform"],
	"terraform":		"farm"
	},
"superhighways": {
	"cost":				200,
	"upkeep":			5,
	"prereq":			"automobile",
	"effects":			["square+% with terraforms or", "trade route+%"],
	"terraforms":		["road", "railroad"],
	"bonus type":		"trade",
	"bonus+%":			50,
	"trade route+%":	50
	},
"research lab": {
	"cost":				160,
	"upkeep":			3,
	"prereq":			"computers",
	"effects":			["research+%", "prereq build"],
	"research+%":		50,
	"prereq build":		"university"
	},
"sam missile battery": {
	"cost":				100,
	"upkeep":			2,
	"prereq":			"rocketry",
	"effects":			["defense vs+%"],
	"defence vs":		"air",
	"defence +%":		100
	},
"coastal fortress": {
	"cost":				80,
	"upkeep":			1,
	"prereq":			"metallurgy",
	"effects":			["defense vs+%"],
	"defence vs":		"sea",
	"defence +%":		100
	},
"solar plant": {
	"cost":				320,
	"upkeep":			4,
	"prereq":			"environmentalism",
	"effects":			["production+%", "prereq build", "xor builds",
						"pollution from prod-%", "global warming-"],
	"production+%":		50,
	"prereq build":		"factory",
	"xor builds":		["power plant", "hydro plant", "nuclear plant"],
	"pollution -%":		100,
	"global warming-":	1 #whatever this means...
	},
"harbor": {
	"cost":				60,
	"upkeep":			1,
	"prereq":			"seafaring",
	"effects":			["square+ terrain"],
	"terrain":			"ocean",
	"bonus type":		"food",
	"bonus+":			1
	},
"offshore platform": {
	"cost":				160,
	"upkeep":			3,
	"prereq":			"miniaturization",
	"effects":			["square+ terrain"],
	"terrain":			"ocean",
	"bonus type":		"production",
	"bonus+":			1
	},
"airport": {
	"cost":				160,
	"upkeep":			3,
	"prereq":			"radio",
	"effects":			["new unit mod", "unit heal rate+%"],
	"mod type":			"air",
	"mod effect":		"veteran",
	"heal type":		"air",
	"heal%":			100
	},
"port facility": {
	"cost":				120, #?
	"upkeep":			2,
	"prereq":			"amphibious warfare",
	"effects":			["new unit mod", "unit heal rate+%"],
	"mod type":			"sea",
	"mod effect":		"veteran",
	"heal type":		"sea",
	"heal%":			100
	},
"police station": {
	"cost":				60,
	"upkeep":			2,
	"prereq":			"communism",
	"effects":			["units away unhappy- each"],
	"unhappy-":			1
	},
}

alleffects = {}
for map in DEFAULT_IMPROVEMENTS.values():
	for effect in map["effects"]:
		alleffects[effect] = True
for effect in alleffects:
	print effect

#next wonders, spaceship parts.
DEFAULT_WONDERS = {}