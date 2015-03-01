import server, threading, time, td2 as td, random

class RandomMessager:

	msgChance = 0.2
	stopInc = 0.1
	
	rxStr = "RX - "
	txStr = "TX - "
	endAddrStr = " | "
	ackStr = "ack received "
	inactiveStr = "inactive "
	haltMsg = "HALT"

	def __init__(self, addrs, i, ids, srcAddr = 0):
		self.td = td.TD(addrs, i, False)
		self.addr = addrs[i]
		self.addrs = [addr for addr in addrs if addr != self.addr]
		self.srcAddr = self.addrs[srcAddr]
		self.id = ids[i]
		self.stopChance = 0.0
		self.msgi = 0
		
		self.reportAddrs = [(addr[0], addr[1] + 5) for addr in addrs]
		td.printRed(self.addrs, self.reportAddrs)
		self.reportChannel = server.FIFOChannel(list(self.reportAddrs), i)
		self.reportChannel.connect()
		self.awaitLock = threading.Lock()
		self.stopEvent = threading.Event()
		
		self.ackListenThread = threading.Thread(target = self.listenForAcks)
		self.msgListenThread = threading.Thread(target = self.listenForMsgs)
		self.randomMsgThread = threading.Thread(target = self.randomlyMessage)
		self.ackListenThread.start()
		self.msgListenThread.start()
		self.randomMsgThread.start()
	
	def normalToReport(self, addr):
		return (addr[0], addr[1] + 5)
	
	def reportToNormal(self, addr):
		return (addr[0], addr[1] - 5)
	
	def strToAddr(self, s):
		firstQuote = s.index("'")
		secondQuote = s.index("'", firstQuote + 1)
		portStart = s.index(",", secondQuote) + 1
		portEnd = s.index(")", portStart)
		addr = (s[firstQuote + 1:secondQuote], int(s[portStart:portEnd]))
		return addr
	
	def getAddr(self, msg):
		if self.endAddrStr not in msg:
			return None
		return self.strToAddr(msg[:msg.index(self.endAddrStr)])
	
	def reportTx(self, dest, msg):
		self.reportChannel.sendMsg(self.normalToReport(self.srcAddr), self.txStr + str(self.normalToReport(dest)) + self.endAddrStr + msg)
	
	def reportRx(self, src, msg):
		self.reportChannel.sendMsg(self.normalToReport(self.srcAddr), self.rxStr + str(self.normalToReport(src)) + self.endAddrStr + msg)
	
	def reportAck(self):
		self.reportChannel.sendMsg(self.normalToReport(self.srcAddr), self.ackStr)
	
	def reportInactive(self):
		self.reportChannel.sendMsg(self.normalToReport(self.srcAddr), self.inactiveStr)
	
	def listenForAcks(self):
		while not self.stopEvent.isSet():
			if self.td.rcvAck():
				#td.printBlue("got Ack at", self.addr)
				self.awaitLock.acquire()
				self.reportAck()
				self.awaitTesterAck()
				self.awaitLock.release()
				self.td.rxqLock.acquire()
				self.td.unAcked -= 1
				if not self.td.active and self.td.unAcked == 0 and not self.td.isSource:
					td.printBlue("sending Ack to engager from", self.addr, "to", self.td.engager, "and setting engager to none")
					self.td.sendAck(self.td.engager)
					self.td.engager = None
				self.td.rxqLock.release()
			else:
				time.sleep(0.5)
	
	def listenForMsgs(self):
		while not self.stopEvent.isSet():
			#td.printBlue("listening at", self.addr)
			msg, addr = self.td.rcv()
			#td.printBlue("got msg at", self.addr)
			if msg == self.haltMsg:
				self.stopEvent.set()
				break
			#td.printBlue("got", msg, "at", self.addr)
			self.awaitLock.acquire()
			self.reportRx(addr, msg)
			self.awaitTesterAck()
			self.td.rxqLock.acquire()
			self.td.active = True
			if self.td.engager or self.td.isSource:
				#td.printRed("sending Ack from", self.addr, "to", addr)
				self.td.sendAck(addr)
			else:
				td.printBlue("Setting engager to", addr, "because current engager is", self.td.engager, "and got a message")
				self.td.engager = addr
			self.td.rxqLock.release()	
			self.awaitLock.release()
			time.sleep(1)
		td.printBlue("Done listening for messages at", self.addr)
		self.ackListenThread.join()
		td.printBlue("Done listening for acks at", self.addr)
		self.randomMsgThread.join()
		td.printBlue("Done sending messages at", self.addr)
		self.td.closeChannel()
		if not self.td.isSource:
			self.reportChannel.stop()
		td.printBlue("closing channel at", self.addr)
	
	def awaitTesterAck(self):
		while not self.stopEvent.isSet():
			msg = self.reportChannel.getMsg(self.normalToReport(self.srcAddr))
			if msg:
				if msg == self.haltMsg:
					self.stopEvent.set()
				break
			else:
				time.sleep(1)
	
	def randomlyMessage(self):
		addrs = [addr for addr in self.addrs]
		while not self.stopEvent.isSet():
			self.td.rxqLock.acquire()
			if not self.td.active:
				self.td.rxqLock.release()
				time.sleep(2)
			else:
				self.td.rxqLock.release()
				if random.random() < self.msgChance:
					addr = random.choice(addrs)
					msg = "random msg " + str(self.msgi) + " from " + str(self.id)
					#td.printBlue("sending", msg, "to", addr)
					self.msgi += 1
					self.awaitLock.acquire()
					self.reportTx(addr, msg)
					self.awaitTesterAck()
					self.td.tx(addr, msg)
					self.awaitLock.release()
					self.stopChance += self.stopInc
					#td.printBlue("stopchance at", self.addr, "=", self.stopChance)
				elif random.random() < self.stopChance:
					self.td.rxqLock.acquire()
					if not self.td.active:
						self.td.rxqLock.release()
					else:
						self.td.rxqLock.release()
						self.awaitLock.acquire()
						self.reportInactive()
						self.awaitTesterAck()
						self.td.rxqLock.acquire()
						#td.printRed("inactive at", self.addr, "acks =", self.td.unAcked)
						self.td.active = False
						if self.td.unAcked == 0 and not self.td.isSource:
							self.td.sendAck(self.td.engager)
							td.printBlue("setting engager to None at", self.addr, "because going inactive and no acks")
							self.td.engager = None
						self.td.rxqLock.release()
						self.awaitLock.release()
				time.sleep(1)

