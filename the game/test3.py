from Tkinter import *

class App(Tk):
	
	def __init__(self, parent):
		Tk.__init__(self, parent)
		self.bind("<ButtonPress-1>", self.click)
		button = Button(self, text="Click me !")
		label = Label(self, text = "label")
		button.grid(column = 0, row = 0)
		label.grid(column = 1, row  = 0)
	
	def click(self, event):
		widget = self.winfo_containing(event.x_root, event.y_root)
		print widget, "?"
		if widget:
			print widget.cget("text")

app = App(None)
app.mainloop()