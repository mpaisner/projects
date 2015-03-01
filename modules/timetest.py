import datetime, time, random, math

ints = [4 for i in range(100000)]
floats = [random.random() for i in range(1000000)]
floats2 = [random.random() for i in range(1000000)]

t1 = datetime.datetime.today()

total = 0
for i in range(len(floats)):
	total += floats[i] * floats2[i]

t2 = datetime.datetime.today()

print "time: ", (t2 - t1).total_seconds(), total