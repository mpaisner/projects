import os, sys
import pygame
from pygame.locals import *

def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('sounds', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound
	
class UnitDisplay(pygame.sprite.DirtySprite):
	
	animationTime = 1.0
	
	def __init__(self, unit, attackAnimation = None, deathAnimation = None):
		self.unit = unit
		self.img = unit.img #base image
		self.image = unit.img #image used by pygame; changed during animation
		self.rect = self.image.get_rect()
		self.attackAnimation = attackAnimation
		self.deathAnimation = deathAnimation
		self.dying = False
		self.attacking = False
	
	def attack(self):
		if self.attackAnimation:
			self.attacking = self.animationTime
	
	def die(self):
		if self.deathAnimation:
			self.dying = self.animationTime
		else:
			self.visible = False
			self.dirty = 1
	
	def remove(self, *groups):
		for group in groups:
			if self.unit in group:
				del group[self.unit]
	
	def update(self, dt):
		if self.dying:
			self.dirty = 1
			self.dying -= dt
			if self.dying <= 0:
				self.visible = 0
				self.dying = False
			else:
				self.image = self.deathAnimation[int((1 - self.dying / self.animationTime) * len(self.deathAnimation))] 
		elif self.attacking:
			self.dirty = 1
			self.attacking -= dt
			if self.attacking <= 0:
				self.image = self.img
				self.attacking = False
			else:
				self.image = self.attackAnimation[int((1 - self.attacking / self.animationTime) * len(self.attackAnimation))] 
	
class Battlefield:
	
	bkgColor = (0, 200, 80)
	
	def __init__(self, size, attackers, defenders):
		self.bkg = pygame.Surface(size)
		self.bkg.fill(self.bkgColor)
		self.attackers = {attacker: UnitDisplay(attacker) for attacker in attackers}
		self.defenders = {defender: UnitDisplay(defender) for defender in defenders}
	
	
		
		
	def placeUnits(self, size, unitSize):
		maxColumns = size[0] / unitSize[0] / 2
		maxRows = size[1] / unitSize[1]
		