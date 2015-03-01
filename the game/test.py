import os, images, pygame
from pygame.locals import *

images.init("./images")
pygame.init()

screen = pygame.display.set_mode((500, 500), DOUBLEBUF | RESIZABLE)
screen.fill((255, 255, 255))

print screen.get_at((0, 0))

img = images.get("soldier")
img = img.convert()
images.whiteWash(img)
img.set_colorkey(img.get_at((0, 0)))

print img.get_colorkey(), "oy"
print screen.get_colorkey(), "yey"

screen.blit(img, (0, 0))
pygame.display.flip()



while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	pygame.display.flip()