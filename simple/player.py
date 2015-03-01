
class Card:
	
	vals = [4, 6, 8, 10]
	inc = 5
	types = ["soldier", "horse", "cannon", "wild"]
	
	def __init__(self, terr, type):
		self.type = type
		self.terr = terr
	
	def get_val(index):
		if index < len(vals):
			return vals[index]
		return vals[-1] + inc * (index + 1 - len(vals))
	
	def gen_cards(self, terrs):
		cards = []
		for terr in terrs:
			cards.append(Card(terr, random.choice(types)))
		return cards

class Player:
	
	def __init__(self, color):
		self.color = color
		self.cards = []
	
	def add_card(self, card):
		self.cards.append(card)
	
	def has_multi_set(cards):
		num = [0, 0, 0, 0]
		for card in cards:
			num[card.types.index_of(card.type)] += 1
		wilds = num[3]
		for i in range(3):
			if num[i] == 0:
				if wilds == 0:
					return False
				else:
					wilds -= 1
		return True
		
	
	def get_best_set(self):
		if len(self.cards) < 3:
			return None
		else:
			set = list(self.cards)
			num = [0, 0, 0, 0]
			for card in set:
				num[card.types.index_of(card.type)] += 1
			for i in range(3):
				if num[i] >= 3:
					toremove = []
					for card in set:
						if card.type != card.types[i]:
							toremove.append(card)
					if len(set) - len(toremove) > 3:
						for card in set:
							if card.type == cards.types[i] and card.terr.player != self:
								toremove.append(card)
							if len(set) - len(toremove) == 3:
								break
					for card in toremove:
						set.remove(card)
					while len(set) > 3:
						set.remove(random.choice(set))
					return set
			if self.has_multi_set(set):
				while len(set) > 3:
					for i in range(len(set)):
						guess = list(set)
						#guess remove_at
				
				
				