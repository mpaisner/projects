from Tkinter import *


class InfoWindow:
	
	defmsg = "Nothing selected."
	titlebuffery = 25
	
	def __init__(self, parent, **options):
		self.canvas = Canvas(parent, **options)
		self.width = options['width']
		self.height = options['height']
		self.canvas.create_line(3, 0, 3, self.height)
	
	def display_def_msg(self):
		self.canvas.create_text((self.width / 2, self.titlebuffery), text = self.defmsg, tags = "title")

	