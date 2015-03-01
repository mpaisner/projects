import server, threading, time

class TD:

	TEST_MSG_ID = "test_msg: "
	ACK_RCV_STR = "got ack "
	ACK_TX_STR = "sent ack "
	INACTIVE_STR = "inactivated "
	rxStr = "RX - "
	txStr = "TX - "
	endAddrStr = " | "

	def __init__(self, addrs, i, isSource = False, testing = False, srcAddr = 0, id = "no id"):
		self.id = id
		self.testing = testing
		self.channel = server.FIFOChannel(list(addrs), i)
		self.addr = self.channel.myAddr
		self.channel.connect()
		self.unAcked = 0
		self.isSource = isSource
		self.source = addrs[srcAddr]
		if isSource:
			self.engager = self.addr
			self.active = True
			self.srcLock = threading.Lock()
			self.uncheckedAcks = 0
		else:
			self.engager = None
			self.active = False
		self.rxq = []
		self.rxqLock = threading.Lock()
		self.awaitLock = threading.Lock()
		self.testQueue = []
		self.ackQueue = []
		self.txQueue = []
		self.ackThread = threading.Thread(target = self.sendTestMessages)
		self.ackThread.start()
		if testing:
			self.testq = []
			self.testqLock = threading.Lock()
		rxThread = threading.Thread(target = self._doRX)
		rxThread.start()
	
	def awaitAck(self):
		'''
		assumed only one thread is in this method at once. Also, since only
		Ack messages will come to non-test servers, and since the test
		server will never await an ack, this method assumes all incoming
		test message are acks.
		'''
		msg, addr = self.getTestMsg()
		#if not msg.startswith(self.ackStr):
			#raise Exception("expected ACK, got " + str(msg))
				
	def sendTestMessages(self):
		while True:
			self.awaitLock.acquire()
			if not self.testQueue:
				self.awaitLock.release()
				time.sleep(0.5)
			else:
				addr, msg, awaitAck = self.testQueue.pop(0)
				print "sending"
				self._sentTestMsg(addr, msg, awaitAck)
				self.awaitLock.release()
			
	
	def reportAckReceived(self):
		if self.isSource:
			self.srcLock.acquire()
			print "ack incr"
			self.uncheckedAcks += 1
			self.srcLock.release()
		else:
			self.sendTestMsg(self.source, self.ACK_RCV_STR)
	
	def reportAckSent(self, dest):
		if not self.isSource:
			self.awaitLock.acquire()
			self.ackQueue.append(dest)
			self.awaitLock.release()
			self.sendTestMsg(self.source, self.ACK_TX_STR)
	
	def reportInactive(self):
		if not self.isSource:
			self.sendTestMsg(self.source, self.INACTIVE_STR)
	
	def reportRx(self, src, msg):
		if not self.isSource:
			self.sendTestMsg(self.source, self.rxStr + str(src) + self.endAddrStr + msg)
	
	def reportTx(self, src, msg):
		if not self.isSource:
			self.awaitLock.acquire()
			self.txQueue.append((src, msg))
			self.awaitLock.release()
			self.sendTestMsg(self.source, self.txStr + str(src) + self.endAddrStr + msg)
			
	
	def _doRX(self):
		while not self.channel.DONE_EVENT.is_set():
			msg = self.channel.getAnyMsg()
			if msg:
				#server.PRINT_LOCK.acquire()
				#print "incoming at", self.id, ":", msg
				#print "Waiting for lock to store", msg
				#server.PRINT_LOCK.release()
				self.rxqLock.acquire()
				#server.PRINT_LOCK.acquire()
				#print "Lock acquired to store", msg
				#server.PRINT_LOCK.release()
				msg, addr = msg
				#printBlue("Got", msg, "from", addr, "at", self.id)
				if msg == "ACK":
					#printRed("Ack received at", self.id)
					self.reportAckReceived()
					self.unAcked -= 1
					print "acks:", self.unAcked
					if not self.active and self.unAcked == 0 and not self.isSource:
						self.reportAckSent(self.engager)
						self.engager = None
				elif self.testing and msg.startswith(self.TEST_MSG_ID):
					#print "got", msg, "at", self.id
					self.testqLock.acquire()
					self.testq.append((msg[len(self.TEST_MSG_ID):], addr))
					self.testqLock.release()
				else:
					#self.rxq.append(msg)
					self.reportRx(addr, msg)
					self.rxq.append((msg, addr))
					self.active = True
					print "active at", self.id
					if self.engager:
						self.reportAckSent(addr)
						#printRed("sending Ack from", self.id)
					else:
						self.engager = addr
				self.rxqLock.release()
				#server.PRINT_LOCK.acquire()
				#print "Lock released after storing", msg
				#server.PRINT_LOCK.release()
			time.sleep(1)
		print "DONE at", self.id
	
	def _sentTestMsg(self, addr, msg, awaitAck):
		tmsg = self.TEST_MSG_ID + msg
		self.channel.sendMsg(addr, msg)
		if awaitAck:
			self.awaitAck()
		if msg.startswith(self.ACK_TX_STR):
			dest = self.ackQueue.pop(0)
			self.channel.sendMsg(dest, "ACK")
		elif msg.startswith(self.txStr):
			dest, msg = self.txQueue.pop(0)
			self.channel.sendMsg(dest, msg)
	
	def sendTestMsg(self, addr, msg, awaitAck = True):
		self.awaitLock.acquire()
		self.testQueue.append((addr, msg, awaitAck))
		self.awaitLock.release()
	
	def getTestMsg(self):
		'''
		returns msg, addr
		'''
		self.testqLock.acquire()
		try:
			msg = self.testq.pop(0)
		except Exception:
			self.testqLock.release()
			time.sleep(1)
			return self.getTestMsg()
		self.testqLock.release()
		printRed(self.id, "got", msg)
		return msg
	
	def tx(self, addr, msg):
		self.rxqLock.acquire()
		self.unAcked += 1
		print "acks:", self.unAcked
		self.rxqLock.release()
		#print "sending message", addr, msg
		self.reportTx(addr, msg)
	
	def rx(self):
		#server.PRINT_LOCK.acquire()
		#print "waiting for lock", self.addr
		#server.PRINT_LOCK.release()
		self.rxqLock.acquire()
		#server.PRINT_LOCK.acquire()
		#print "lock taken", self.addr
		#server.PRINT_LOCK.release()
		try:
			msg = self.rxq.pop(0)
		except Exception:
			self.rxqLock.release()
			#server.PRINT_LOCK.acquire()
			#print "lock released.", self.addr
			#server.PRINT_LOCK.release()
			time.sleep(1)
			return self.rx()
		self.rxqLock.release()
		#server.PRINT_LOCK.acquire()
		#print "lock released.", self.addr
		#server.PRINT_LOCK.release()
		#print "received msg", msg
		return msg
	
	def inactive(self):
		self.rxqLock.acquire()
		if not self.rxq:
			self.active = False
			print "trying to inactivate. acks:", self.unAcked
			if self.unAcked == 0 and not self.isSource:
				print "reporting"
				self.reportInactive()
				print self.engager
				self.channel.sendMsg(self.engager, "ACK")
				self.engager = None
		self.rxqLock.release()
	
	def isTerminated(self):
		'''
		rather than waiting, returns false if not at a0.
		'''
		self.rxqLock.acquire()
		res = self.unAcked == 0 and self.isSource and not self.active
		print "terminate?", self.unAcked, self.isSource, self.active
		self.rxqLock.release()
		return res
	
	def rxAndPrint(self):
		msg = self.rx()
		server.PRINT_LOCK.acquire()
		print '\033[94m', msg, '\033[0m'
		server.PRINT_LOCK.release()
		return msg
	
	def closeChannel(self):
		self.channel.stop()

