from Tkinter import *
import re

def parsegeometry(geometry):
    m = re.match("(\d+)x(\d+)([-+]\d+)([-+]\d+)", geometry)
    if not m:
        raise ValueError("failed to parse geometry string")
    return map(int, m.groups())

def contains(widget, event):
	return event.widget.winfo_x() + event.x >= widget.winfo_x() and event.widget.winfo_x() + event.x < widget.winfo_x() + widget.winfo_width() and event.widget.winfo_y() + event.y >= widget.winfo_y() and event.widget.winfo_y() + event.y < widget.winfo_y() + widget.winfo_height()

BOOLEAN = 0
SYMBOL = 1
NUM = 2

class Attribute:
	
	def __init__(self, name, type):
		self.name = name
		self.type = type
	
	def __str__(self):
		return self.name

class ScrollableOptions(Frame):
	
	def __init__(self, master, options, mode = SINGLE, **args):
		Frame.__init__(self, master, **args)
		self.master = master
		self.optionList = Listbox(self, selectmode = mode)
		for option in options:
			self.optionList.insert(END, option)
		self.optionList.configure(height = 10)
		self.scrollBar = Scrollbar(self, command = self.optionList.yview)
		self.optionList['yscrollcommand'] = self.scrollBar.set
		
		self.optionList.grid(row = 0, column = 0, sticky="nsew", padx=2, pady=2)
		self.scrollBar.grid(row = 0, column = 1, sticky='nsew')
		
		self.optionList.bind("<ButtonPress-1>", self.click)
		self.optionList.bind("<ButtonRelease-1>", self.released)
		self.optionList.bind("<B1-Motion>", self.motion)
		self.dragging = None
		self.dragDestinations = []
	
	def eventInList(self, event):
		return contains(self.optionList, event)
	
	def dispatchDrop(self, event, droppedItem):
		for dest in self.dragDestinations:
			if contains(dest, event):
				if hasattr(dest, "receiveDrop"):
					dest.receiveDrop(self, droppedItem, event)
	
	def released(self, event):
		if self.eventInList(event): #release takes place inside option list
			#resort if dragging
			if self.dragging:
				index = self.optionList.nearest(event.y - self.dragging.winfo_height() / 2) + 1
				self.optionList.insert(index, self.dragging.name)
				if self.dragging.index > index: 
					#insert will have offset old index - correct
					self.dragging.index += 1
				print self.optionList.curselection(), self.dragging.index
				if str(self.dragging.index) in self.optionList.curselection():
					self.optionList.selection_set(index)
				self.optionList.delete(self.dragging.index)
		
		if self.dragging:
			self.dragging.destroy()
		self.dragging = None
	
	def motion(self, event):
		index = self.optionList.nearest(event.y)
		selection = self.optionList.get(index)
		if not self.dragging:
			self.dragging = FloatingWindow(index, selection, event.x, event.y)
			#toggle selection (so dragging does not change selection)
			#only for multiple selection method
			if self.optionList.cget("selectmode") in [MULTIPLE, EXTENDED]:
				if selection not in self.getSelections():
					self.optionList.selection_set(index)
				else:
					self.optionList.selection_clear(index)
				
			self.dragging.geometry("+%s+%s" % (self.master.winfo_x() + self.dragging.x, self.master.winfo_y() + self.dragging.y))
		else:
			deltax = event.x
			deltay = event.y
			x = self.master.winfo_x() + deltax
			y = self.master.winfo_y() + deltay
			self.dragging.geometry("+%s+%s" % (x - self.dragging.winfo_width() / 2, y + self.dragging.winfo_height() / 2))
	
	def click(self, event):
		self.selections = self.getSelections()
	
	def getSelections(self):
		items = self.optionList.curselection()
		return [self.optionList.get(item) for item in items]
	
	def connectToDest(self, dest):
		#allows for dragging and dropping of list items to a destination
		self.dragDestinations.append(dest)

		
class FloatingWindow(Toplevel):
   
   def __init__(self, index, name, x, y):
		Toplevel.__init__(self)
		self.overrideredirect(True)
		self.attributes("-alpha", 0.8)  

		self.index = index
		self.name = name
		self.label = Label(self, text=name)
		self.label.pack(side="right", fill="both", expand=True)

		self.x = x
		self.y = y

def test():
	OPTIONS = [
		Attribute("egg", 1),
		"bunny",
		"chicken",
		"ducks",
		"moose"
	] * 5
	
	master = Tk()
	
	w = ScrollableOptions(master, OPTIONS, mode = MULTIPLE, width = 400)
	w.pack()
	
	#master.bind("<ButtonPress-1>", w.click)
	
	master.mainloop()

if __name__ == "__main__":
	test()