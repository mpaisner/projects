import operator

#this will be fairly complex eventually. For now, it is just the salary offered.
def get_job_q(business, salary):
	return salary

def get_job_offer(business, jobSeekers):
	'''jobseekers is a TransferGroup.'''
	


def get_n_best_offers(business, buyers, n, transportcosts):
	offers = []
	for buyer in buyers:
		offer = buyer.get_offer(business, business.output, business.stockpiles[business.output].quality, transportcosts.cost(business.market, buyer.market))
		if len(offers) < n:
			heapq.heappush(offers, (offer.price, offer))
		elif offer.price > offers[0].price:
			heapq.heappop(offers)
			heapq.heappush(offers, (offer.price, offer))
	return {offer for price, offer in offers}
		
def all_offers(marketsByIndex, businessesByIndex, transCostDict, resourceTransCosts):
	offers = {}
	for sellerIndex, seller in businessesByIndex.items():
		offers[sellerIndex] = []
		for marketIndex, market in marketsByIndex.items():
			unitTransCost = transCostDict[(seller.market.index, marketIndex)] * resourceTransCosts[seller.output]
			if unitTransCost <= seller.maxTransCost:
				for buyer in market.buyers[seller.output]:
					qDifPer = (seller.stockpiles[seller.output].quality - buyer.stockpiles[seller.output].quality) / buyer.stockpiles[seller.output].quality
					quantityValModifier = 1 + buyer.task.outputQuantityContr[seller.output] * qDifPer
					qualityValModifier = 1 + buyer.dVdQPer * buyer.task.outputQualityContr[seller.output] * qDifPer
					unitOffer = buyer.prices[seller.output] * quantityValModifier * qualityValModifier - unitTransCost
					if unitOffer >= seller.minOutputPrice:
						offers[sellerIndex].append((buyer.index, unitOffer, unitTransCost, 0))
		offers[sellerIndex].sort(key = operator.itemgetter(1))
		offers[sellerIndex] = offers[sellerIndex][-seller.maxOffers:]
	return offers

def fill_offers(offerDict, marketsByIndex, businessesByIndex):
	for sellerIndex, offers in offerDict.items():
		seller = businessesByIndex[sellerIndex]
		vals = [offer[1] ** seller.distributionExp for offer in offers]
		totalVal = sum(vals)
		filledOffers = []
		for i in range(len(offers)):
			quantity = vals[i] * seller.outputAvailable / totalVal
			filledOffers.append((offers[i][0], offers[i][1], offers[i][2], quantity))
		offerDict[sellerIndex] = filledOffers
	return offerDict

def update_sales(offerDict, marketsByIndex, businessesByIndex):
	stockpileDict = {} #stores "total" quality rather than per unit, for easier summation.
	for bizIndex, business in businessesByIndex.items():
		stockpileDict[bizIndex] = {resource: (business.stockpiles[resource].quantity, business.stockpiles[resource].quantity * business.stockpiles[resource].quality) for resource in business.task.inputs + [business.output]}
	for sellerIndex, offers in offerDict:
		seller = businessesByIndex[sellerIndex]
		for buyerIndex, price, transCost, quantity in offers:
			buyer = businessesByIndex[buyerIndex]
			dQTotal = buyer.stockpiles[seller.output].quality * quantity
			#update seller
			oldN, oldQ = stockpileDict[sellerIndex][seller.output]
			stockpileDict[sellerIndex][seller.output] = (oldN + quantity, oldQ + dQTotal)
			seller.cash += price * quantity
			#update buyer
			oldN, oldQ = stockpileDict[buyerIndex][seller.output]
			stockpileDict[buyerIndex][seller.output] = (oldN - quantity, oldQ - dQTotal)
			buyer.cash -= price * quantity

def update_prices(offerDict, marketsByIndex, businessesByIndex):
	offersByBuyer = {}
	for sellerIndex, offers in offerDict:
		seller = businessesByIndex[sellerIndex]
		

class Task:
	
	#inputs and outputs are resIndices, not Resource objects
	def __init__(self, name, inputQs, output, defdVdQ, defPrices):
		self.name = name
		self.inputs = inputQs
		self.output = output
		#change this to change interactions between skill and input quality as far as output quantity
		self.outputQuantityContr = {input: float(quantity) / sum(inputQs.values()) / 2 for input, quantity in inputQs.items()}
		#change this to change interactions between skill and input quality as far as output quality
		self.outputQualityContr = {input: float(quantity) / sum(inputQs.values()) / 2 for input, quantity in inputQs.items()}
		self.prices = defPrices

class Stockpile:
	
	def __init__(self, quality, quantity):
		self.quality = quality
		self.quantity = quantity

