import random

def learn_rule(self, other, args):
	return "delta weight other -> self, args"

def activate(self, inVal):
	return "sum(in), e.g."

def clean(self):
	return None #, but clean temporary learning data

class Neuron:

	def __init__(self, name, actRule, learnRule = None, cleanRule = None):
		self.name = name
		self.activation = 0
		self.calc_activation = actRule
		self.deltaW = learnRule
		self.cleanFunc = cleanRule
		self.weightV = {}
		self.learnData = {}
	
	def add_connection(self, other, weight):
		self.weightV[other] = weight
	
	def remove_connection(self, other):
		del self.weightV[other]
	
	def input_sum(self):
		sum = 0
		for input in self.weightV:
			sum += input.activation * self.weightV[input]
		return sum
	
	def activate(self):
		self.activation = self.calc_activation(self, self.input_sum())
		return self.activation
	
	def learn(self, args):
		if self.deltaW:
			for input in self.weightV:
				self.weightV[input] += self.deltaW(self, input, args)
	
	def clean(self):
		if self.cleanFunc:
			self.cleanFunc(self)

class Layer:
	
	def __init__(self, name, actRule, learnRule = None, cleanRule = None):
		self.name = name
		self.neurons = []
		self.neurons.append(Neuron(name + " bias", lambda s, x: 1))
		self.input = None
		self.output = None
		self.actRule = actRule
		self.learnRule = learnRule
		self.cleanRule = cleanRule
	
	def size(self):
		return len(self.neurons) - 1
	
	def add_neuron(self, name=None):
		if name:
			self.neurons.append(Neuron(name, self.actRule, self.learnRule, self.cleanRule))
		else:
			self.neurons.append(Neuron(self.name + " " + str(len(self.neurons) - 1), self.actRule, self.learnRule, self.cleanRule))
	
	def define_input(self, layer):
		self.input = layer
	
	def define_output(self, layer):
		self.output = layer
	
	def initialize(self, weightFunc):
		if not self.input:
			print self.name + ": Nothing to initialize: no input layer"
		else:
			for neuron in self.neurons:
				for iNeuron in self.input.neurons:
					neuron.add_connection(iNeuron, weightFunc())
	
	def set_activations(self, vector, start = 1):
		self.neurons[0].activate()
		for i in range(start, len(self.neurons)):
			self.neurons[i].activation = vector[i - start]
	
	def calc_activations(self):
		for neuron in self.neurons:
			neuron.activate()
	
	def learn(self, args):
		for neuron in self.neurons:
			neuron.learn(args)
	
	def clean(self):
		for neuron in self.neurons:
			neuron.clean()
	
	def activations_as_list(self):
		activations = []
		for neuron in self.neurons:
			activations.append(neuron.activation)
		return activations
	
	def weights_as_matrix(self):
		weights = []
		if self.input:
			inputOrdering = self.input.neurons
		else:
			inputOrdering = []
		for neuron in self.neurons[1:]:
			weights.append([])
			weights[-1].append(neuron.name)
			for input in inputOrdering:
				weights[-1].append(neuron.weightV[input])
		return weights
	
	def set_s(self, s):
		for neuron in self.neurons:
			neuron.s = s

class LearnMem:
	
	def __init__(self):
		self.mse = []
		self.consecIncreases = 0
	
	def update(self, mse):
		self.mse.append(mse)
		if len(self.mse) > 1:
			if self.mse[-1] > self.mse[-2]:
				self.consecIncreases += 1
			else:
				self.consecIncreases = 0
		
	def __str__(self):
		i = 0
		s = ""
		for mse in self.mse:
			s += str(round(mse, 2)) + "\n"
			if i % 20 == 0:
				s += "Step " + str(i) + "\n"
			i += 1
		if hasattr(self, "reason"):
			s += self.reason
		return s

class LayeredNet:
	
	def __init__(self):
		self.layers = []
	
	def add_layer(self, layer):
		if self.layers:
			last = self.layers[-1]
			last.define_output(layer)
			layer.define_input(last)
		self.layers.append(layer)
	
	#this can also be done manually by layer
	def initialize(self, weightFunc):
		for layer in self.layers:
			layer.initialize(weightFunc)
	
	def get_output(self):
		return self.layers[-1].activations_as_list()[1:]
	
	def sim(self, input):
		for layer in self.layers:
			if layer.input:
				layer.calc_activations()
			elif layer.size() == len(input):
				layer.set_activations(input)
			else:
				raise Exception("Layer is input and input is wrong size")
		return self.get_output()
	
	
	def mse(self, testIO):
		se = 0
		for input, output in testIO:
			self.sim(input)
			n = 0
			for neuron in self.layers[-1].neurons[1:]:
				se += (output[n] - neuron.activation) ** 2
				n += 1
		return se / (len(testIO) * len(self.layers[-1].neurons[1:]))
		
	def learning_done(self, testIO, threshold):
		if self.mse(testIO) < threshold:
			return True
		
	
	def learn_back(self, IO, cycles, args, testIO = [], threshold = 0.1, maxIncreases = 25):
		learnRep = LearnMem()
		for i in range(cycles):
			random.shuffle(IO) 
			if testIO:
				random.shuffle(testIO)
				mse = self.mse(testIO)
				learnRep.update(mse)
				if mse < threshold:
					learnRep.reason = "Under mse threshold"
					return learnRep
				elif learnRep.consecIncreases > maxIncreases:
					learnRep.reason = "mse consecutive increases"
					return learnRep
			for input, output in IO:
				self.sim(input)
				n = 0
				for neuron in self.layers[-1].neurons[1:]:
					neuron.learnData["predicted"] = output[n]
					n += 1
				layer = len(self.layers) - 1
				while layer >= 0:
					self.layers[layer].learn(args)
					args["last layer"] = self.layers[layer]
					layer -= 1
				layer = len(self.layers) - 1
				while layer >= 0:
					self.layers[layer].clean()
					layer -= 1
		return learnRep
	
	def str(self):
		s = ""
		for layer in self.layers:
			s += layer.name + "\n"
			weightMatrix = layer.weights_as_matrix()
			if weightMatrix:
				for neuron in weightMatrix:
					s += neuron[0] + ":  "
					for weight in neuron[1:]:
						s += str(round(weight, 2))
						s += "  "
					s += "\n"
			s += "\n"
		return s