import pygame, math, sys
sys.path.append("/Users/swordofmorning/documents/_programming/problem_generator/houses/")
sys.path.append("/Users/swordofmorning/documents/_programming/modules/")
import simulator, planner, gui
from pygame.locals import *

pygame.font.init()

from Tkinter import Tk
from tkFileDialog import askopenfilename
Tk().withdraw()

LOT_MIN_SIZE = (100, 100)
LOT_MAX_SIZE = (900, 900)
LOT_SPACE = 20
MAX_LOTS = 20
BKG_COLOR = (30, 60, 150)
INFO_BKG_COLOR = (100, 100, 50)
aspRatio = 1024.0/768

DEFAULT_SIZE = (1024, 568)

INFO_WIDTH = 250
INFO_TXT_BUFFER = 20
BUFFER = (100, 100)

images = {}
imageNames = {"brick house": "brickhouse.png", "brick house nr": "brickhousenoroof.png", "wood house": "woodhouse.png", "wood house nr": "woodhousenoroof.png", "foundation": "foundation.png", "empty lot": "emptylot.png", "fire": "fire.png", "hq building": "hqbuilding.png", "hq logo": "hq.png", "fireman": "firemanhose.png", "teamster": "teamster.png", "construction worker": "constructionworker.png"}
def init_images(imgdir, nameDict=imageNames):
	for name in nameDict:
		try:
			images[name] = pygame.image.load(imgdir + nameDict[name])
		except Exception:
			print "Failed loading image " + imgdir + nameDict[name] + ". This image will not display correctly in simulation."

init_images("/Users/swordofmorning/Documents/programming/visualizer/images/")

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = Rect(rect)
    y = rect.top
    lineSpacing = -2
 
    # get the height of the font
    fontHeight = font.size("Tg")[1]
 
    while text:
        i = 1
 
        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break
 
        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1
 
        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1
 
        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)
 
        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing
 
        # remove the text we just blitted
        text = text[i:]
 
    return text

class PlanVis:
	
	def __init__(self):
		self.plan = None
		self.world = None
		self.font = pygame.font.Font(None, 20)
		self.status = None
		self.nextStep = 0
		self.worlds = []
	
	def draw(self, size, bkg = INFO_BKG_COLOR):
		surf = pygame.Surface(size)
		surf.fill(bkg)
		if not self.plan:
			if self.world:
				if status == "no goals":
					msg = "No goals present in file loaded"
				elif status == "planning failed":
					msg = "Planner failed to generate a plan"
				else:
					msg = "Press enter to generate a plan"
			else:
				msg = "Press spacebar to load a problem file"
			drawText(surf, msg, (0, 0, 0), pygame.Rect(INFO_TXT_BUFFER, INFO_TXT_BUFFER, size[0] - 2 * INFO_TXT_BUFFER, size[1] - 2 * INFO_TXT_BUFFER), self.font)
		else:
			planLines = planner.prodigy_str(self.plan).split("\n")
			i = 0
			for line in planLines:
				if not line or line[0] != "<":
					continue
				color = (0, 0, 0)
				if i == self.nextStep:
					color = (0, 255, 0)
				txt = self.font.render(line, True, color)
				surf.blit(txt, (INFO_TXT_BUFFER, INFO_TXT_BUFFER + self.font.size(line)[1] * i))
				i += 1
		return surf
		
	def load_plan(self, world):
		self.world = world
		self.worlds.append(world)
		world = world.deep_copy()
		if not world.goals:
			self.status = "no goals"
			return []
		try:
			plan = planner.gen_plan(world)
		except Exception:
			self.status = "planning failed"
			print Exception
			return []	
		world = self.world.deep_copy()
		try:
			for step in plan:
				world.execute_action(step)
				self.worlds.append(world)
				world = world.deep_copy()
		except Exception:
			self.status = "planning failed"
			print Exception
			return []	
		self.plan = plan

