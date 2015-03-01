from Tkinter import *
import re
from numbers import Number

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
OBJECT = 3

class Item:
	
	def __init__(self, name, type):
		self.name = name
		self.type = type
	
	def __str__(self):
		return self.name

class DraggableList(Listbox):
	
	def __init__(self, master, options, mode = SINGLE):
		Listbox.__init__(self, master, selectmode = mode, font = ("Times", 16))
		self.master = master
		self.optionNames = {str(option): option for option in options}
		for option in options:
			self.insert(END, option)
		#self.optionList.configure(height = 10)
		#self.bind("<ButtonPress-1>", self.click)
		self.bind("<ButtonRelease-1>", self.released)
		self.bind("<B1-Motion>", self.motion)
		self.dragging = None
		self.dragDestinations = []
	
	def strIndex(self, name):
		strs = self.get(0, END)
		for i in range(len(strs)):
			if strs[i] == name:
				return i
		return None
	
	def updateNames(self):
		for name, option in self.optionNames.items():
			if name != str(option):
				i = self.strIndex(name)
				selected = self.selection_includes(i)
				self.delete(i)
				self.insert(i, str(option))
				del self.optionNames[name]
				self.optionNames[str(option)] = option
				if selected:
					self.selection_set(i)
				
	
	def dispatchDrop(self, event, droppedItem):
		for dest in self.dragDestinations:
			if contains(dest, event):
				if hasattr(dest, "receiveDrop"):
					dest.receiveDrop(self, droppedItem, event)
	
	def released(self, event):
		if contains(self, event): #release takes place inside option list
			#re-sort if dragging
			if self.dragging:
				index = self.nearest(event.y - self.dragging.winfo_height() / 2) + 1
				self.insert(index, self.dragging.name)
				if self.dragging.index > index: 
					#insert will have offset old index - correct
					self.dragging.index += 1
				print self.curselection(), self.dragging.index
				if str(self.dragging.index) in self.curselection():
					self.selection_set(index)
				self.delete(self.dragging.index)
		
		if self.dragging:
			self.dragging.destroy()
		self.dragging = None
	
	def motion(self, event):
		index = self.nearest(event.y)
		selection = self.get(index)
		if not self.dragging:
			self.dragging = FloatingWindow(index, selection, event.x, event.y)
			#toggle selection (so dragging does not change selection)
			#only for multiple selection method
			if self.cget("selectmode") in [MULTIPLE, EXTENDED]:
				if selection not in self.getSelections():
					self.selection_set(index)
				else:
					self.selection_clear(index)
				
			self.dragging.geometry("+%s+%s" % (self.master.winfo_rootx() + self.dragging.x, self.master.winfo_rooty() + self.dragging.y))
		else:
			deltax = event.x
			deltay = event.y
			x = self.master.winfo_x() + deltax
			y = self.master.winfo_y() + deltay
			self.dragging.geometry("+%s+%s" % (x - self.dragging.winfo_width() / 2, y + self.dragging.winfo_height() / 2))
	
	def getSelections(self):
		self.updateNames()
		items = self.curselection()
		return [self.optionNames[self.get(item)] for item in items]
	
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


class ListEntry(Entry):
	
	def __init__(self, master, obj, **options):
		Entry.__init__(self, master, **options)
		self.master = master
		self._obj = obj
		if not obj or not hasattr(obj, "set"):
			raise Exception("entry must have an object with a set method.")
		self.bind("<FocusOut>", self._lostFocus)
		self.bind("<FocusIn>", self._gotFocus)
		self.bind("<Tab>", self._tab)
		self.bind("<Return>", self._return)
	
	def _reportInputError(self, msg):
		self.delete(0, END)
		self.insert(0, msg)
	
	def displayLast(self):
		self.delete(0, END)
		self.insert(0, str(self._obj.get()))
	
	def _gotFocus(self, event):
		self.displayLast()
		self.selection_range(0, END)
		
	def _lostFocus(self, event):
		try:
			self._obj.set(self.get())
		except Exception as e:
			self._reportInputError(str(e))
		
	def _return(self, event):
		self.master.focus_set()		
	
	def _tab(self, event):
		pass#self.master.focusNext()
	
	def getVal(self):
		return self._obj.get()

class IntStrVar:
	
	def __init__(self):
		self.var = IntVar()
	
	def set(self, val):
		try:
			self.var.set(int(val))
		except Exception:
			raise Exception("Must be an integer value")
	
	def get(self):
		return self.var.get()
	
	def __str__(self):
		return str(self.get())

class FloatStrVar:
	
	def __init__(self):
		self.var = DoubleVar()
	
	def set(self, val):
		self.var.set(float(val))
	
	def get(self):
		return self.var.get()
	
	def __str__(self):
		return str(self.get())