class State:
	
	def __init__(self, addrs = None, srcid = None, previousState = None):
		if not previousState:
			self.src = srcid
			self.txs = {addr1: {addr2: [] for addr2 in addrs if addr2 != addr1} for addr1 in addrs}
			self.rcvs = {addr1: {addr2: [] for addr2 in addrs if addr2 != addr1} for addr1 in addrs}
			self.active = {addr: True if addr == srcid else False for addr in addrs}
			#src engager set to none for easier processing later.
			self.engagers = {addr: None for addr in addrs}
			self.unAcked = {addr: 0 for addr in addrs}
		else:
			self.src = previousState.src
			self.txs = {}
			for key, val in previousState.txs.items():
				self.txs[key] = dict(val)
			self.rcvs = {}
			for key, val in previousState.rcvs.items():
				self.rcvs[key] = dict(val)
			self.active = dict(previousState.active)
			#src engager set to none for easier processing later.
			self.engagers = dict(previousState.engagers)
			self.unAcked = dict(previousState.unAcked)
	
	def prefix(self, prefix, lst):
		for i in range(len(prefix)):
			if len(lst) <= i or lst[i] != prefix[i]:
				return False
		return True
	
	def isOutTree(self):
		runningAddrs = {addr for addr in self.active if self.active[addr] or self.unAcked[addr] > 0}
		nodesInTree = set()
		newAdds = set()
		if self.active[self.src] or self.unAcked[self.src] > 0:
			nodesInTree.add(self.src)
			newAdds.add(self.src)
		while True:
			added = False
			nextSet = set()
			for addr, engager in self.engagers.items():
				if engager in newAdds:
					if addr in nodesInTree:
						td.printYellow("Failure: cycle in tree at", addr)
					nextSet.add(addr)
					added = True
			nodesInTree = nodesInTree.union(newAdds)
			newAdds = nextSet
			if not added:
				break
		if nodesInTree != runningAddrs:
			td.printYellow("Failure: running nodes are:", runningAddrs, "; nodes in tree are:", nodesInTree)
	
	def tx(self, msg, src, dest):
		if not self.active[src]:
			td.printYellow("Failure: system", src, "sending message but is inactive.")
		if src == dest:
			td.printYellow("Failure: system", src, "sending message to itself")
		self.txs[src][dest].append(msg)
		self.unAcked[src] += 1
		self.isOutTree()
	
	def rx(self, msg, src, dest):
		self.rcvs[src][dest].append(msg)
		if not self.prefix(self.rcvs[src][dest], self.txs[src][dest]):
			td.printYellow("Failure: system", dest, "receiving message from", src, "that has not been reported as sent.")
		if not self.engagers[dest] and dest != self.src:
			self.engagers[dest] = src
		self.active[dest] = True
		self.isOutTree()
	
	
	def sentAck(self, src):
		pass
	
	def receivedAck(self, src):
		self.unAcked[src] -= 1
		if self.unAcked[src] == 0 and not self.active[src]:
			self.engagers[src] = None
		self.isOutTree()
	
	def inactivated(self, src):
		if not self.active[src]:
			td.printYellow("Failure: system", src, "inactivating but is already inactive.")
		self.active[src] = False
		if self.unAcked[src] == 0:
			self.engagers[src] = None
		self.isOutTree()
	
	def __str__(self):
		s = "\ntx history:\n"
		s += str(self.txs) + "\n"
		s += "rx history:\n"
		s += str(self.rcvs) + "\n"
		s += "active:\n"
		s += str(self.active)
		s += "\nunAcked:\n"
		s += str(self.unAcked)
		return s

