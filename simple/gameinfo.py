import pygame
from pygame.locals import *


class Button:
	
	buffer = 5
	color = (20, 20, 20)
	textcolor = (200, 200, 200)
	
	def __init__(self, name, x, y, width, height):
		self.name = name
		self.rect = pygame.Rect(x, y, width, height)

class Text:
	
	color = (200, 0, 0)
	
	def __init__(self, text, x, y, linewidth, maxheight, font):
		self.text = text
		self.rect = pygame.Rect(x, y, linewidth, maxheight)
		self.font = font

class DisplayArea:
	
	color = (0, 0, 0)
	textcolor = (150, 150, 150)
	
	def __init__(self, starttext, x, y, linewidth, maxheight, font):
		self.text = starttext
		self.rect = pygame.Rect(x, y, linewidth, maxheight)
		self.font = font

class InfoArea:
	
	bkgcolor = (120, 90, 30)
	contbuttonheight = 30
	terrbuttonheight = 25
	
	contlistloc = (60, 260)
	
	def __init__(self, width, height):
		self.buttons = []
		self.text = []
		self.displayAreas = []
		self.width = width
		self.height = height
		self.font = pygame.font.Font(None, 20)
		self.continents = {}
		self.currentCont = None
		self.currentTerr = None
		
	def clear(self):
		self.buttons = []
		self.text = []
		self.displayAreas = []
	
	def add_button(self, text, x, y, width, height):
		self.buttons.append(Button(text, x, y, width, height))
		
	def get_button(self, x, y):
		for button in self.buttons:
			if button.rect.collidepoint(x, y):
				return button.name
		return None
		
	def add_text(self, text, x, y, linewidth, maxheight, font=None):
		self.text.append(Text(text, x, y, linewidth, maxheight, font))
	
	def add_text_display(self, text, x, y, linewidth, maxheight, font=None):
		self.displayAreas.append(DisplayArea(text, x, y, linewidth, maxheight, font))
		self.currentDisplay = self.displayAreas[-1]
	
	def set_current_display(self, index):
		self.currentDisplay = self.displayAreas[index]
	
	def get_display_area(self, x, y):
		i = 0
		for displayarea in self.displayAreas:
			if displayarea.rect.collidePoint(x, y):
				return i
			i += 1
		return -1
	
	def set_mode(self, mode):
		self.modeText.text = "Mode : " + mode
	
	def set_continent(self, name):
		if name in self.continents:
			if self.currentCont: #remove old territory buttons
				for terr in self.currentCont.territories:
					for button in self.buttons:
						if button.name == terr:
							self.buttons.remove(button)
							break
			i = 0
			for terr in self.continents[name].territories:
				self.add_button(terr, 190, 290 + i * self.terrbuttonheight, 100, self.terrbuttonheight)
				i += 1
			self.selectedTerrText.rect.y = 300 + i * self.terrbuttonheight
			self.selectedContText.text = "Selected: " + name
			self.currentCont = self.continents[name]
			self.set_territory(self.continents[name], None)	
			return self.continents[name]
		return None
	
	def set_territory(self, cont, name):
		if cont == self.currentCont and name in cont.territories:
			self.currentTerr = cont.territories[name]
			self.selectedTerrText.text = "Selected: " + name
			return cont.territories[name]
		elif name == None:
			self.currentTerr = None
			self.selectedTerrText.text = "Selected: None"
		return None
	
	def get_continent(self, name):
		return self.continents[name]
		
	def get_territory(self, continent, name):
		if name in continent.territories:
				return continent.territories[name]
		return None
			
	
	def draw_default(self):
		self.clear()
		self.add_button("Draw Borders", 25, 100, 95, 30)
		self.add_button("Place Centers", 25, 150, 95, 30)
		self.add_button("Fill", 135, 100, 40, 30)
		self.add_button("Trim", 190, 100, 40, 30)
		self.add_button("Clear", 245, 100, 50, 30)
		self.add_text("Mode = Clear", 150, 150, 50, 50)
		self.modeText = self.text[-1]
		self.add_text("Continents", self.contlistloc[0], self.contlistloc[1], 100, 30)
		self.add_text("Selected: None", 40, 320, 140, 30)
		self.selectedContText = self.text[-1]
		self.add_text("Territories", 190, 260, 100, 30)
		self.add_text("Selected: None", 190, 300, 100, 30)
		self.selectedTerrText = self.text[-1]
	
	def add_continent(self, continent):
		self.add_button(continent.name, 50, 300 + len(self.continents) * self.contbuttonheight, 100, self.contbuttonheight)
		self.continents[continent.name] = continent
		self.selectedContText.rect.y += self.contbuttonheight
		self.set_continent(continent)
	
	def add_territory(self, continent, territory):
		continent.add_territory(territory)
		self.set_continent(continent)
		self.set_territory(continent, territory)
	
	def is_continent(self, name):
		return name in self.continents
	
	def is_territory(self, continent, territory):
		return territory in continent.territories
		
	
	def draw(self):
		new = pygame.Surface((self.width, self.height))
		new.convert_alpha()
		new.fill(self.bkgcolor)
		for button in self.buttons:
			pygame.draw.rect(new, button.color, button.rect)
			new.blit(self.font.render(button.name, True, button.textcolor), (button.rect.x + button.buffer, button.rect.y + button.buffer))
		for text in self.text:
			new.blit(self.font.render(text.text, True, text.color), text.rect)
		for display in self.displayAreas:
			pygame.draw.rect(new, display.color, display.rect)
			new.blit(self.font.render(display.text, True, display.textcolor), display.rect)
		return new
			
	