def printRed(*args):
	server.PRINT_LOCK.acquire()
	print '\033[91m',
	for arg in args:
		print arg,
	print '\033[0m'
	server.PRINT_LOCK.release()

def printBlue(*args):
	server.PRINT_LOCK.acquire()
	print '\033[94m',
	for arg in args:
		print arg,
	print '\033[0m'
	server.PRINT_LOCK.release()

def test():
	addrs = [('Matthews-MacBook-Pro-2.local', 20003), ('Matthews-MacBook-Pro-2.local', 30003), ('Matthews-MacBook-Pro-2.local', 40003)]
	td1 = TD(addrs, 0, True)
	td2 = TD(addrs, 1)
	td3 = TD(addrs, 2)
	printRed("dead:", td1.isTerminated())
	td1.tx(td2.addr, "start2")
	td2.rxAndPrint()
	print "start send"
	td2.tx(td1.addr, "random 2->1")
	print "end send"
	#td2.rxAndPrint()
	td1.rxAndPrint()
	printRed("dead:", td1.isTerminated())
	td2.inactive()
	#td1.rxAndPrint()
	td1.inactive()
	while True:
		res = td1.isTerminated()
		printRed("dead:", res)
		if res:
			break
		time.sleep(1)
	td1.closeChannel()
	td2.closeChannel()
	td3.closeChannel()

#test()
	