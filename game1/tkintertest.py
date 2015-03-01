from Tkinter import *
from infodisplay import *
import grid

def onclick(event):
   print("Clicked at: ", event.x, event.y)

root = Tk()

def bottom_border(grid, loc):
	return loc in grid and (loc[0], loc[1] + 1) in grid and grid[loc] != grid[(loc[0], loc[1] + 1)]

def right_border(grid, loc):
	return loc in grid and (loc[0] + 1, loc[1]) in grid and grid[loc] != grid[(loc[0] + 1, loc[1])]

def draw_borders(canvas, grid, squaresize = 30, color = 'black', topleft = (0, 0)):
	for x in range(grid.width):
		for y in range(grid.height):
			if bottom_border(grid, (x, y)):
				line = canvas.create_line(topleft[0] + x * squaresize, topleft[1] + (y + 1) * squaresize, topleft[0] + (x + 1) * squaresize, topleft[1] + (y + 1) * squaresize, fill = color, tags = [grid[(x, y)], grid[(x, y + 1)]])
			if right_border(grid, (x, y)):
				line = canvas.create_line(topleft[0] + (x + 1) * squaresize, topleft[1] + y * squaresize, topleft[0] + (x + 1) * squaresize, topleft[1] + (y + 1) * squaresize, fill = color, tags = [grid[(x, y)], grid[(x + 1, y)]])

def paint_squares(canvas, grid, squaresize = 30, defcolor = 'red', topleft = (0, 0), colormap = None):
	color = defcolor
	for x in range(grid.width):
		for y in range(grid.height):
			if colormap:
				try:
					color = colormap[grid[(x, y)]]
				except KeyError:
					color = defcolor
			rect = canvas.create_rectangle(topleft[0] + x * squaresize, topleft[1] + y * squaresize, topleft[0] + (x + 1) * squaresize, topleft[1] + (y + 1) * squaresize, fill = color, tags = grid[(x, y)], outline = color)
			

def grid_canvas(grid):
	colormap = {'0': 'blue', '3': 'blue', '10': 'green'}
	canvas = Canvas(root, width = 400, height = 800)
	paint_squares(canvas, grid, colormap = colormap)
	draw_borders(canvas, grid)
	print grid.all_vals()
	return canvas

w = grid_canvas(grid.random_territory_grid(10, 10, 4, 1))
#w.create_line(0, 0, 200, 100)
#w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))

'''
text = Text(w)
text.insert(INSERT, "Hello.....")
text.insert(END, "Bye Bye.....")
text.pack()

text.tag_add("here", "1.0", "1.4")
text.tag_add("start", "1.4", "1.10")
text.tag_config("here", background="yellow", foreground="blue")
text.tag_config("start", background="black", foreground="green")
'''

#scrollbar = Scrollbar(w)
#scrollbar.pack( side = RIGHT, fill = BOTH)
#w.config(yscrollcommand = scrollbar.set)

w.pack(side = LEFT)
inf = InfoWindow(root, height = 800, width = 300)
inf.canvas.pack(side=RIGHT)
inf.display_def_msg()


root.mainloop()