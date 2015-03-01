import pygame
from pygame.locals import *

images = {}

stdLoads = {"obama":"obama.png", "redX":"redx.png", "greenX":"greenx.png", "grassland":"grassland.jpg", "ocean":"ocean.png"}
picDir = "/Users/swordofmorning/Documents/game/pics/"

def load_all():
	for name, loc in stdLoads.items():
		img = pygame.image.load(picDir + loc)
		images[name] = img


def get_image(name):
	return images[name]