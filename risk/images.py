import pygame

########################
###### INIT IMAGES
########################
images = {}
imageNames = {"soldier": "soldier.png"}
def init_images(imgdir, nameDict=imageNames):
	for name in nameDict:
		try:
			images[name] = pygame.image.load(imgdir + nameDict[name])
		except Exception:
			print "Failed loading image " + imgdir + nameDict[name] + ". This image will not display correctly in simulation."

init_images("/Users/swordofmorning/Documents/_programming/bored/pics/")

def get(imgName):
	return images[imgName]