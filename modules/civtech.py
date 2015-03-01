
#args['playertech'] should contain a list of all tech the player has.
def standard_tech_available(self, args):
	if self.data["prereqs"]:
		for prereq in self.data["prereqs"]:
			if prereq not in args["playertech"]:
				return False
	return True

class Tech:
	
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
	
	def long_str(self):
		s = "Tech{\n"
		s += "\tname = " + self.data["name"] + "\n"
		s += "prereqs = ["
		if "prereqs" in self.data:
			for prereq in self.data["prereqs"]:
				s += prereq.get("name") + ", "
			s = s[:-2] + "]\n"
		else:
			s = s[:-1] + "None\n"
		return s
	
	def __str__(self):
		return self.data["name"]
	

DEFAULT_TECH_TREE = [
['Advanced Flight', ['Radio']],
['Alphabet', []],
['Amphibious Warfare', ['Tactics', 'Navigation']],
['Astronomy', ['Mysticism', 'Mathematics']],
['Atomic Theory', ['Theory of Gravity', 'Physics']],
['Automobile', ['Combustion', 'Steel']],
['Banking', ['Trade', 'The Republic']],
['Bridge Building', ['Iron Working', 'Construction']],
['Bronze Working', []],
['Ceremonial Burial', []],
['Chemistry', ['University', 'Medicine']],
['Chivalry', ['Feudalism', 'Horseback Riding']],
['Code of Laws', ['Alphabet']],
['Combined Arms', ['Mobile Warfare', 'Advanced Flight']],
['Combustion', ['Refining', 'Explosives']],
['Communism', ['Industrialization', 'Philosophy']],
['Computers', ['Miniaturization', 'Mass Production']],
['Conscription', ['Democracy', 'Metallurgy']],
['Construction', ['Masonry', 'Currency']],
['Currency', ['Bronze Working']],
['Democracy', ['Invention', 'Banking']],
['Economics', ['Banking', 'University']],
['Electricity', ['Metallurgy', 'Magnetism']],
['Electronics', ['Electricity', 'The Corporation']],
['Engineering', ['The Wheel', 'Construction']],
['Environmentalism', ['Space Flight', 'Recycling']],
['Espionage', ['Communism', 'Democracy']],
['Espionage', ['Communism', 'Democracy']],
['Explosives', ['Gunpowder', 'Chemistry']],
['Feudalism', ['Warrior Code', 'Monarchy']],
['Flight', ['Combustion', 'Explosives']],
['Fundamentalism', ['Monotheism', 'Conscription']],
['Fusion', ['Superconductor', 'Nuclear Power']],
['Future Tech', ['Fusion', 'Recycling']],
['Genetic Engineering', ['The Corporation', 'Medicine']],
['Guerilla Warfare', ['Communism', 'Tactics']],
['Gunpowder', ['Invention', 'Iron Working']],
['Horseback Riding', []],
['Industrialization', ['Railroad', 'Banking']],
['Invention', ['Engineering', 'Literacy']],
['Iron Working', ['Bronze Working']],
['Labor Union', ['Mass Production', 'Guerilla Warfare']],
['Leadership', ['Chivalry', 'Gunpowder']],
['Literacy', ['Writing', 'Code of Laws']],
['Machine Tools', ['Steel', 'Tactics']],
['Magnetism', ['Physics', 'Iron Working']],
['Map Making', ['Alphabet']],
['Masonry', []],
['Mass Production', ['Automobile', 'The Corporation']],
['Mathematics', ['Alphabet', 'Masonry']],
['Medicine', ['Philosophy', 'Trade']],
['Metallurgy', ['University', 'Gunpowder']],
['Miniaturization', ['Machine Tools', 'Electronics']],
['Mobile Warfare', ['Automobile', 'Tactics']],
['Monarchy', ['Code of Laws', 'Ceremonial Burial']],
['Monotheism', ['Philosophy', 'Polytheism']],
['Mysticism', ['Ceremonial Burial']],
['Navigation', ['Seafaring', 'Astronomy']],
['Nuclear Fission', ['Atomic Theory', 'Mass Production']],
['Nuclear Power', ['Nuclear Fission', 'Electronics']],
['Philosophy', ['Mysticism', 'Literacy']],
['Physics', ['Navigation', 'Literacy']],
['Plastics', ['Refining', 'Space Flight']],
['Polytheism', ['Ceremonial Burial']],
['Pottery', []],
['Radio', ['Flight', 'Electricity']],
['Railroad', ['Steam Engine', 'Bridge Building']],
['Recycling', ['Mass Production', 'Democracy']],
['Refining', ['Chemistry', 'The Corporation']],
['Refrigeration', ['Sanitation', 'Electricity']],
['Robotics', ['Computers', 'Mobile Warfare']],
['Rocketry', ['Advanced Flight', 'Electronics']],
['Sanitation', ['Medicine', 'Engineering']],
['Seafaring', ['Map Making', 'Pottery']],
['Space Flight', ['Rocketry', 'Computers']],
['Stealth', ['The Laser', 'Superconductor']],
['Steam Engine', ['Physics', 'Iron Working']],
['Steel', ['Industrialization', 'Electricity']],
['Superconductor', ['The Laser', 'Plastics']],
['Tactics', ['Leadership', 'Conscription']],
['The Corporation', ['Industrialization', 'Economics']],
['The Laser', ['Mass Production', 'Nuclear Power']],
['The Republic', ['Code of Laws', 'Literacy']],
['The Wheel', ['Horseback Riding']],
['Theology', ['Monotheism', 'Feudalism']],
['Theory of Gravity', ['Astronomy', 'University']],
['Trade', ['Currency', 'Code of Laws']],
['University', ['Mathematics', 'Philosophy']],
['Warrior Code', []],
['Writing', ['Alphabet']]
]

#returns list of techs, input is techs + prereqs in str list form (see above)
def init_techs(strlist):
	techs = {}
	for tech, prereqs in strlist:
		techs[tech.lower()] = Tech({"name": tech.lower()})
	for tech, prereqs in strlist:
		if prereqs:
			prereqtechs = []
			for name in prereqs:
				prereqtechs.append(techs[name.lower()])
			techs[tech.lower()].set({"prereqs": prereqtechs})
	return techs

techs = init_techs(DEFAULT_TECH_TREE)

if __name__ == "__main__":
	for tech in techs.values():
		s = tech.get("name") + ": nil"
		if tech.get("prereqs"):
			s = s[:-3] + ": "
			for prereq in tech.get("prereqs"):
				s += prereq.get("name") + ", "
			s = s[:-2]
		print s