import re, subprocess, os, time

def getSteps(lines):
	steps = {}
	for line in lines:
		if re.match("^\[(\d)*\]", line):
			step = int(line[line.index("[") + 1:line.index("]")])
			if step not in steps:
				steps[step] = []
			steps[step].append(line[line.index("]") + 1:])

	return steps

def parseSource(msg):
	srcNameStart = msg.index("[") + 1
	srcNameEnd = msg.index("]")
	srcName = msg[srcNameStart:srcNameEnd]
	return srcName, msg[srcNameEnd + 1:]

def parseReactors(steps):
	newSteps = {}
	for step, msgs in steps.items():
		newSteps[step] = {}
		for msg in msgs:
			reactorName, msg = parseSource(msg)
			if reactorName not in newSteps[step]:
				newSteps[step][reactorName] = []
			newSteps[step][reactorName].append(msg)
	return newSteps

def getUpdates(steps):
	updates = {}
	for step, packets in steps.items():
		updates[step] = {}
		for src, msgs in packets.items():
			updateMsgs = [msg[7:].strip() for msg in msgs if msg.startswith("ASSERT")]
			if updateMsgs:
				updates[step][src] = updateMsgs
	return updates

def getNumRejected(lines):
	steps = getSteps(f)
	num = 0
	for step, msgs in steps.items():
		for msg in msgs:
			if "REJECTED" in msg:
				steps += 1
	return steps

def getNodeName(fullName):
	try:
		return fullName[fullName.index(".") + 1:fullName.index(".", fullName.index(".") + 1)]
	except ValueError:
		try:
			return fullName[fullName.index(".") + 1:]
		except ValueError:
			return fullName
			

def changeLookahead(s, nodeName, val):
	i = s.index("Reactor name=\"" + nodeName + "\"")
	i = s.index("lookahead", i)
	firstQuote = s.index("\"", i)
	secondQuote = s.index("\"", firstQuote + 1)
	return s[:firstQuote + 1] + str(val) + s[secondQuote:]


def newCFGchangeLookahead(oldfile, newfile, nodeName, lookahead):
	f = open(oldfile)
	s = f.read()
	f.close()
	newS = changeLookahead(s, nodeName, lookahead)
	f = open(newfile, 'w')
	f.write(newS)
	f.close()

def getLinesIfOpen(filename):
	try:
		f = open(filename)
		txt = f.readlines()
		f.close()
		return txt
	except IOError:
		return ""

def getTextIfOpen(filename):
	try:
		f = open(filename)
		txt = f.read()
		f.close()
		return txt
	except IOError:
		return ""
		
def shellCommand(cmd):
	return subprocess.Popen(cmd, shell = True, stdin = subprocess.PIPE)

def continuouslyCheck(sharedVar, filename, lock):
	lastTime = -10000
	while True:
		if not os.path.exists(filename):
			lock.acquire()
			if sharedVar == "DONE":
				break	
			lock.release()
		else:
			t = os.path.getmtime(filename)
			if t > lastTime:
				lastTime = t
				txt = getTextIfOpen(filename)
				lock.acquire()
				if sharedVar == "DONE":
					break
				else:
					sharedVar = txt
				lock.release()
		time.sleep(0.4)
			

