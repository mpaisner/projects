import time

t = time.time()
i = 0 
while t + 2 > time.time():
	i += 1

print i