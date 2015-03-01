from Tkinter import *


class DraggableLabel(Label):
	
	def __init__(self, master, loc, **options):
		Label.__init__(self, master, options)
		self.place(x = loc[0], y = loc[1])
		self.loc = loc
	
	def StopMove(self, event):
		self.destroy()
	
	def OnMotion(self, event):
		deltax = event.x - self.loc[0]
		deltay = event.y - self.loc[1]
		x = self.winfo_x() + deltax
		y = self.winfo_y() + deltay
		self.loc  = (x, y)
		self.geometry("+%s+%s" % (x, y))

class DraggableMenu(OptionMenu):
	
	def __init__(self, master, variable, *values):
		OptionMenu.__init__(self, master, variable, *values)
		self.dragging = False
		self.variable = variable
		#self.bind("<ButtonPress-1>", self.click)
		#self["menu"].bind("<ButtonPress-1>", self.click)
		#self.bind("<ButtonRelease-1>", self.stopDrag)
		#self.bind("<B1-Motion>", self.onMotion)
	
	def click(self, event):
		print self.get()
		
	def stopDrag(self, event):
		pass
	
	def add_option(self, option):
		pass
	
	def get(self):
		return variable.get()
	

# the constructor syntax is:
# OptionMenu(master, variable, *values)

OPTIONS = [
    "egg",
    "bunny",
    "chicken"
]

master = Tk()

variable = StringVar(master)
variable.set(OPTIONS[0]) # default value

w = DraggableMenu(master, variable, *OPTIONS)
w.pack()

master.bind("<ButtonPress-1>", w.click)

master.mainloop()