class SrcRandomMessager(RandomMessager):
	
	def __init__(self, addrs, i, ids, tester):
		self.td = td.TD(addrs, i, True)
		self.addr = addrs[i]
		self.addrs = [addr for addr in addrs if addr != self.addr]
		td.printRed(self.addrs)
		self.id = ids[i]
		self.stopChance = 0.0
		self.msgi = 0
		
		self.stopEvent = threading.Event()
		self.awaitLock = threading.Lock()
		self.tester = tester
		
		self.ackListenThread = threading.Thread(target = self.listenForAcks)
		self.msgListenThread = threading.Thread(target = self.listenForMsgs)
		self.randomMsgThread = threading.Thread(target = self.randomlyMessage)
		self.ackListenThread.start()
		self.msgListenThread.start()
		self.randomMsgThread.start()
	
	def halt(self):
		self.td.rxqLock.acquire()
		self.td.rxq.insert(0, (self.haltMsg, self.addr))
		self.td.rxqLock.release()
	
	def terminated(self):
		return self.td.isTerminated()
	
	def reportTx(self, dest, msg):
		td.printRed("Got Tx from", self.id, "to", dest)
		self.tester.reportTx(msg, self.addr, dest)
	
	def reportRx(self, src, msg):
		td.printRed("Got Rx from", src, "to", self.id)
		self.tester.reportRx(msg, src, self.addr)
	
	def reportAck(self):
		td.printRed("Got Ack received from", self.id)
		self.tester.reportAckReceived(self.addr)
	
	def reportInactive(self):
		td.printRed("Got Inactive from", self.id)
		self.tester.reportInactive(self.addr)
	
	def awaitTesterAck(self):
		pass

