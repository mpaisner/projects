import server, threading, time

class TD:

	TEST_MSG_ID = "test_msg: "
	ACK_RCV_STR = "got ack "
	ACK_TX_STR = "sent ack "
	INACTIVE_STR = "inactivated "
	rxStr = "RX - "
	txStr = "TX - "
	endAddrStr = " | "

	def __init__(self, addrs, i, isSource = False):
		self.id = id
		self.channel = server.FIFOChannel(list(addrs), i)
		self.channel.connect()
		self.addr = self.channel.myAddr
		self.unAcked = 0
		self.isSource = isSource
		self.rxq = []
		self.ackq = []
		self.rxqLock = threading.Lock()
		self.active = isSource
		if isSource:
			self.engager = self.addr
		else:
			self.engager = None
		rxThread = threading.Thread(target = self._doRX)
		rxThread.start()
				
	def _doRX(self):
		while not self.channel.DONE_EVENT.is_set():
			msg = self.channel.getAnyMsg()
			if msg:
				self.rxqLock.acquire()
				msg, addr = msg
				if msg == "ACK":
					self.ackq.append(msg)
				else:
					self.rxq.append((msg, addr))
				self.rxqLock.release()
			time.sleep(0.5)
	
	def rcvAck(self):
		self.rxqLock.acquire()
		try:
			self.ackq.pop(0)
			self.rxqLock.release()
			return True
		except Exception:
			self.rxqLock.release()
			return False	
		
	
	def rcv(self):
		self.rxqLock.acquire()
		try:
			msg = self.rxq.pop(0)
			msg, addr = msg
		except Exception:
			self.rxqLock.release()
			time.sleep(1)
			return self.rcv()
		self.rxqLock.release()
		return (msg, addr)
	
	def tx(self, addr, msg):
		self.rxqLock.acquire()
		self.unAcked += 1
		self.channel.sendMsg(addr, msg)
		self.rxqLock.release()
	
	def sendAck(self, addr):
		self.channel.sendMsg(addr, "ACK")
	
	def inactive(self):
		self.rxqLock.acquire()
		if not self.rxq:
			self.active = False
			if self.unAcked == 0 and not self.isSource:
				self.channel.sendMsg(self.engager, "ACK")
				self.engager = None
		self.rxqLock.release()
	
	def isTerminated(self):
		'''
		rather than waiting, returns false if not at a0.
		'''
		self.rxqLock.acquire()
		#printBlue("unacked =", self.unAcked, "isSource =", self.isSource, "active =", self.active)
		res = self.unAcked == 0 and self.isSource and not self.active
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

def printYellow(*args):
	server.PRINT_LOCK.acquire()
	print '\033[93m',
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
	