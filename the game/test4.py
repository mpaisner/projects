from Tkinter import *

class ScrollableOptions(Frame):
	
	def __init__(self, master, options, singularSelection = True, textArgs = {}, scrollBarArgs = {}, **args):
		Frame.__init__(self, master, **args)
		self.textBox = Text(self, **textArgs)
		for option in options:
			self.textBox.insert(END, option + "\n", option)
			self.textBox.tag_bind(option, "<Button-1>", self.clickedTag)
		self.textBox.config(state=DISABLED)
		self.textBox.bind("<ButtonRelease-1>", self.released)
		scrollBarArgs["command"] = self.textBox.yview
		self.scrollBar = Scrollbar(self, **scrollBarArgs)
		self.textBox['yscrollcommand'] = self.scrollBar.set
		
		self.textBox.grid(row = 0, column = 0, sticky="nsew", padx=2, pady=2)
		self.scrollBar.grid(row = 0, column = 1, sticky='nsew')
		
		self.singular = singularSelection
		if self.singular:
			self.selection = None
		else:
			self.selection = set()
		
	
	def released(self, event):
		
		
		self.dragging = None
	
	def clickedTag(self, event):
		self.textBox.config(state=NORMAL)
		for tag in self.textBox.tag_names(CURRENT):
			if self.singular:
				if self.selection:
					self.textBox.tag_config(self.selection, foreground = "black")
				self.selection = tag
				self.textBox.tag_config(tag, foreground = "gray")
			else:
				if tag in self.selection:
					self.selection.remove(tag)
					self.textBox.tag_config(tag, foreground = "black")
				else:
					self.selection.add(tag)
					self.textBox.tag_config(tag, foreground = "gray")
			self.dragging = True
		self.textBox.config(state=DISABLED)
	
OPTIONS = [
    "egg",
    "bunny",
    "chicken",
    "ducks",
    "moose"
]

master = Tk()

w = ScrollableOptions(master, OPTIONS, singularSelection = False, textArgs = {"borderwidth": 3, "relief": "sunken"}, width = 400)
w.pack()

#master.bind("<ButtonPress-1>", w.click)

master.mainloop()