class Tester:
	
	rxStr = "RX - "
	txStr = "TX - "
	endAddrStr = " | "
	ackStr = "ack received "
	inactiveStr = "inactive "
	haltMsg = "HALT"
	
	def __init__(self, addrs, i, ids):
		self.addrs = addrs
		self.addr = addrs[i]
		self.id = ids[i]
		self.idDict = {addrs[i]: ids[i] for i in range(len(addrs))}
		
		self.reportAddrs = [(addr[0], addr[1] + 5) for addr in addrs]
		td.printRed(self.reportAddrs)
		self.reportChannel = server.FIFOChannel(list(self.reportAddrs), i)
		self.reportChannel.connect()

		self.states = []
		self.states.append(State(self.idDict.values(), self.id))
		self.stateLock = threading.Lock()
		
		self.pauseLock = threading.Lock()
		self.paused = threading.Event()
		self.paused.set()
		self.step = 0
		self.halted = threading.Event()
		receiveThread = threading.Thread(target = self.receiveMsgs)
		receiveThread.start()
	
	def receiveMsgs(self):
		step = 0
		while not self.halted.is_set():
			while self.paused.is_set():
				time.sleep(0.5)
			msg = self.reportChannel.getAnyMsg()
			#td.printRed(msg)
			if msg:
				msg, addr = msg
				step += 1
				td.printRed("got", msg, "from", addr)
				if msg.startswith(self.txStr):
					dest = msg[len(self.txStr):msg.index(self.endAddrStr)]
					self.reportTx(msg[msg.index(self.endAddrStr) + len(self.endAddrStr):], self.reportToNormal(addr), self.reportToNormal(self.strToAddr(dest)))
					self.ack(addr)
				elif msg.startswith(self.rxStr):
					src = msg[len(self.rxStr):msg.index(self.endAddrStr)]
					self.reportRx(msg[msg.index(self.endAddrStr) + len(self.endAddrStr):], self.reportToNormal(self.strToAddr(src)), self.reportToNormal(addr))
					self.ack(addr)
				elif msg.startswith(self.inactiveStr):
					self.reportInactive(self.reportToNormal(addr))
					self.ack(addr)
				elif msg.startswith(self.ackStr):
					#print "ack received report received."
					self.reportAckReceived(self.reportToNormal(addr))
					self.ack(addr)
				if step % 10 == 0:
					self.printState()
			else:
				if self.localMessager.terminated():
					self.halted.set()
				else:
					time.sleep(1)
		for addr in self.addrs:
			if addr != self.addr:
				print "sending halt message to", addr
				self.localMessager.td.tx(addr, self.haltMsg)
		self.localMessager.halt()
		self.reportChannel.stop()
		self.printState()
		
	def setLocalMessager(self, messager):
		self.localMessager = messager
		print "local set"
		self.paused.clear()
	
	def pause(self):
		self.paused.set()
	
	def unpause(self):
		self.paused.clear()
	
	def ack(self, addr):
		self.reportChannel.sendMsg(addr, "ACK")
	
	def id(self, reportAddr):
		return self.idDict[self.reportToNormal(reportAddr)]
	
	def reportRx(self, msg, src, dest):
		self.stateLock.acquire()
		self.states.append(State(previousState = self.states[-1]))
		self.states[-1].rx(msg, self.idDict[src], self.idDict[dest])
		self.stateLock.release()
	
	def reportTx(self, msg, src, dest):
		self.stateLock.acquire()
		self.states.append(State(previousState = self.states[-1]))
		self.states[-1].tx(msg, self.idDict[src], self.idDict[dest])
		self.stateLock.release()
	
	def reportInactive(self, src):
		self.stateLock.acquire()
		self.states.append(State(previousState = self.states[-1]))
		self.states[-1].inactivated(self.idDict[src])
		self.stateLock.release()	
	
	def reportAckReceived(self, src):
		self.stateLock.acquire()
		self.states.append(State(previousState = self.states[-1]))
		self.states[-1].receivedAck(self.idDict[src])
		self.stateLock.release()
	
	def normalToReport(self, addr):
		return (addr[0], addr[1] + 5)
	
	def reportToNormal(self, addr):
		return (addr[0], addr[1] - 5)
	
	def strToAddr(self, s):
		firstQuote = s.index("'")
		secondQuote = s.index("'", firstQuote + 1)
		portStart = s.index(",", secondQuote) + 1
		portEnd = s.index(")", portStart)
		addr = (s[firstQuote + 1:secondQuote], int(s[portStart:portEnd]))
		return addr
	
	def getAddr(self, msg):
		if self.endAddrStr not in msg:
			return None
		return self.strToAddr(msg[:msg.index(self.endAddrStr)])
	
	def printState(self, i = -1):
		self.stateLock.acquire()
		state = self.states[i]
		td.printBlue(str(state))
		self.stateLock.release()
	
	def halt(self):
		self.halted.set()

