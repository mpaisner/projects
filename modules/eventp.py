import pygame
from pygame.locals import *

class Object:
	def __init__(self):
		pass

o = Object()
d = Object()
keyspressed = {}

M_RECT_SELECT = 0
M_MAP_SELECT = 1
M_METHOD_SELECT = 2

def set_defaults():
	o.arrowscroll = 10
	d.arrowscroll = 10
	o.mousescroll = 1
	o.mousescrollbutton = 1
	o.scrollboundaries = True
	o.selectionmode = -1
	o.selectionbutton = 1

set_defaults()


################################################
########SCROLLING
################################################

def set_scroll_boundaries(on):
	o.scrollboundaries = on

def set_arrow_scroll(speed):
	if speed == True:
		o.arrowscroll = d.arrowscroll
	elif speed == False:
		o.arrowscroll = 0
	else:
		o.arrowscroll = int(speed)

def scroll_event(scrollcoords, mapsize, windowsize, event):
	if event.type == pygame.KEYDOWN and o.arrowscroll > 0:
		if event.key == K_UP:
			scroll = (0, -o.arrowscroll)
			if o.scrollboundaries:
				scroll = (0, max(-scrollcoords[1], scroll[1]))
			return scroll
		elif event.key == K_DOWN:
			scroll = (0, o.arrowscroll)
			if o.scrollboundaries:
				scroll = (0, max(0, min(mapsize[1] - scrollcoords[1] - windowsize[1], scroll[1])))
			return scroll
		elif event.key == K_LEFT:
			scroll = (-o.arrowscroll, 0)
			if o.scrollboundaries:
				scroll = (max(-scrollcoords[0], scroll[0]), 0)
			return scroll
		elif event.key == K_RIGHT:
			scroll = (o.arrowscroll, 0)
			if o.scrollboundaries:
				scroll = (max(0, min(mapsize[0] - scrollcoords[0] - windowsize[0], scroll[0])), 0)
			return scroll
	elif event.type == pygame.MOUSEMOTION and o.mousescroll > 0:
		if event.buttons[o.mousescrollbutton - 1] > 0:
			scroll = event.rel
			if o.scrollboundaries:
				scroll = (max(-scrollcoords[0], min(mapsize[0] - scrollcoords[0] - windowsize[0], scroll[0])), max(-scrollcoords[1], min(mapsize[1] - scrollcoords[1] - windowsize[1], scroll[1])))
			return scroll
	return None


################################################
########Selection
################################################

def set_selection_mode(mode):
	o.selectionmode = mode

def set_selection_button(button):
	o.selectionbutton = button

def select_event(offset, mapper, event):
	if event.type == pygame.MOUSEBUTTONDOWN and event.button == o.selectionbutton:
		selected = []
		#offset for non-method modes
		offsetpos = (event.pos[0] + offset[0], event.pos[1] + offset[1])
		if o.selectionmode == M_RECT_SELECT:
			for rect in mapper:
				if rect.collidepoint(offsetpos):
					selected.append(mapper[rect])
		elif o.selectionmode == M_MAP_SELECT:
			selected.append(mapper[offsetpos])
		elif o.selectionmode == M_METHOD_SELECT:
			selected.append(mapper(offsetpos))
		return selected

def handle_event(event):
	if event.type == pygame.KEYDOWN:
		keyspressed[event.key] = True
	elif event.type == pygame.KEYUP and event.key in keyspressed:
		del keyspressed[event.key]
