import pygame, math, sys, random, world, pics
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
fpsClock = pygame.time.Clock()

#constants
MAXSCROLL = 50
MINSCROLL = 5
SCROLLSLOW = 2

#init:
pics.load_all()
theWorld = world.World(world.BaseMapGen())
mapTop = 0
mapLeft = 0
rightScroll = 0
downScroll = 0

#main loop
while 1:
	
	deltat = fpsClock.tick(30)
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE: 
				sys.exit(0)
			elif event.key == K_UP: 
				downScroll = max(-MAXSCROLL, downScroll - 15)
			elif event.key == K_DOWN: 
				downScroll = min(MAXSCROLL, downScroll + 15)
			elif event.key == K_RIGHT: 
				rightScroll = min(MAXSCROLL, rightScroll + 15)
			elif event.key == K_LEFT: 
				rightScroll = max(-MAXSCROLL, rightScroll - 15)
		elif event.type == pygame.MOUSEMOTION:
			pass
	
	mapTop += (downScroll * deltat / 30)
	mapTop = min(theWorld.image.get_height() - screen.get_height(), max(0, mapTop))
	mapLeft += (rightScroll * deltat / 30)
	mapLeft = min(theWorld.image.get_width() - screen.get_width(), max(0, mapLeft))
	
	#slow scrolling
	if abs(downScroll) < MINSCROLL: downScroll = 0
	elif downScroll < 0: downScroll += SCROLLSLOW * deltat / 30
	else: downScroll -= SCROLLSLOW * deltat / 30
	if abs(rightScroll) < MINSCROLL: rightScroll = 0
	elif rightScroll < 0: rightScroll += SCROLLSLOW * deltat / 30
	else: rightScroll -= SCROLLSLOW * deltat / 30
	
	
	screen.blit(theWorld.image, (-mapLeft, -mapTop))
	pygame.display.flip()