def test():
	addrs = [('Matthews-MacBook-Pro-2.local', 20003), ('Matthews-MacBook-Pro-2.local', 30003), ('Matthews-MacBook-Pro-2.local', 40003), ('Matthews-MacBook-Pro-2.local', 50003)]
	ids = ["source", "messenger1", "messenger2", "messenger3"]
	msg1 = RandomMessager(addrs, 1, ids, srcAddr = 0)
	msg2 = RandomMessager(addrs, 2, ids, srcAddr = 0)
	msg3 = RandomMessager(addrs, 3, ids, srcAddr = 0)
	tester = Tester(addrs, 0, ids)
	src1 = SrcRandomMessager(addrs, 0, ids, tester)
	tester.setLocalMessager(src1)

def erewhon():
	addrs = [('erewhon', 20003), ('erewhon', 30003), ('metacog', 40003), ('metacog', 50003)]
	ids = ["source", "erewhon1", "metacog1", "metacog2"]
	tester = Tester(addrs, 0, ids)
	src = SrcRandomMessager(addrs, 0, ids, tester)
	msg1 = RandomMessager(addrs, 1, ids, srcAddr = 0)
	tester.setLocalMessager(src)

def metacog():
	addrs = [('erewhon', 20003), ('erewhon', 30003), ('metacog', 40003), ('metacog', 50003)]
	ids = ["source", "erewhon1", "metacog1", "metacog2"]
	msg1 = RandomMessager(addrs, 2, ids, srcAddr = 0)
	msg2 = RandomMessager(addrs, 3, ids, srcAddr = 0)

def start(addrs, ids, machine, srci):
	for i in range(len(addrs)):
		if addrs[i][0] == machine:
			if i == srci:
				tester = Tester(addrs, i, ids)
				messager = SrcRandomMessager(addrs, i, ids, tester)
				tester.setLocalMessager(messager)
			else:	
				RandomMessager(addrs, i, ids, srci)

#example setup 1: erewhon and metacog machines on mcl cluster:

addrs = [('erewhon', 20003), ('erewhon', 30003), ('metacog', 40003), ('metacog', 50003)] 
ids = ["source", "erewhon1", "metacog1", "metacog2"]
srci = 0

#example setup 2: 4 addresses on my laptop

addrs = [('Matthews-MacBook-Pro-2.local', 20003), ('Matthews-MacBook-Pro-2.local', 30003), ('Matthews-MacBook-Pro-2.local', 40003), ('Matthews-MacBook-Pro-2.local', 50003)]
ids = ["source", "messenger1", "messenger2", "messenger3"]
srci = 0

#fill in example 3: grace machines

addrs = [('gracename', port), ('gracename', port)...]
ids = ["id1", "id2",...] #same length as addrs
srci = 0 #index of address at which tester operates & src for td.

#test()
if __name__ == "__main__":
	import socket
	machine = socket.gethostname()
	start(addrs, ids, machine, srci)
		