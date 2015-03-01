import pygame, sys, pickle, gui, map2, gamedata, random
from pygame.locals import *

MODE_FILL = 0
MODE_BORDER = 1
MODE_CENTER = 2
selectedterr = None
selectedcont = None

def create_terr_buttons(info, continent, labels, buttons):
	info.add(gui.Label("Territories"), (140, 300))
	for button in buttons["Territories"]:
		info.remove(button)
	buttons["Territories"] = []
	i = 1
	height = 30
	for terr in continent.territories.values():
		button = gui.Button(terr.name)
		button.terr = terr
		info.add(button, (140, 300 + height * i))
		buttons["Territories"].append(button)
		i += 1
	label = gui.Label("Selected: None")
	if "Terr" in labels:
		info.remove(labels["Terr"])
	labels["Terr"] = label
	info.add(label, (140, 300 + height * i))
		

def create_cont_buttons(info, labels):
	info.add(gui.Label("Continents"), (10, 300))
	i = 1
	height = 30
	for cont in gamedata.CONTINENTS:
		button = gui.Button(cont.name)
		button.cont = cont
		info.add(button, (10, 300 + height * i))
		i += 1
	label = gui.Label("Selected: None")
	labels["Cont"] = label
	info.add(label, (10, 300 + height * i))

def select_cont(info, cont, labels, buttons):
	labels["Cont"].text = "Selected: " + cont.name
	create_terr_buttons(info, cont, labels, buttons)
	selectedcont = cont

def init_mapdraw_gui(info, labels, buttons):
	info.add(gui.Button("Border"), (30, 50))
	info.add(gui.Button("Fill"), (120, 50))
	info.add(gui.Button("Trim"), (190, 50))
	info.add(gui.Button("Clear"), (60, 120))
	info.add(gui.Button("Place Center"), (130, 120))
	ocean = gui.Button("Fill Ocean")
	ocean.terr = "ocean"
	info.add(ocean, (25, 230))
	info.add(gui.Button("Add Neighbors"), (100, 230))
	labels["Mode"] = gui.Label("Mode: Border")
	info.add(labels["Mode"], (80, 170))
	create_cont_buttons(info, labels)
	cont = random.choice(gamedata.CONTINENTS.keys())
	select_cont(info, cont, labels, buttons)
	
def init_world(world):
	world.add_terr("border", (0, 0, 0))
	for terr in gamedata.territories:
		world.add_terr(terr, gamedata.territories[terr])



	
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
gamedata.add_territories()
world = map2.Map((768, 768))
init_world(world)

info = gui.GUI((1024 - 768, 768), (0, 200, 30))
labels = {}
buttons = {"Territories": []}
init_mapdraw_gui(info, labels, buttons)
infoloc = (768, 0)
screen.blit(world.pixels, (0, 0))
screen.blit(info.draw(), infoloc)
pygame.display.flip()
changed = False
infochanged = False
lastclick = [None, None, None]
mode = MODE_BORDER

while 1:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit(0)
		elif event.type == pygame.MOUSEMOTION:
			if world.in_map(event.pos):
				if event.buttons[0] and lastclick[0] and mode == MODE_BORDER:
					map2.draw_line(world, "border", event.pos, (event.pos[0] - lastclick[0][0], event.pos[1] - lastclick[0][1]))
					lastclick[0] = event.pos
					changed = True
			else:
				pass #nothing to do in gui
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if world.in_map(event.pos):
				if event.button == 1 and mode == MODE_FILL:
					world.fill(event.pos, selectedterr)
					changed = True
				lastclick[event.button - 1] = event.pos
			else:
				button = info.click(event.button, (event.pos[0] - infoloc[0], event.pos[1] - infoloc[1]))
				if button:
					if button.text == "Border":
						mode = MODE_BORDER
						labels["Mode"].text = "Mode: " + button.text
						infochanged = True
					elif button.text == "Fill":
						mode = MODE_FILL
						labels["Mode"].text = "Mode: " + button.text
						infochanged = True
					elif button.text == "Place Center":
						mode = MODE_CENTER
						labels["Mode"].text = "Mode: " + button.text
						infochanged = True
					elif button.text == "Clear":
						world = map2.Map((768, 768))
						init_world(world)
						changed = True
					elif button.text == "Trim":
						world.trim()
						changed = True
					elif button.text == "Add Neighbors":
						world.add_neighbors()
						for terr in gamedata.territories:	
							s = terr.name + ": "
							for neighbor in terr.neighbors:
								s += neighbor.name + ", "
							print s[:-2]
					elif hasattr(button, "cont"):
						select_cont(info, button.cont, labels, buttons)
						infochanged = True
					elif hasattr(button, "terr"):
						selectedterr = button.terr
						if selectedterr != "ocean":
							labels["Terr"].text = "Selected: " + button.terr.name
						else:
							labels["Terr"].text = "Selected: ocean"
						infochanged = True

	if infochanged:
		screen.blit(info.draw(), infoloc)
		infochanged = False
		if not changed:
			pygame.display.flip()
	if changed:
		screen.blit(world.pixels, (0, 0))
		pygame.display.flip()
		changed = False

selectedstate = 
while 1:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit(0)
				