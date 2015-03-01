from Tkinter import *
import tkMessageBox
import Image, ImageTk

def callback():
    if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
        root.destroy()

images = {}
imageNames = {"brick house": "brickhouse.png", "brick house nr": "brickhousenoroof.png", "wood house": "woodhouse.png", "wood house nr": "woodhousenoroof.png", "foundation": "foundation.png", "emptp lot": "emptylot.png"}
def init_images(imgdir, nameDict=imageNames):
	for name in nameDict:
		try:
			images[name] = ImageTk.PhotoImage(Image.open(imgdir + nameDict[name]))
		except Exception:
			print "Failed loading image " + imgdir + nameDict[name] + ". This image will not display correctly in simulation."

class Lot:

    def __init__(self, master, row, column, width, height):

        self.frame = Frame(master, width=width, height=height)
       	self.house = Label(master)
       	self.frame.grid(row=row, column=column)
       	self.house.pack(side = BOTTOM)

    def set_house_pic(self, image):
        self.house.configure(image = image)


root = Tk()
root.protocol("WM_DELETE_WINDOW", callback)

init_images("/Users/swordofmorning/Desktop/")
#print images

lot1 = Lot(root, 0, 0, 300, 200)
print images["brick house"]
lot1.set_house_pic(images["brick house"])

root.mainloop()