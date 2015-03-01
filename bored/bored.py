import pygame, math, sys, random

from pygame.locals import *
pygame.font.init()

BKG_COLOR = (30, 60, 150)
BUFFER = 50
DEFAULT_SIZE = (828, 828)

########################
###### INIT IMAGES
########################
images = {}
imageNames = {"hero": "hero.png", "goblin": "goblin.png", "hit": "crappy_fireball.png"}
def init_images(imgdir, nameDict=imageNames):
	for name in nameDict:
		try:
			images[name] = pygame.image.load(imgdir + nameDict[name])
		except Exception:
			print "Failed loading image " + imgdir + nameDict[name] + ". This image will not display correctly in simulation."

init_images("/Users/swordofmorning/Documents/_programming/bored/pics/")

########################
###### ACTORS
########################

def roll(int):
	return random.randrange(1, int + 1)

class Enemy:
	
	def __init__(self, type, name = None, args = {}):
		self.args = args
		if name:
			self.name = name
		else:
			self.name = type.name
		self.type = type
		self.hplost = 0
		self.beenhit = False
	
	def get_img(self):
		return self.type.get_img(self)
	
	def draw(self, size):
		return self.type.draw(size, actor = self)
	
	def get_attack(self):
		return self.type.meleeskill + max([roll(val) for val in self.type.hitdice])
	
	def get_damage(self):
		dmg = 0
		for die in self.type.dmgdice:
			dmg += roll(die)
		return dmg
	
class EnemyType:
	
	def __init__(self, name, meleeskill, hitdice, dmgdice, hp, img):
		self.name = name
		self.meleeskill = meleeskill
		self.hitdice = hitdice
		self.dmgdice = dmgdice
		self.hp = hp
		self.img = img
		self.hitimg = images["hit"]
		self.hitsize = (.7, .7)
	
	#simple instance; all enemies of a type are identical
	def instantiate(self, name = None):
		if name:
			return Enemy(self, name)
		return Enemy(self)
	
	def get_img(self, actor):
		img = self.img.copy()
		if actor.beenhit:
			size = img.get_size()
			img.blit(pygame.transform.scale(self.hitimg, (int(size[0] * self.hitsize[0]), int(size[1] * self.hitsize[1]))), (int(size[0] * (1 - self.hitsize[0]) / 2), int(size[1] * (1 - self.hitsize[1]) / 2)))
		return img
	
	def draw(self, size, actor):
		return pygame.transform.scale(self.get_img(actor), size)

class Hero:
	
	def __init__(self):
		self.type = self
		self.name = "Hero"
		self.meleeskill = 4
		self.hitdice = [6]
		self.dmgdice = [4, 4]
		self.hp = 30
		self.img = images["hero"]
		self.hitimg = images["hit"]
		self.hitsize = (.7, .7)
		self.beenhit = False
	
	def get_img(self, actor = None):
		img = self.img.copy()
		if self.beenhit:
			size = img.get_size()
			img.blit(pygame.transform.scale(self.hitimg, (int(size[0] * self.hitsize[0]), int(size[1] * self.hitsize[1]))), (int(size[0] * (1 - self.hitsize[0]) / 2), int(size[1] * (1 - self.hitsize[1]) / 2)))
		return img
	
	def draw(self, size):
		return pygame.transform.scale(self.get_img(), size)
	
	def get_attack(self):
		return self.type.meleeskill + max([roll(val) for val in self.type.hitdice])
	
	def get_damage(self):
		dmg = 0
		for die in self.type.dmgdice:
			dmg += roll(die)
		return dmg
	
	#right now each additional enemy just gets += to skill
	def attack(self, enemies):
		i = 0
		for enemy in enemies:
			attack = self.get_attack()
			enemyAttack = enemy.get_attack() + i
			if attack > enemyAttack:
				dmg = 0
				for hit in range(attack - enemyAttack):
					dmg += self.get_damage()
				#print "Hit: " + enemy.name + " took " + str(dmg) + " from " + str(attack - enemyAttack) + " hits!"
				enemy.hplost += dmg
				enemy.beenhit = True
			elif attack < enemyAttack:
				dmg = 0
				for hit in range(enemyAttack - attack):
					dmg += enemy.get_damage()
				#print "Ouch! " + enemy.name + " did " + str(dmg) + " from " + str(enemyAttack - attack) + " hits!"
				self.hp -= dmg
				self.beenhit = True
			i += 1
			if enemy.hplost >= enemy.type.hp:
				pass
				#print enemy.name + " is dead."
			if self.hp <= 0:
				pass
				#print "Hero is dead."
		#print "HP left: " + str(self.hp)

