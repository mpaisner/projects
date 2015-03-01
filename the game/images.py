from pygame import image
import os

########################
###### INIT IMAGES
########################
images = {}
def init(imgdir):
	nameDict = {}
	for path,dirs,files in os.walk(imgdir):
		for fn in files:
			if ".jpg" in fn:
				nameDict[fn[:fn.index(".")]] = os.path.join(path,fn)
	
	for name, path in nameDict.items():
		try:
			img = image.load(path)
			#whiteWash(img)
			images[name] = img
		except Exception:
			print "Failed loading image " + imgdir + path + ". This image will not display correctly in simulation."

def get(imgName):
	return images[imgName]

def surroundingWhite(img, loc):
	for x in range(-1,2):
		for y in range(-1, 2):
			loc2 = (loc[0] + x, loc[1] + y)
			if min(loc2) >= 0 and loc2[0] < img.get_width() and loc2[1] < img.get_height():
				if img.get_at(loc2) == (255, 255, 255):
					return True
	return False

def whiteWash(img):
	done = False
	while not done:
		done = True
		for x in range(img.get_width()):
			for y in range(img.get_height()):
				color = img.get_at((x, y))
				if color[0] + color[1] + color[2] > 590 and color[0] + color[1] + color[2] < 765:
					if surroundingWhite(img, (x, y)):
						done = False
						img.set_at((x, y), (255, 255, 255))