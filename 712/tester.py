import td, threading, time, random

class RandomMessager:
	
	stopMsg = "HALT"
	msg = "Message: "
	rxStr = "RX - "
	txStr = "TX - "
	ackStr = "ACK - "
	endAddrStr = " | "
	msgProb = 0.1
	inactiveInc = 0.02
	
	def __init__(self, ids, addrs, i, isSource = False, testing = False, testAddr = 0):
		self.td = td.TD(addrs, i, isSource, testing, id = ids[i])
		self.addrs = [addr for addr in addrs if addr != addrs[i]]
		self.nextMsg = None
		self.msgLock = threading.Lock()
		self.msgi = 0
		self.testAddr = addrs[testAddr]
		self.awaitingAck = False
		self.id = ids[i]
		self.inactiveChance = 0
		sendThread = threading.Thread(target = self.randomlyCorrespond)
		#sendThread.daemon = True
		receiveThread = threading.Thread(target = self.doRx)
		#receiveThread.daemon = True
		sendThread.start()
		receiveThread.start()
		
	def awaitAck(self):
		'''
		assumed only one thread is in this method at once. Also, since only
		Ack messages will come to non-test servers, and since the test
		server will never await an ack, this method assumes all incoming
		test message are acks.
		'''
		msg, addr = self.td.getTestMsg()
		if not msg.startswith(self.ackStr):
			raise Exception("expected ACK, got " + str(msg))
	
	def randomlyCorrespond(self):
		while True:
			self.td.rxqLock.acquire()
			if not self.td.active:
				self.td.rxqLock.release()
				time.sleep(2)
				continue
			self.td.rxqLock.release()
			if random.random() < self.msgProb:
				dest = random.choice([addr for addr in self.addrs if addr != self.testAddr])
				msg = self.msg + str(self.id) + ":" + str(self.msgi)
				self.msgi += 1
				#self.reportTx(dest, msg)
				self.td.tx(dest, msg)
			self.td.rxqLock.acquire()
			if random.random() < self.inactiveChance and self.td.active:
				self.td.rxqLock.release()
				self.td.inactive()
			else:
				self.td.rxqLock.release()
			self.msgLock.acquire()
			if self.nextMsg:
				#print "got message", self.nextMsg
				self.nextMsg = None
			self.msgLock.release()
			self.inactiveChance += self.inactiveInc
			time.sleep(1)
	
	def reportRx(self, src, msg):
		self.td.sendTestMsg(self.testAddr, self.rxStr + str(src) + self.endAddrStr + msg)
	
	def reportTx(self, dest, msg):
		self.td.sendTestMsg(self.testAddr, self.txStr + str(dest) + self.endAddrStr + msg)
	
	def ack(self, addr, msg):
		#td.printRed("Acking", addr, self.ackStr + msg)
		self.td.sendTestMsg(addr, self.ackStr + msg, False)
	
	def doRx(self):
		while True:
			self.msgLock.acquire()
			if not self.nextMsg:
				self.msgLock.release()
				msg, addr = self.td.rx()
				if not msg or msg.startswith(self.stopMsg):			
					self.td.closeChannel()
					break
				#print "reporting rx"
				#self.reportRx(addr, msg)
				self.msgLock.acquire()
				self.nextMsg = msg
				self.msgLock.release()
			else:
				self.msgLock.release()
			time.sleep(1)

class State:
	
	def __init__(self, addrs = None, srcid = None, previousState = None):
		if not previousState:
			self.txs = {addr1: {addr2: [] for addr2 in addrs if addr2 != addr1} for addr1 in addrs}
			self.rcvs = {addr1: {addr2: [] for addr2 in addrs if addr2 != addr1} for addr1 in addrs}
			self.active = {addr: True if addr == srcid else False for addr in addrs}
			self.unAcked = {addr: 0 for addr in addrs}
		else:
			self.txs = {}
			for key, val in previousState.txs.items():
				self.txs[key] = dict(val)
			self.rcvs = {}
			for key, val in previousState.rcvs.items():
				self.rcvs[key] = dict(val)
			self.active = dict(previousState.active)
			self.unAcked = dict(previousState.unAcked)
	
	def tx(self, msg, src, dest):
		self.txs[src][dest].append(msg)
		self.unAcked[src] += 1
	
	def rx(self, msg, src, dest):
		self.rcvs[src][dest].append(msg)
		self.active[dest] = True
	
	def sentAck(self, src):
		pass
	
	def receivedAck(self, src):
		self.unAcked[src] -= 1
	
	def inactivated(self, src):
		self.active[src] = False
	
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