class Lot:
	
	def __init__(self, house, world):
		self.house = house
		self.world = world
	
	def get_house_image(self):
		image = images["empty lot"]
		if self.house.type == "HQ":
			image = images["hq building"]
			width, height = image.get_size()
			image.blit(pygame.transform.scale(images["hq logo"], (width, 3 * height / 8)), (0, 0))
		elif self.house.roof:
			if self.house.walls == "WOOD":
				image = images["wood house"]
			else:
				image = images["brick house"]
		elif self.house.walls == "WOOD":
			image = images["wood house nr"]
		elif self.house.walls == "BRICK":
			image = images["brick house nr"]
		elif self.house.foundation:
			image = images["foundation"]	
		if self.house.fire:
			width, height = image.get_size()
			image.blit(pygame.transform.scale(images["fire"], (width / 2, height / 2)), (width / 4, height / 4))
		#add fire at end
		return image
	
	def get_worker_image(self, worker):
		if worker.type == "FIREMAN":
			return images["fireman"]
		elif worker.type == "TEAMSTER":
			return images["teamster"]
		else:
			return images["construction worker"]
	
	#(firemen, teamsters, construction workers)
	def get_num_workers(self):
		num = [0, 0, 0]
		for worker in self.world.workers.values():
			if worker.loc == self.house:
				if worker.type == "FIREMAN":
					num[0] += 1
				elif worker.type == "TEAMSTER":
					num[1] += 1
				else:
					num[2] += 1
		return num
	
	def draw(self, size, bkg = BKG_COLOR):
		surf = pygame.Surface(size)
		surf.fill(bkg)
		houseSize = (int(size[0] * 0.6), int(size[1] * 0.7))
		workerSize = (int((size[0] - houseSize[0]) / 2.6), int(size[1] * 0.4))
		picture = pygame.transform.scale(self.get_house_image(), houseSize)
		surf.blit(picture, (size[0] - houseSize[0], (size[1] - houseSize[1]) / 2))
		font = pygame.font.Font(None, 20)
		numWorkers = self.get_num_workers()
		filledSlots = 0
		if numWorkers[0] > 0:
			surf.blit(pygame.transform.scale(images["fireman"], workerSize), (size[0] - houseSize[0] - (workerSize[0] - 15) * (1 + filledSlots), size[1] * 0.3))
			#number of this type
			surf.blit(font.render(str(numWorkers[0]), True, (0, 0, 0)), (size[0] - houseSize[0] - (workerSize[0] - 15) * (0.5 + filledSlots), size[1] * 0.3 + workerSize[1]))
			filledSlots += 1
		if numWorkers[1] > 0:
			surf.blit(pygame.transform.scale(images["teamster"], workerSize), (size[0] - houseSize[0] - (workerSize[0] - 15) * (1 + filledSlots), size[1] * 0.3))
			#number of this type
			surf.blit(font.render(str(numWorkers[1]), True, (0, 0, 0)), (size[0] - houseSize[0] - (workerSize[0] - 15) * (0.5 + filledSlots), size[1] * 0.3 + workerSize[1]))
			filledSlots += 1
		if numWorkers[2] > 0:
			surf.blit(pygame.transform.scale(images["construction worker"], workerSize), (size[0] - houseSize[0] - (workerSize[0] - 15) * (1 + filledSlots), size[1] * 0.3))
			#number of this type
			surf.blit(font.render(str(numWorkers[2]), True, (0, 0, 0)), (size[0] - houseSize[0] - (workerSize[0] - 15) * (0.5 + filledSlots), size[1] * 0.3 + workerSize[1]))
			filledSlots += 1
		return surf

def get_rows_cols(numlots):
	if numlots == 0:
		return (0, 0)
	#cols = math.ceil(math.sqrt(numlots))
	#if (cols - 1) * cols >= numlots:
	#	return int(cols - 1), int(cols)
	#return int(cols), int(cols)
	rows = math.floor(math.sqrt(numlots) * 2)
	cols = math.ceil(numlots * 1.0 / rows)
	while (rows - 1) * cols >= numlots:
		rows -= 1
	return int(rows), int(cols)
	

lots = {}
info = PlanVis()

def sorted_lots(lots):
	if lots:
		keys = lots.keys()
		keys.sort(key=lambda x: x.house.name)
		return keys
	return []

def get_lot_size(num, screenSize):
	rows, cols = get_rows_cols(num)
	if rows == 0 or cols == 0:
		return (0, 0)
	screenSize = (screenSize[0] - 50, screenSize[1] - 50) #buffer
	preferredWidth = screenSize[0] / cols - LOT_SPACE
	preferredHeight = screenSize[1] / rows - LOT_SPACE
	return (min(LOT_MAX_SIZE[0], max(LOT_MIN_SIZE[0], preferredWidth)), min(LOT_MAX_SIZE[1], max(LOT_MIN_SIZE[1], preferredHeight)))

def assign_houses(world):
	lots.clear()
	rows, cols = get_rows_cols(len(world.locations))
	i = 0
	houses = sorted(world.locations.values(), key = lambda x: x.name)
	for y in range(rows):
		for x in range(cols):
			if i >= len(houses):
				break
			lots[Lot(houses[i], world)] = (x, y)
			i += 1

def load_state_file(path):
	f = open(path, "r")
	text = f.read()
	objects, state = simulator.parse_state(text)
	world = simulator.HouseWorld(objects, state)
	world.goals = simulator.parse_goals(text)
	info.load_plan(world)
	assign_houses(world)
	update = True

def display(screen, lots=lots, info=info, bkg=BKG_COLOR):
	screenSize = screen.get_size()
	lotSize = get_lot_size(len(lots), (screenSize[0] - INFO_WIDTH - BUFFER[0], screenSize[1] - BUFFER[1]))
	screen.fill(bkg)
	for lot in sorted_lots(lots):
		screen.blit(lot.draw(lotSize), (lots[lot][0] * (lotSize[0] + LOT_SPACE), lots[lot][1] * (lotSize[1] + LOT_SPACE)))
	screen.blit(info.draw((INFO_WIDTH, screenSize[1])), (screenSize[0] - INFO_WIDTH, 0))

	
pygame.init()
screen = pygame.display.set_mode(DEFAULT_SIZE, DOUBLEBUF | RESIZABLE)
display(screen)
update = True
while 1:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE:
				sys.exit(0)
			if event.key == K_SPACE:
				filename = askopenfilename()
				load_state_file(filename)
			if event.key == K_DOWN:		
				if info and info.worlds:
					info.nextStep = min(len(info.worlds) - 1, info.nextStep + 1)
					world = info.worlds[info.nextStep]
					assign_houses(world)
					update = True
			if event.key == K_UP:		
				if info and info.worlds:
					info.nextStep = max(0, info.nextStep - 1)
					world = info.worlds[info.nextStep]
					assign_houses(world)
					update = True
	assign_houses
	if update:
		display(screen)
		pygame.display.flip()