import nn, learnBP, activateBP, display, random

def weight_init():
	return (random.random() - 0.5) / 2
	
net = nn.LayeredNet()

iLayer = nn.Layer("input", None)
iLayer.add_neuron("square/circle")
iLayer.add_neuron("white/black")
net.add_layer(iLayer)

n = 4
while n < 16:
	hLayer = nn.Layer("Hidden: size = " + str(n), activateBP.logistic_activation, learnBP.logistic_learn_hl, learnBP.clean)
	for i in range(n):
		hLayer.add_neuron()
	hLayer.set_s(4)
	net.add_layer(hLayer)
	n *= 2

n = 16
oLayer = nn.Layer("output", activateBP.logistic_activation, learnBP.logistic_learn_ol, learnBP.clean)
for i in range(n):
	oLayer.add_neuron()
oLayer.set_s(0.5)
net.add_layer(oLayer)
net.initialize(weight_init)

outputs = [(0, 1, 1, 0,
		    1, 0, 0, 1,
		    1, 0, 0, 1,
		    0, 1, 1, 0),
		    (1, 1, 1, 1,
		    1, 0, 0, 1,
		    1, 0, 0, 1,
		    1, 1, 1, 1),
		    (1, 0, 0, 1,
		    0, 1, 1, 0,
		    0, 1, 1, 0,
		    1, 0, 0, 1),
		    (0, 0, 0, 0,
		    0, 1, 1, 0,
		    0, 1, 1, 0,
		    0, 0, 0, 0)]

trainset = [((0, 0), outputs[2]), ((1, 0), outputs[3]), ((0, 1), outputs[0])]
testIO = [((1, 1), (outputs[1]))] + trainset

learnArgs = {"learn rate": 0.31}
print net.learn_back(trainset, 2000, learnArgs, testIO = testIO, threshold = 0.01, maxIncreases = 100)

print net.sim(testIO[0][0])

for io in trainset:
	print io[0]
display.display_pics([net.sim(trainset[0][0]),
					  net.sim(trainset[1][0]),
					  net.sim(trainset[2][0]),
					  net.sim(testIO[0][0])], 4, 30)