import random

#adds a little noise
def randomize(l):
	return [random.gauss(elt, 0.2) for elt in l]

#200 points of normal data - near [1, 2, 3]
#200 points of anomaly 1 - near [1, 2, 1]
#200 points of anomaly 2 - near [1, 1, 3]
data = [randomize([1, 2, 3]) for i in range(200)] + [randomize([1, 2, 1]) for i in range(200)] + [randomize([1, 1, 3]) for i in range(200)]

#prints data elements near the start of the first anomaly
print data[190:210]

class FeatureExtractor:
	
	#this is an abstract class
	
	def getValue(dataElement):
		raise Exception("Method not implemented")

class SingleValueExtractor(FeatureExtractor):
	
	#this is a subclass which returns a single value in a list
	
	def __init__(self, i):
		self.i = i #i is the index of the value to return
	
	def getValue(dataElement):
		return dataElement[i]

featureExtractors = [SingleValueExtractor(0), SingleValueExtractor(1), SingleValueExtractor(2)]
'''
The above variable is a list of three feature extractors, each of which returns one element of a three element list. 

So for the data element [1, 2, 3], the first featureExtractor's getValue() would return 1, the second's would return 2, and the third's 3.

Using these, we can run A-distance once for each feature extractor and get three streams of results. e.g.:

Feature 1: 1, 1, 1, 1, 1, 1, 0, 0, 0 - anomaly in feature 1
Feature 2: 17, 16.9, 16.9, 16.9, 17, 17.1, 4.2, 3.9, 4.1 - anomaly in feature 2.
Feature 3: -3, -3, -3, -3, -3, -3, -3, -3, -3, -3, -3, -3 - no anomaly in feature 3.

NOTE: you should be able to use the 'data' and 'featureExtractors' values in this file as arguments to your getDistanceValues() methods (with an instance of your DCClass being the third argument.
'''