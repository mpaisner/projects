'''
At each step t, each industry has:
1) a measure (0..2) of demand for more output
	-This is defined by numbidlast / (stockpile + lastproduction)
2) a measure (>= 0) of its desire for better output
	-This is defined by a "poll" of potential buyers on their marginal valuation of 1 additional unit of quality. It should reflect the actual per unit cash value of 1 unit of quality, assuming nothing changes.
3) a measure (0..2) of its current demand for each resource it uses. This is defined by (2 * its desired stockpile) / (its desired stockpile + its actual stockpile).
4) a measure of its current demand for more workers. This defined by (the least reciprocal of all values from #3 ** 2) * #1)

Buyer offers:
1) Base buyer offers are increased or decreased depending on their demand for a given resource, calculated in 3 above.
2) Buyer offers are weighted by their valuation of the worth of resources by quality, calculated using 2 above.

Seller sales:
1) Seller calculate how many offers (n) to accept based on previous value of n +/- 1 depending on if they sold all their goods at a profit last turn.
2) Sellers pick the n best offers. 
3) For each of the n buyers, sellers sell num available * quadratic(offer value) / sum(all values)
'''
import random
from transport import *
from trading import ValueMem

class Offer:
	
	def __init__(self, buyer, price):
		self.buyer = buyer
		self.price = price
		self.quantity = 0

class SalaryOffer:
	
	def __init__(self, business, salary):
		self.business = business
		self.salary = salary
		self.quantity = 0



def pick_n_best_offers(offers, n):
	return sorted(offers, cmp = lambda x, y: cmp(x.price, y.price))[-n:]

#quantity of available goods should be determined by overall offer quality, compared to recent turns, as well as available stockpiles.
def calculate_sales(offers, available, n):
	nOffers = n_best_offers(offers, n)
	quadratics = {offer.buyer: offer.price ** 10 for offer in nOffers}
	total = sum(quadratics.values())
	for offer in nOffers:
		offer.quantity = available * quadratics[offer.buyer] / total


'''
offers = [Offer(str(i), random.random()) for i in range(10)]
calculate_sales(offers, 50, 5)
for offer in offers:
	print offer.price, offer.quantity
'''	

'''Given:
1) transport costs
2) {industry: set(feasible markets)} - calculated using 1) and cutoffs
3) {market: {resource: set(sellers)}} - calculated using 2)
4) {market: {resource: set(buyers)}} - easy to calculate, should not be done each time step - update when industries appear/vanish.
'''

class Market:
	
	def __init__(self, name):
		self.name = name
		self.businesses = {} #{type: business}
		self.buyers = {} #{resource, set(business)} - local buyers of resource
		self.sellers = {} #{resource, set(business)}- all sellers of resource here
		#will eventually be data for population wealth, demand, etc. Possibly in another data structure, however.

#eventually, sort markets for each market by distance, then easier to cut off for each business. However, for now keeping it simple (though not efficient)
def get_feasible_markets(self, business, markets, transportcosts, maxcostpercent = 1.0):
	routesfrom = transportcosts.paths_from(business.market)
	res = set()
	for dest, path in routesfrom.items():
		if path.cost < business.output_value() * maxcostpercent:
			res.add(dest)
	return res

#assumes markets have updated information
def get_all_buyers(business, viablemarkets):
	buyers = set()
	for market in viablemarkets:
		for business in market.buyers[business.task.output]:
			buyers.add(business)
	return buyers
	

#must calculate outputs first
#markets is set of feasible markets for current business
def get_all_offers(business, buyers, transportcosts):
	offers = set()
	for buyer in buyers:
		offers.add(buyer.get_offer(business, business.task.output, business.outputstockpile.quality, transportcosts.cost(business.market, buyer.market)))
	return offers

import heapq

def get_n_best_offers(business, buyers, n, transportcosts):
	offers = []
	for buyer in buyers:
		offer = buyer.get_offer(business, business.task.output, business.outputstockpile.quality, transportcosts.cost(business.market, buyer.market))
		if len(offers) < n:
			heapq.heappush(offers, (offer.price, offer))
		elif offer.price > offers[0].price:
			heapq.heappop(offers)
			heapq.heappush(offers, (offer.price, offer))
	return {offer for price, offer in offers}

#Next: 1 function that returns all offers (or numerical representations) for all resources in the whole world on a given turn. This function should use minimal external function calls (acutally, any O(1) number of function calls are fine)


def get_best_offers(markets, transcostsdict)

	