class Grid:
	
	def __init__(self, size):
		self.stuff = []
		for x in range(size[0]):
			self.stuff.append([])
			for y in range(size[1]):
				self.stuff[-1].append([])
		self.units = {}
		self.size = size
	
	def in_grid(self, loc):
		return loc[0] >= 0 and loc[0] < self.size[0] and loc[1] >= 0 and loc[1] < self.size[1]
	
	def add_unit(self, unit, loc):
		if not self.in_grid(loc):
			raise Exception("Out of Grid")
		self.units[unit] = loc
		self.stuff[loc[0]][loc[1]].append(unit)
	
	def remove_unit(self, unit):
		loc = self.units[unit]
		self.stuff[loc[0]][loc[1]].remove(unit)
		del self.units[unit]
	
	def relocate_unit(self, unit, loc):
		if not self.in_grid(loc):
			raise Exception("Out of Grid")
		self.remove_unit(unit)
		self.add_unit(unit, loc)
	
	def new_loc(self, loc, direction):
		if direction == "up":
			return (loc[0], loc[1] - 1)
		elif direction == "down":
			return (loc[0], loc[1] + 1)
		elif direction == "left":
			return (loc[0] - 1, loc[1])
		elif direction == "right":
			return (loc[0] + 1, loc[1])
	
	def move_unit(self, unit, direction):
		loc = self.new_loc(self.units[unit], direction)				
		if not self.in_grid(loc):
			return False
		if self.stuff[loc[0]][loc[1]]:
			return "attack"
		self.relocate_unit(unit, loc)
	
	def dist(self, u1, u2):
		locs = self.units[u1], self.units[u2]
		return math.sqrt((locs[0][0] - locs[1][0]) ** 2 + (locs[0][1] - locs[1][1]) ** 2)
	
grid = Grid((10, 10))
hero = Hero()
goblin = EnemyType("Goblin", 3, [5], [3], 10, images["goblin"])

grid.add_unit(hero, (4, 5))
grid.add_unit(goblin.instantiate(), (2, 2))

def display(screen, grid=grid, bkg=BKG_COLOR):
	screenSize = screen.get_size()
	squareSize = ((screenSize[0] - BUFFER) / grid.size[0], (screenSize[1] -  BUFFER) / grid.size[1])
	screen.fill(bkg)
	for unit, loc in grid.units.items():
		screen.blit(unit.draw(squareSize), (BUFFER + loc[0] * squareSize[0], BUFFER + loc[1] * squareSize[1]))

if __name__ == "__main__":
	
	pygame.init()
	screen = pygame.display.set_mode(DEFAULT_SIZE, DOUBLEBUF | RESIZABLE)
	update = True

	while 1:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == K_ESCAPE:
					sys.exit(0)
				if event.key == K_DOWN:
					hero.beenhit = False
					for creature in grid.units:
						creature.beenhit = False
					if grid.move_unit(hero, "down") == "attack":
						loc = grid.new_loc(grid.units[hero], "down")
						hero.attack(grid.stuff[loc[0]][loc[1]])
					update = True
				if event.key == K_UP:		
					grid.move_unit(hero, "up")
					update = True
					hero.beenhit = False
					for creature in grid.units:
						creature.beenhit = False
				if event.key == K_LEFT:		
					grid.move_unit(hero, "left")
					update = True
					hero.beenhit = False
					for creature in grid.units:
						creature.beenhit = False
				if event.key == K_RIGHT:		
					grid.move_unit(hero, "right")
					update = True
					hero.beenhit = False
					for creature in grid.units:
						creature.beenhit = False
		if update:
			display(screen)
			pygame.display.flip()