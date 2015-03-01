import territory

territories = {}

CONTINENTS = {territory.Continent("South America", 2, (50, 190, 25), (30, 60, 20)): ["Brazil", "Peru", "Argentina", "Venezuela"], territory.Continent("North America", 5, (170, 80, 45), (50, 50, 25)): ["Eastern US", "Western US", "Alaska", "Central America", "Alberta", "Quebec", "Ontario", "Northwest Territory", "Greenland"], territory.Continent("Europe", 5, (45, 35, 160), (40, 20, 30)): ["Iceland", "Northern Europe", "Southern Europe", "Western Europe", "Ukraine", "Scandinavia", "Great Britain"], territory.Continent("Africa", 3, (190, 50, 90), (35, 35, 40)): ["North Africa", "South Africa", "Congo", "East Africa", "Egypt", "Madagascar"], territory.Continent("Asia", 2, (25, 180, 150), (15, 60, 50)): ["Siam", "China", "India", "Mongolia", "Irkutsk", "Yakutsk", "Kamchatka", "Japan", "Siberia", "Ural", "Afghanistan", "Middle East"], territory.Continent("Australia", 2, (150, 10, 150), (30, 5, 30)): ["Western Australia", "Eastern Australia", "Indonesia", "New Guinea"]}

def add_territories():
	for continent in CONTINENTS:
		for terrname in CONTINENTS[continent]:
			terr = territory.Territory(terrname)
			continent.add_territory(terr)
			territories[terr] = continent.get_new_color()

def load_conts(savedmap):
	pass