import nn, learnBP, activateBP, display, random

def weight_init():
	return 0

def random_init():
	return (random.random() - 0.5) / 10

net = nn.LayeredNet()

iLayer = nn.Layer("input", None)
iLayer.add_neuron("top/bottom")
iLayer.add_neuron("white/black")
net.add_layer(iLayer)

oLayer = nn.Layer("output", activateBP.logistic_activation, learnBP.logistic_learn_ol, learnBP.clean)
oLayer.add_neuron()
oLayer.add_neuron()
oLayer.add_neuron()
oLayer.add_neuron()
oLayer.set_s(1)
net.add_layer(oLayer)
net.initialize(random_init)

IO1 = [((0, 0), (1, 1, 0, 0)), ((0, 1), (0, 0, 1, 1)), ((1, 0), (1, 1, 0, 0))]
IOTest = [((1, 1), (0, 0, 1, 1))]

learnArgs = {"learn rate": 0.11}
print net.learn_back(IO1, 2000, learnArgs, IOTest, 0.05)

print net.sim((1, 1))

#displays IO1 + (1, 1)
#display.display_pics([net.sim(IO1[0][0]),
#					  net.sim(IO1[1][0]),
#					  net.sim(IO1[2][0]),
#					  net.sim((1, 1))], 2, 100)