class SourceMessager(RandomMessager):
	
	def __init__(self, ids, addrs, i):
		self.td = td.TD(addrs, i, True, True, id = ids[i])
		self.addrs = [addr for addr in addrs if addr != addrs[i]]
		self.nextMsg = None
		self.msgLock = threading.Lock()
		self.msgi = 0
		self.testAddr = self.td.addr
		self.id = ids[i]
		self.inactiveChance = 0
		self.srci = i
		self.idDict = {str(addrs[i]): ids[i] for i in range(len(addrs))}
		self.testerSetup(addrs, i)
		sendThread = threading.Thread(target = self.startAll)
		receiveThread = threading.Thread(target = self.doRx)
		#receiveThread.daemon = True
		sendThread.start()
		receiveThread.start()
		
	def testerSetup(self, ids, srcId):
		self.states = []
		self.states.append(State(self.idDict.values(), self.id))
		self.stateLock = threading.Lock()
		
		self.pauseLock = threading.Lock()
		self.paused = False
		self.step = 0
		self.halted = False
	
	def reportRx(self, msg, src, dest):
		self.stateLock.acquire()
		self.states.append(State(previousState = self.states[-1]))
		self.states[-1].rx(msg, self.idDict[str(src)], self.idDict[str(dest)])
		self.stateLock.release()
	
	def reportTx(self, msg, src, dest):
		self.stateLock.acquire()
		self.states.append(State(previousState = self.states[-1]))
		self.states[-1].tx(msg, self.idDict[str(src)], self.idDict[str(dest)])
		self.stateLock.release()
	
	def reportInactive(self, src):
		self.stateLock.acquire()
		self.states.append(State(previousState = self.states[-1]))
		self.states[-1].inactivated(self.idDict[str(src)])
		self.stateLock.release()	
	
	def reportAckReceived(self, src):
		self.stateLock.acquire()
		self.states.append(State(previousState = self.states[-1]))
		self.states[-1].receivedAck(self.idDict[str(src)])
		self.stateLock.release()
	
	def startAll(self):
		for addr in self.addrs:
			msg = self.msg + str(self.id) + ":" + str(self.msgi)
			self.msgi += 1
			self.reportTx(msg, self.td.addr, addr)
			self.td.tx(addr, msg)
		self.reportInactive(self.td.addr)
		self.td.inactive()
		self.doTester()
	
	def doTester(self):
		while True:
			self.pauseLock.acquire()
			#print "starting"
			while self.paused:
				time.sleep(1)
			self.pauseLock.release()
			msg, addr = self.td.getTestMsg()
			#print "got", msg
			if msg.startswith(self.txStr):
				dest = msg[len(self.txStr):msg.index(self.endAddrStr)]
				self.reportTx(msg[msg.index(self.endAddrStr) + len(self.endAddrStr):], addr, dest)
				self.ack(addr, msg)
			elif msg.startswith(self.rxStr):
				src = msg[len(self.txStr):msg.index(self.endAddrStr)]
				self.reportRx(msg[msg.index(self.endAddrStr) + len(self.endAddrStr):], src, addr)
				self.ack(addr, msg)
			elif msg.startswith(self.td.INACTIVE_STR):
				self.reportInactive(addr)
				self.ack(addr, msg)
				print "acked inactive to", addr
			elif msg.startswith(self.td.ACK_RCV_STR):
				#print "ack received report received."
				self.reportAckReceived(addr)
				self.ack(addr, msg)
			elif msg.startswith(self.td.ACK_TX_STR):
				#print "ack sent report received."
				self.ack(addr, msg)
				#print "sent Ack-ack", msg,"to", addr
			self.td.srcLock.acquire()
			while self.td.uncheckedAcks > 0:
				self.reportAckReceived(self.td.addr)
				print "tester ack received."
				self.td.uncheckedAcks -= 1
			self.td.srcLock.release()
			self.step += 1
			if self.step % 10 == 0:
				self.printState()
			self.pauseLock.acquire()
			print self.step
			if self.td.isTerminated() or self.halted:
				self.pauseLock.release()
				self.printState()
				break
			else:
				self.pauseLock.release()
			time.sleep(0.1)
	
	def pause(self):
		self.pauseLock.acquire()
		self.paused = True
		self.pauseLock.release()
	
	def unpause(self):
		self.pauseLock.acquire()
		self.paused = False
		self.pauseLock.release()
	
	def stop(self):
		self.pauseLock.acquire()
		self.halted = True
		self.pauseLock.release()
		self.msgLock.acquire() #to stop rx
		print "oy"
		for addr in self.addrs:
			self.td.tx(addr, self.stopMsg)
			self.td.tx(addr, self.stopMsg)
		self.td.closeChannel()
		self.msgLock.release()
		

	def printState(self, i = -1):
		self.stateLock.acquire()
		state = self.states[i]
		td.printRed(str(state))
		self.stateLock.release()
	
	def doRx(self):
		while True:
			self.msgLock.acquire()
			if not self.nextMsg:
				self.msgLock.release()
				msg, addr = self.td.rx()
				if not msg:
					break
				self.reportRx(msg, addr, self.td.addr)
				self.msgLock.acquire()
				self.nextMsg = msg
				self.msgLock.release()
			else:
				self.msgLock.release()
			time.sleep(1)

def test():
	addrs = [('Matthews-MacBook-Pro-2.local', 20000), ('Matthews-MacBook-Pro-2.local', 30000), ('Matthews-MacBook-Pro-2.local', 40000)]
	ids = ["source", "messenger1", "messenger2"]
	msg1 = RandomMessager(ids, addrs, 1, isSource = False, testing = True, testAddr = 0)
	msg2 = RandomMessager(ids, addrs, 2, isSource = False, testing = True, testAddr = 0)
	src1 = SourceMessager(ids, addrs, 0)

test()
	