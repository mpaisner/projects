import Tkinter

class ReadOnlyText(Tkinter.Text):
	
	def __init__(self, master, **args):
		Tkinter.Text.__init__(self, master, args)
		self.config(state = Tkinter.DISABLED)
	
	def getText(self):
		return self.get(1.0, Tkinter.END)
	
	def setText(self, txt):
		self.config(state = Tkinter.NORMAL)
		self.delete(1.0, Tkinter.END)
		self.insert(Tkinter.INSERT, txt)
		self.config(state = Tkinter.DISABLED)


class simpleapp_tk(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
                
        self.initialize()

    def initialize(self):
        self.grid()
        
        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self, textvariable = self.entryVariable)
        self.entry.grid(column=0,row=0,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        
        self.button = Tkinter.Button(self,text=u"Click me !",  command=self.OnButtonClick)
        self.button.grid(column=1,row=0)
        
        self.button = Tkinter.Button(self,text=u"Click me !")
        self.button.grid(column=2,row=0)
        
        self.textBox = ReadOnlyText(self, fg="white",bg="blue", height = 10, width = 50, wrap = 'word')
        self.textBox.config(state = Tkinter.DISABLED)
        self.textBox.grid(column=0,row=1,columnspan=3,sticky='EW')
        
        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)      
        self.update()
        self.geometry(self.geometry())
        
        #self.after_idle(self.onIdle)
    
    def OnButtonClick(self):
        self.createHelpBox("button!")
        #self.labelVariable.set("You clicked the button !")

    def OnPressEnter(self,event):
        self.textBox.setText(self.entryVariable.get())
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)
    
    def createHelpBox(self, txt):
    	txtVar = Tkinter.StringVar()
    	txtVar.set(txt)
    	box = Tkinter.Toplevel(self)
    	box.grid()
    	label = Tkinter.Label(box, textvariable=txtVar, anchor="w",fg="black",bg="floral white")
    	label.grid(column=0,row=0,columnspan=1,sticky='EW')
    	
class DropDownDrag:
	
	
    	

if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('my application')
    app.mainloop()


'''
*All units are shown with both a name and picture next to it. Use some generic picture and empty name as placeholders where necessary.
1) Dropdown menu from which every unit type can be selected
2) New Unit pane (on right or left).
	-several quick choices (e.g. basic infantry, cavalry, etc.). 
	-quick choices can be modified by dragging from the dropdown menu or by clicking a 'set to current' button next to each quick choice. 
	-Also, units can be selected from a dropdown identical to the main units selector, but which also allows an 'empty' choice. Empty units will have only abilities which are set as default for that world.
3) Under main dropdown, unit editing window
	-Name text field
	-Attributes listed in order and by category. Original order will be some arbitrary order and only one category, but attributes can be dragged to different spots, and there should be an always-visible button to create a new category. All changes of this type will propogate to all units.
	-Boolean attributes will only appear is the unit has them. Unused boolean attributes will be selectable from a box to the side of the unit attributes (click to add, right click to display description if any). Illegal attributes will be grayed out; there will be a checkbox to enable/disable showing of illegal attributes. 
	-Clicking a boolean attribute will remove it; clicking a non-boolean will open it for editing (a textbox will appear where the value was displayed). Right clicking will display a help text if any exists.
	-All attribute help text will appear in a designated box near the unit attribute area.
4) There will be a delete unit button, with an 'are you sure?' popup
5) Each game setup must have a unique name. Autosave under that name will occur after each change. 
6) There will be a second tab 'world attributes', where these (if any) as well as defaults can be set.

'''