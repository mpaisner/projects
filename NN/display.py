import pygame
from pygame.locals import *

pygame.init()
pygame.display.quit()

BUFFER = 20
SCREEN_SIZE = (1024, 840)

def add_pic(surface, pixels, width, start = (0, 0), zoom = 100):
	n = 0
	surf = pygame.Surface((width * zoom, zoom * len(pixels) / width))
	for pixel in pixels:
		surf.fill((255 * pixel, 255 * pixel, 255 * pixel), pygame.Rect((n % width * zoom, n / width * zoom), (zoom, zoom)))
		n += 1
	surface.blit(surf, start)

#can only display same-sized pictures
def display_pics(pixels, width, zoom):	
	pygame.display.init()
	screen = pygame.display.set_mode(SCREEN_SIZE)
	screen.fill((0, 0, 255))
	loc = (BUFFER, BUFFER)
	for pixset in pixels:
		add_pic(screen, pixset, width, loc, zoom)
		loc = (loc[0] + zoom * width + BUFFER, loc[1])
		if loc[0] + zoom * width >= SCREEN_SIZE[0]:
			loc = (BUFFER, loc[1] + BUFFER + len(pixset) / width * zoom)
	pygame.display.flip()
	quit = False
	while not quit:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.display.quit()
					quit = True