class EntryList(Canvas):
	
	'''
	create a list where entries can be edited.
	'''
	
	def __init__(self, master, **options):
		Canvas.__init__(self, master, highlightthickness = 0)
		self.frame = Frame(self)
		self.frame.pack()
		#self.grid_propagate(False)
		self.entryOptions = {}
		if 'width' in options:
			self.entryOptions['width'] = options['width']
		self.entries = []	
		self.create_window((3,3), window=self.frame, anchor="nw", 
                                  tags="self.frame")
		self.frame.bind("<Configure>", self.onFrameConfigure)
		
			
	def onFrameConfigure(self, event):
		self.configure(scrollregion=(0, 0, self.frame.winfo_reqwidth(), self.frame.winfo_reqheight()))
	
	def addEntry(self, entry):
		entry.displayLast()
		entry.pack(row = len(self.entries))
		self.entries.append(entry)	
	
	def addEntries(self, entries):
		for entry in entries:
			self.addEntry(entry)
	
	def add(self, val):
		if isinstance(val, basestring):
			var = StringVar()
			var.set(val)
			val = var #to simplify following code
		elif isinstance(val, (long, int)):
			var = IntStrVar()
			var.set(val)
			val = var #to simplify following code
		elif isinstance(val, float):
			var = FloatStrVar()
			var.set(val)
			val = var #to simplify following code
			
		self.addEntry(ListEntry(self.frame, val, **self.entryOptions))
	
	def addAll(self, vals):
		for val in vals:
			self.add(val)

	def focusNext(self):
		current = self.focus_get()
		for i in range(len(self.entries)):
			if self.entries[i] == current:
				self.entries[(i + 1) % len(self.entries)].focus_set()

class TraitList(Canvas):
	
	'''
	create a list where entries cannot be edited, but scrolling is enabled.
	'''
	
	def __init__(self, master, **options):
		Canvas.__init__(self, master, **options)
		self.frame = Frame(self)
		self.frame.pack()
		#self.grid_propagate(False)
		self.font = None
		if 'font' in options:
			self.font = font
		self.entries = []	
		self.create_window((3,3), window=self.frame, anchor="nw", 
                                  tags="self.frame")
		self.frame.bind("<Configure>", self.onFrameConfigure)
		
			
	def onFrameConfigure(self, event):
		self.configure(scrollregion=(0, 0, self.frame.winfo_reqwidth(), self.frame.winfo_reqheight()))
	
	def addEntry(self, entry):
		entry.pack(fill=X)
		self.entries.append(entry)	
	
	def addEntries(self, entries):
		for entry in entries:
			self.addEntry(entry)
	
	def add(self, val):
		if self.font:
			self.addEntry(Label(self.frame, text = val, font = self.font))
		else:
			self.addEntry(Label(self.frame, text = val))
	
	def addAll(self, vals):
		for val in vals:
			self.add(val)
	

def scrollAll(objs, *args):
	for obj in objs:
		obj.yview(*args)

def test():
	OPTIONS = [
		"egg",
		"bunny",
		"chicken",
		"ducks",
		"moose",
		6
	] * 5
	
	master = Tk()
	
	#w = DraggableList(master, OPTIONS, mode = MULTIPLE)
	#w.configure(height = 10, width = 50)
	w = TraitList(master)
	w2 = EntryList(master)
	w.addAll(OPTIONS)
	w2.addAll(OPTIONS)
	w.configure(height = 10)
	
	scrollBar = Scrollbar(master, command = lambda *args: scrollAll((w, w2), *args))
	
	w['yscrollcommand'] = scrollBar.set
	w2['yscrollcommand'] = scrollBar.set
	
	#master.grid_propagate(False)
	#master['width'] = 200
	#master['height'] = 200
	
	
	w.grid(row = 0, column = 0, sticky="nsew", padx=2, pady=2)
	scrollBar.grid(row = 0, column = 2, sticky="nsew", padx=2, pady=2)
	w2.grid(row = 0, column = 1, sticky="nsew", padx=2, pady=2)
	
	#master.bind("<ButtonPress-1>", w.click)
	
	master.mainloop()

class Unit:
	
	def __init__(self):
		self.attrs = {}
	
	def __setitem__(self, attr, val):
		self.attrs[attr] = val
	
	def __getitem__(self, attr):
		return self.attrs[attr]
	
	def __str__(self):
		if 'name' in self.attrs:
			return self.attrs['name']
		return " unit: " + str(self.attrs)

class SwitchButton(Button):
	
	def __init__(self, master, default = False, **options):
		Button.__init__(self, master, command = self._onClick, **options)
		self.value = default
		txt = str(self.value)
		self['text'] = txt
		self.master = master
	
	def _onClick(self):
		self.value = not self.value
		self.master.setVal(self.value)
		txt = str(self.value)
		self['text'] = txt
	
	def getVal(self):
		return self.value

