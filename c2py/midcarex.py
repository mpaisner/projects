from readLog import *
import threading, time, sys

def runMidcaRex(trexCommand, argsBesidesCFGPath, defaultCFGPath, newCFGPath, logPath, runSteps, secondRunSteps):
	'''
	assumes the name of the reactor whose lookahead will be changed is 'test'. New lookahead is set to 60.
	'''
	tRex = shellCommand([trexCommand] + argsBesidesCFGPath + [defaultCFGPath])
	'''
	traceLock = threading.Lock()
	trace = ""
	checkingThread = threading.Thread(target = continuouslyCheck, args = (trace, logPath, traceLock))
	checkingThread.start()
	'''
	time.sleep(1)
	for step in range(runSteps):
		tRex.stdin.write("n\n")
		time.sleep(0.1)
		'''
		traceLock.acquire()
		myTrace = trace
		trace = ""
		traceLock.release()
		if myTrace:
			print "MIDCA reading trace"
		time.sleep(0.3)
		'''
	try:
		tRex.kill()
	except Exception:
		print "t-rex appears to have already stopped on its own."
	time.sleep(1) #in case T-rex is using files
	txt = getLinesIfOpen(logPath)
	if not txt:
		print "unable to read log file"
	print "MIDCA read log file."
	print str(getNumRejected(lines)), "goals rejected."
	
	print "changing cfg file...",
	newCFGchangeLookahead(defaultCFGPath, newCFGPath, 'test', 1)
	newCFGchangeLookahead(newCFGPath, newCFGPath, 'test2', 1)
	print "changed."
	time.sleep(1) #just in case
	tRex = shellCommand([trexCommand] + argsBesidesCFGPath + [defaultCFGPath])
	for step in range(secondRunSteps):
		tRex.stdin.write("n\n")
		time.sleep(0.1)
	try:
		tRex.kill()
	except Exception:
		print "t-rex appears to have already stopped on its own."
	
	time.sleep(1) #in case T-rex is using files
	txt = getLinesIfOpen(logPath)
	if not txt:
		print "unable to read log file"
	print "MIDCA read log file."
	print str(getNumRejected(lines)), "goals rejected."
	print "MIDCA stopping."

if __name__ == "__main__":
	runMidcaRex(trexCommand, argsBesidesCFGPath, defaultCFGPath, newCFGPath, logPath, runSteps, secondRunSteps)
	#These should be something like, but not exactly:
	#runMidcaRex('amc', [], 'cfgFolder/light.cfg', 'cfgFolder/light2.cfg', 'logFolder/log.txt', 80, 80)
	
	#argsBesidesCFGPath is in case there need to be arguments to trex before the cfg file.