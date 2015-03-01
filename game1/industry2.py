class Stockpile:
	'''a Stockpile can be temporary (turn-to-turn production) or long-term. Long-term stockpiles may degrade depending on resource type and other factors.'''
	
	def __init__(self, resource, quality, quantity):
		self.resource = resource
		self.quality = quality
		self.quantity = quantity

class Input:
	
	def __init__(self, resource, quantity):
		self.resource = resource
		self.quantity = quantity

class Output:
	
	def __init__(self, product, quantity):
		self.product = product
		self.quantity = quantity
		
class IndustryTask:
	
	#efficiencyfunc and qualityfunc define the output quantity and quality as a function of labor skill and mean quality of inputs).
	def __init__(self, name, id, skill, inputs, outputs, labor, efficiencyfunc, qualityfunc, learningfunc, agingfunc, desiredstockpiles, withinskillshiftpenalty, defaultsalary):
		self.name = name #name for user consumption
		self.id = id #id to identify for replacement/modification
		self.skill = skill
		self.inputs = inputs
		self.totalinputs = sum(inputs.values())
		self.output = output #tasks can now have only one output.
		self.labor = labor
		self.efficiencyfunc = efficiencyfunc
		self.qualityfunc = qualityfunc
		self.desiredstockpiles = desiredstockpiles
		self.withinskillshiftpenalty = withinskillshiftpenalty
		self.defaultsalary
	
	def __str__(self):
		return self.name
	
	def input_percent(self, resource):
		try:
			return float(self.inputs[resource]) / self.totalinputs
		except KeyError:
			return 0.0

class Business:
	
	productValueUpdateTime = 5.0
	expectedprofitratio = .2
	
	def __init__(self, task, workers, workerskill, market, index):
		self.task = task
		self.workers = workers
		self.market = market
		self.salary = task.defaultsalary
		self.skill = workerskill
		self.inputstockpiles = {resource: Stockpile(resource, 50.0, 0.0) for resource in task.inputs}
		self.outputstockpile = Stockpile(task.output, 50.0, 0.0)
		self.prices = {resource: resource.startprice for resource in task.inputs} #normalized to current quality = 50
		self.prices[self.task.output] = self.task.output.startprice
		self.dVdQ = 0.0
		self.timesinceupdate = self.productValueUpdateTime #update ASAP
		self.nBuyers = 3
	
	#return (unitoutput, quality)
	def unit_output(self, dt):
		resourceunits = {float(self.inputstockpiles[resource]) / self.task.inputs[resource]: resource for resource in self.task.inputs}
		workerunits = dt * float(self.workers) / self.task.labor
		meanresQ = sum([self.task.input_percent(resource) * self.inputstockpiles[resource].quality for resource in self.task.inputs])
		quantity = self.task.efficiencyfunc(self.skill, meanresQ) * min(resourceunits.keys() + [workerunits])
		quality = self.get_output_q()self.task.qualityfunc(self.skill, meanresQ)
		return quantity, quality
	
	def _output(self, unitoutput, quality):
		Stockpile(self.task.output, quality, unitoutput)
	
	#needs testing.
	def get_output(self, dt):
		quantity, quality = self.unit_output(dt)
		return self._output(quantity, quality)
	
	def add_output(self, output):
		self.outputstockpile.quality = (self.outputstockpile.quality * self.outputstockpiles.quantity + output.quality * output.quantity) / (self.outputstockpile.quantity + output.quantity)
	
	#uses the resources necessary to produce unitoutput units of output. The actual output is unitoutput * task.outputs.values()
	def use_resources(self, unitoutput):
		meanresQ = sum([self.task.input_percent(resource) * self.inputstockpiles[resource].quality for resource in self.task.inputs])
		unitsused = unitoutput / self.task.efficiencyfunc(self.skill, meanresQ)
		for resource, stockpile in self.inputstockpiles.items():
			stockpile.quantity -= unitsused * self.task.inputs[resource]
	
	#actually produce products and consume resources
	def do_production(self, dt):
		unitoutput, quality = self.unit_output(dt)
		self.use_resources(unitoutput)
		self.add_output(self._output(unitoutput, quality))
	
	def get_output_q(self, resourceQs = None, workerSkill = None):
		if not workerSkill:
			workerSkill = self.skill
		meanresQ = sum([self.task.input_percent(input) * self.inputstockpiles[input].quality for input in self.task.inputs if input not in resourceQs])
		meanresQ += sum([self.task.input_percent(resource) * resourceQs[resource] for resource in resourceQs])
		return self.task.qualityfunc(workerSkill, meanresQ)
	
	def get_value(self, resource, quality):
		try:		
			outputQ = self.get_output_q()
			newOutputQ = self.get_output_q({resource: quality})
			increasePercent = ((newOutputQ - outputQ) * self.dVdQ + self.prices[self.task.output]) / self.prices[self.task.output]
			return self.prices[resource] * increasePercent
		except KeyError:
			raise KeyError(str(resource) "is not an input to " + str(self.task))
		#except /0 error:
	
	def output_value(self):
		return self.prices[self.task.output]
	
	def n_best_offers(self, buyers, n, quality = None):
		if not quality:
			quality = self.outputstockpile.quality
		offers = []
		for buyer in buyers:
			offer = buyer.get_offer(self, self.task.output, quality)
			if len(offers) < n:
				heapq.heappush(offers, (offer.price, offer))
			elif offer.price > offers[0].price:
				heapq.heappop(offers)
				heapq.heappush(offers, (offer.price, offer))
	return {offer for price, offer in offers}
	
	def quality_query(self, buyers, n):
		currentOffers = self.n_best_offers(buyers, n)
		betterQualityOffers = self.n_best_offers(buyers, n, self.outputstockpile.quality + 1)
		calculate_sales(currentOffers, 1.0, n)
		calculate_sales(betterQualityOffers, 1.0, n)
		currentValue = sum([offer.price * offer.quantity for offer in currentOffers]) #weighted mean of top n by projected sales
		betterQualityValue = sum([offer.price * offer.quantity for offer in betterQualityOffers]) #weighted mean of top n by projected sales
		return currentValue, betterQualityValue - currentValue
	
	def update_dV_dQ(self, buyers):
		self.prices[self.task.output], self.dVdQ = self.quality_query(buyers, self.nBuyers)

	#may be changed to reflect other factors (e.g. desired profit margins, business relationships, etc.)
	def get_offer(self, seller, resource, quality, transportcost):
		return Offer(self, self.get_value(resource, quality) - transportcost)
	
	def get_worker_value(self, skill):
		outputQ = self.get_output_q()
		newOutputQ = self.get_output_q(workerSkill = skill)
		increasePercent = ((newOutputQ - outputQ) * self.dVdQ + self.prices[self.task.output]) / self.prices[self.task.output]
		return increasePercent * self.salary
	
	def get_skill_at(self, workers):
		'''input workers is a TransferGroup. This function returns the skill the group would have working at this business. Used to generate salary offers as well as to actually add workers. This will depend on the relationship between the skill the workers have currently and the skill required for this job. For now, all skills transfer at 90% of old value unless they are the same skilltype.'''
		if workers.skilltype == self.task.skill:
			return workers.skill
		else:
			return workers.skill * 0.9
	
	def get_salary_offer(self, workers):
		'''input workers is a TransferGroup.'''
		return SalaryOffer(self, self.get_worker_value(self.get_skill_at(workers)))