class Business:
	
	nextIndex = 1
	
	def __init__(self, name, task, market, cash):
		self.name = name
		self.index = Business.nextIndex
		Business.nextIndex += 1
		self.task = task
		self.output = task.output
		self.stockpiles = {resource: Stockpile(50, 0) for resource in self.task.inputs.keys() + [self.output]}
		self.market = market
		self.dVdQPer = 1.0
		self.prices = dict(task.prices)
		self.cash = cash
		self.maxTransCost = self.prices[self.output] / 2
		self.outputAvailable = self.stockpiles[self.output].quantity
		self.distributionExp = 8.0
		self.maxOffers = 5
		self.minOutputPrice = 0.0
	
	def calculate_available(self):
		self.outputAvailable = self.stockpiles[self.output].quantity

class Market:
	
	nextIndex = 1
	
	def __init__(self, name, allResources):
		self.name = name
		self.index = Market.nextIndex
		Market.nextIndex += 1
		self.buyers = {resource: set() for resource in allResources}
		self.businesses = {}
	
	def add_business(self, business):
		replacing = False
		if business.task in self.businesses:
			print "replacing old business in task", str(business.task)
			replacing = True
		self.businesses[business.task] = business
		for input in business.task.inputs:
			self.buyers[input] = {buyer for buyer in self.buyers[input] if buyer.task != business.task}
			self.buyers[input].add(business)
		
wood = 1
furniture = 2
paper = 3
resTransCosts = {1: 2.0, 2: 10.0, 3: 0.2}
woodcuttingTask = Task("Woodcutting", {}, 1, 0.01, {1: 10.0})
woodbuyingTask = Task("Furniture", {1: 1.0}, 2, 0.01, {1: 10.0, 2: 30})
market1 = Market("M1", (1, 2, 3))
market2 = Market("M2", (1, 2, 3))

woodcutBiz = Business("WoodBiz", woodcuttingTask, market1, 100.0)
woodcutBiz.stockpiles[1].quantity = 10.0
woodcutBiz.stockpiles[1].quality = 50.0
woodcutBiz.calculate_available()

furnitureBiz = Business("FurnitureBiz", woodbuyingTask, market1, 100.0)

market1.add_business(woodcutBiz)
market2.add_business(furnitureBiz)

transcosts = {(1, 2): 1.0, (2, 1): 1.0, (1, 1): 0.0, (2, 2): 0.0}

print all_offers({1: market1, 2: market2}, {1: woodcutBiz, 2: furnitureBiz}, transcosts, resTransCosts)
print fill_offers(all_offers({1: market1, 2: market2}, {1: woodcutBiz, 2: furnitureBiz}, transcosts, resTransCosts), {1: market1, 2: market2}, {1: woodcutBiz, 2: furnitureBiz})

'''
Resource trading - values needed for:
All:
	1) Int key associated with each market (< 1000)
	2) Int key associated with each business
		-format is: (ordinal in market by creation time) * 1000 + (marketNum)
		-so businessKey % 1000 == market key

Buying Business:
	1) My resource base prices
	2) My current resource stockpile qualities
	3) My resource output %contribution to quality
	4) My resource quality %contribution to quantity
	5) My %dVdQ for output
	6) Seller Resource Quality
	7) Transport cost
	8) Resource transport "size"
	9) Max transport cost per resource (output) - defines sale range
	Def: qDif% = (sellerQ - MyStockpileQ) / MyStockpileQ
	
	Offer = basePrice * (1 + outputQuantity% * qDif%) * (1 + %dVdQ * outputQuality% * qDif%) - transport cost * transport size

Selling Business:
	1) All offer prices
	2) Distribution exponent k
	3) My output available for sale
	4) My max number of buyers
	5) Min acceptable price
	Def: totalVal = sum([offerPrice ^ k for all offers])
	
	Amount sold = offerPrice ^ k * outputAvailable / totalVal

Algorithm:
	1) init dict {seller: (buyer, 0, transcost, 0)} #(buyer, price, transcost quantity)
		-All buyers of resource in feasible markets for each seller
	2) load transport cost dict {(source, dest): cost}
	3) iteratively update offers to {seller: [(buyer, offer, transcost, 0)]}
		-keep only offers above min price
	4) sort offers by price, keep only N (#4 in seller info).
	5) iterate through sellers again. For each:
		A) calculate total offer value (totalVal above)
		B) Assign quantities to dict so {seller: [(buyer, offer, transcost, quantity)]}
	6) return dict {seller: (buyer, offer, transcost, quantity)}

Updating - Info needed:
	1) current industry cash
	2) offerDict {seller: [(buyer, offer, transcost, quantity)]}
	3) current industry stockpiles {industry: {resource: (num, num * quality)}}

Updating - Algorithm:
	1) Initialize newStockpiles {industry: {resource: (num, totalQuality)}} for each resource and output. Copies of 3) above.
	2) Init newCash {industry: cash}
	3) Init transCosts {(start, dest): cost}
	For each seller in offerDict:
		for each (buyer, offer, transcost, quantity) in offerDict[seller]:
			newStock[seller][seller.output][0] -= quantity
			newStock[buyer][seller.output][0] += quantity
			newStock[buyer][seller.output][1] += quantity * seller.outputQ
			transCosts[seller.market, buyer.market] += transcost #check if in
			newCash[seller] += quantity * offer
			newCash[buyer] -= quantity * offer
	4) Copy new values to businesses.
'''	