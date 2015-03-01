import pygame, sys, random, territory, pickle, gameinfo, map
from pygame.locals import *

MODE_BORDER = 0
MODE_FILL = 1
MODE_EDIT_CONT = 2
MODE_PLACE_CENTER = 3

MAX_CONTINENTS = 8
MAX_TERRITORIES = 15

CONTINENTS = {territory.Continent("South America", 2, (50, 190, 25), (30, 60, 20)): ["Brazil", "Peru", "Argentina", "Venezuela"], territory.Continent("North America", 5, (170, 80, 45), (50, 50, 25)): ["Eastern US", "Western US", "Alaska", "Central America", "Alberta", "Quebec", "Ontario", "Northwest Territory", "Greenland"], territory.Continent("Europe", 5, (45, 35, 160), (40, 20, 30)): ["Iceland", "Northern Europe", "Southern Europe", "Western Europe", "Ukraine", "Scandinavia", "Great Britain"], territory.Continent("Africa", 3, (190, 50, 90), (35, 35, 40)): ["North Africa", "South Africa", "Congo", "East Africa", "Egypt", "Madagascar"], territory.Continent("Asia", 2, (25, 180, 150), (15, 60, 50)): ["Siam", "China", "India", "Mongolia", "Irkutsk", "Yakutsk", "Kamchatka", "Japan", "Siberia", "Ural", "Afghanistan", "Middle East"], territory.Continent("Australia", 2, (150, 10, 150), (30, 5, 30)): ["Western Australia", "Eastern Australia", "Indonesia", "New Guinea"]}

BORDERS = {"North Africa": ["Brazil," "Western Europe", "Southern Europe"], "Greenland": ["Quebec", "Ontario", "Northwest Territory", "Iceland"], "Great Britain": ["Western Europe", "Northern Europe", "Scandinavia", "Iceland"], "Scandinavia": ["Iceland"], "Egypt": ["Southern Europe"], "East Africa": ["Middle East"], "Madagascar": ["South Africa", "East Africa"], "Kamchatka": ["Alaska", "Japan"], "Mongolia": ["Japan"], "Indonesia": ["Siam", "Western Australia", "New Guinea"], "New Guinea": ["Eastern Australia", "Western Australia"]}

pygame.init()
pygame.font.init()
scrollcoords = (0, 0)
mapsize = (700, 768)
maprect = pygame.Rect((0, 0), mapsize)
screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
mapfile = open("map", "r")
world = pickle.load(mapfile)
#world = map.Map(200, 200)
info = gameinfo.InfoArea(324, 768)
info.draw_default()
player = territory.Player((255, 0, 0))
for cont in CONTINENTS:
	info.add_continent(cont)
	for terrname in CONTINENTS[cont]:
		terr = territory.Territory(terrname, cont.get_new_color())
		terr.player = player
		world.add_territory(terr)
		info.add_territory(cont, terr)

changed = True
infochanged = True
mode = -1

while 1:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE: 
				file = open("map", "w+")
				pickle.dump(world, file)
				#file = open("info", "w+")
				#pickle.dump(info, file)
				sys.exit(0)
			elif event.key == K_r:
				world.remove_useless_borders()
				changed = True
			elif event.key == K_s:
				file = open("newfile", "w+")
				pickle.dump(world, file)
				#file = open("info", "w+")
				#pickle.dump(info, file)
			elif event.key == K_p:
				print world.gen_neighbor_pairs()
		elif event.type == pygame.MOUSEMOTION:
			if event.buttons[0] == 1:
				pos = (event.pos[0] + scrollcoords[0], event.pos[1] + scrollcoords[1])
				if mode == MODE_BORDER and maprect.collidepoint(event.pos):		
					world.add_border(((pos[0] - event.rel[0]) / world.squaresize, (pos[1] - event.rel[1]) / world.squaresize), (pos[0] / world.squaresize, pos[1] / world.squaresize))
				elif mode == MODE_FILL and maprect.collidepoint(event.pos):
					if info.currentTerr:
						world.fill_column(pos[0] / world.squaresize, pos[1] / world.squaresize, info.currentTerr)
					else:
						world.fill_column(pos[0] / world.squaresize, pos[1] / world.squaresize, "ocean")
				changed = True
			elif event.buttons[2] == 1: #right button
				scrollcoords = (max(0, min(world.width * world.squaresize - mapsize[0], scrollcoords[0] + event.rel[0])), max(0, min(world.height * world.squaresize - mapsize[1], scrollcoords[1] + event.rel[1])))
				changed = True
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.pos[0] > mapsize[0]: #info area
				button = info.get_button(event.pos[0] - mapsize[0], event.pos[1])
				if button == None:
					pass
				elif button == "Draw Borders":
					mode = MODE_BORDER
					info.set_mode("Draw Borders")
					infochanged = True
				elif button == "Fill":
					mode = MODE_FILL
					info.set_mode("Fill")
					infochanged = True
				elif button == "Trim":
					world.remove_useless_borders()
					changed = True
				elif button == "Clear":
					world = map.Map(200, 200)
					changed = True
				elif button == "Place Centers":
					mode = MODE_PLACE_CENTER
					info.set_mode("Place Centers")
					infochanged = True
				elif info.is_continent(button):
					info.set_continent(button)
					infochanged = True
				elif info.is_territory(info.currentCont, button):
					info.set_territory(info.currentCont, button)
					infochanged = True
			elif maprect.collidepoint(event.pos): #map
				pos = (event.pos[0] + scrollcoords[0], event.pos[1] + scrollcoords[1])
				if mode == MODE_PLACE_CENTER:
					world.set_center(pos[0] / world.squaresize, pos[1] / world.squaresize)
	if changed:
		screen.blit(world.draw_noarg(), (-scrollcoords[0], -scrollcoords[1]))
		screen.blit(info.draw(), (mapsize[0], 0))
		pygame.display.flip()
		changed = False
		infochanged = False
	elif infochanged:
		screen.blit(info.draw(), (mapsize[0], 0))
		pygame.display.flip()
		infochanged = False