class EntryButton(Frame):
	
	def __init__(self, master, default, **options):
		Frame.__init__(self, master, **options)
		self.button = Button(self, command = self._buttonClick)
		self.button['text'] = str(default)
		self.button.pack()
		self.val = default
		self.entry = Entry(self)
		self.entry.bind("<FocusOut>", self._entryLostFocus)
		self.entry.bind("<Return>", self._entryReturn)
		self.master = master
	
	def _buttonClick(self):
		self.entry.delete(0, END)
		self.entry.insert(0, str(self.val))
		self.entry.focus_set()
		self.entry.selection_range(0, END)
		self.button.pack_forget()
		self.entry.pack()
	
	def _entryReturn(self, event):
		self.focus_set()
	
	def _entryLostFocus(self, event):
		try:
			self.set(self.entry.get())
			self.entry.pack_forget()
			self.button['text'] = str(self.val)
			self.button.pack()
		except ValueError:
			self.entry.delete(0, END)
			if isinstance(self.val, int):
				self.entry.insert(0, "Value must be an int")
			elif isinstance(self.val, float):
				self.entry.insert(0, "Value must be a float")
			self.entry.selection_range(0, END)
			self.focus_set()
	
	def set(self, strVal):
		if isinstance(self.val, int):
			self.val = int(strVal)
		elif isinstance(self.val, float):
			self.val = float(strVal)
		else:
			self.val = strVal
		self.master.setVal(self.val)
	

class LabeledButton(Frame):
	
	def __init__(self, master, unit, trait, default, **options):
		Frame.__init__(self, master, **options)
		self.trait = trait
		label = Label(self)
		label['text'] = str(trait)
		label.pack(side = LEFT, anchor = W)
		if default is False or default is True:
			self.button = SwitchButton(self, default = default)
		else:
			self.button = EntryButton(self, default = default)
		self.button.pack(side = RIGHT, anchor = E)
		self.unit = unit
			
	def displayLast(self):
		pass
	
	def getTrait(self):
		return self.trait
	
	def getVal(self):
		return self.button.getVal()
	
	def setVal(self, val):
		self.unit[self.trait] = val

class ScrollableButtonList(TraitList):
	
	'''
	modify to create a version of traitlist with buttons as well as labels; a button should change to an entry when pressed, and back to a button when that object loses focus. For booleans, hitting the button should just flip the trait.	
	'''
	
	def add(self, unit, trait, val = False):
		self.addEntry(LabeledButton(self.frame, unit, trait, val))
	
	def getValue(self, trait):
		for entry in self.entries:
			if entry.getTrait() == trait:
				return entry.getVal()
		return None
	
	def fitToUnit(self, unit):
		for entry in self.entries:
			entry.destroy()
		for attr, val in unit.attrs.items():
			self.add(unit, attr, val)
	
class WorldEditor(Frame):
	
	def __init__(self, master):
		Frame.__init__(self, master)
		self.tabs = Frame(self)
		self.unitTab = Button(self.tabs, text='Edit Units', relief=RAISED, command = self.switchToUnitTab)
		self.unitTab.grid(row = 0, column = 0, padx=2)
		self.traitTab = Button(self.tabs, text='Edit Traits', relief=RAISED, command = self.switchToUnitTab)
		self.traitTab.grid(row = 0, column = 1, padx=2)
		self.tabs.pack(side = 'top')
		
		self.unitEdit = Frame(self)
		unit = Unit()
		unit['name'] = 'Juan'
		unit['isKickass'] = False
		unit['strength'] = 3
		self.unitList = DraggableList(self.unitEdit, [unit])
		self.unitList.bind("<<ListboxSelect>>", self.unitSelect)
		self.unitList.pack(side = LEFT, fill = 'x', expand = False)
		self.unitAttrs = ScrollableButtonList(self.unitEdit)
		self.unitAttrs.pack(side = LEFT, fill = 'x', expand = False)
		self.newButton = Button(self.unitEdit, text="New Unit")
		self.newButton.pack(side = LEFT, fill = 'x', expand = False)
		
		self.attrEdit = Frame(self)
		
		self.currentTab = None
	
	def unitSelect(self, event):
		unit = event.widget.getSelections()[0]
		self.selectNewUnit(unit)
	
	def selectNewUnit(self, unit):
		self.unitAttrs.fitToUnit(unit)
	
	def setTab(self, button):
		if button.cget('text') == 'Edit Units':
			self.attrEdit.pack_forget()
			self.unitEdit.pack(side = 'bottom', expand = True, fill = 'both')
		else:
			self.unitEdit.pack_forget()
			self.attrEdit.pack(side = 'bottom', expand = True, fill = 'both')
		if self.currentTab:
			self.currentTab.configure(relief=SUNKEN)
		button.configure(relief = RAISED)
	
	
	def switchToUnitTab(self):
		if self.currentTab != self.unitTab:
			self.setTab(self.unitTab)
			self.currentTab = self.unitTab
		
if __name__ == "__main__":
	master = Tk()
	ed = WorldEditor(master)
	ed.pack()
	master.geometry("300x200+300+300")
	master.mainloop()
	
