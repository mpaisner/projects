import socket, threading, time


PRINT_LOCK = threading.Lock()
MSG_SIZE = 2048
MSG_END = "MSG_ENDING" 
#note that if someone sends this exact string as part of a message, this whole thing will break.

def send(socket, msg, addr):
	totalsent = 0
	msg = str(addr) + msg + MSG_END
	while totalsent < len(msg):
		sent = socket.send(msg)
		totalsent += sent

#returns (completeMsg [if any], leftover chars)
#will only return one msg at a time. User must store leftover chars and send as input next call.
def receive(previous, msg):
	all = previous + msg
	if MSG_END in all:
		firstQuote = all.index("'")
		secondQuote = all.index("'", firstQuote + 1)
		portStart = all.index(",", secondQuote) + 1
		portEnd = all.index(")", portStart)
		addr = (all[firstQuote + 1:secondQuote], int(all[portStart:portEnd]))
		return (addr, all[portEnd + 1:all.index(MSG_END)], all[all.index(MSG_END) + len(MSG_END):])
	else:
		return (None, None, all)

def serverAction(myAddress, connection, address):
	PRINT_LOCK.acquire()
	print "server at", myAddress, "Connected to:", address
	PRINT_LOCK.release()
	previous = ""
	val = ""
	while True:
		addr, msg, previous = receive(previous, val)
		if msg:
			PRINT_LOCK.acquire()
			print "got:", msg, "from", addr
			PRINT_LOCK.release()
		val = connection.recv(MSG_SIZE)
		if val == "":
			PRINT_LOCK.acquire()
			print "Connection to", address, "broken."
			PRINT_LOCK.release()
			break


class Server:
	
	portMin = 20000
	portMax = 20000
	
	def __init__(self, port, maxConnections):
		self.addr = socket.gethostname()
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#port = self.portMin
		#self.bind(self.s, port)
		self.s.bind((self.addr, port))
		PRINT_LOCK.acquire()
		print "Server at", self.addr, "bound to port", port, "."
		PRINT_LOCK.release()
		self.s.listen(maxConnections)
		self.maxConnections = maxConnections
		self.threads = []
	
	def bind(self, s, port):
		try:
			s.bind((self.addr, port))
			PRINT_LOCK.acquire()
			print "Server at", self.addr, "bound to port", port, "."
			PRINT_LOCK.release()
		except Exception, e:
			PRINT_LOCK.acquire()
			print "Bind failed at", self.addr, "port", port, "error code:", e, ". Trying next port."
			PRINT_LOCK.release()
			if port == self.portMax:
				PRINT_LOCK.acquire()
				print "All ports failed. Something is clearly wrong."
				PRINT_LOCK.release()
			else:
				self.bind(s, port + 1)
	
	#connects to maxConnections incoming sockets, then terminates. If fewer than maxConnections occur, will run forever.
	def go(self, myAddress, action):
		while not self.finished():
			connection, address = self.s.accept()
			thread = threading.Thread(target = action, args = (myAddress, connection, address))
			self.threads.append(thread)
			thread.start()
		PRINT_LOCK.acquire()
		print "server done."
		PRINT_LOCK.release()
	
	def finished(self):
		return len(self.threads) == self.maxConnections
	
	def setFinished(self, val):
		self.lock.acquire()
		self.done = val
		self.lock.release()

		

class Client:
	
	def __init__(self, host, port):
		self.addr = (host, port)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect(self.addr)
			
	def go(self):
		send(self.s, "Hello!", self.addr)
		time.sleep(1)
		send(self.s, "I am awake or something!", self.addr)
		self.s.close()


'''
serve = Server(20000, 2)
serveThread = threading.Thread(target = serve.go, args = (('Matthews-MacBook-Pro-2.local', 20000), serverAction))
serveThread.start()
client = Client('Matthews-MacBook-Pro-2.local', 20000)
thread1 = threading.Thread(target = client.go)
thread1.start()
#time.sleep(1)
client2 = Client('Matthews-MacBook-Pro-2.local', 20000)
thread2 = threading.Thread(target = client2.go)
thread2.start()
'''
import traceback

def tryConnect(s, addr, myAddr):
	try:
		s.connect(addr)
		return s
	except Exception as e:
		PRINT_LOCK.acquire()
		#print "client at", myAddr, "failed to connect to", addr, "with exception", traceback.format_exc(), ". Trying again in 3 seconds."
		PRINT_LOCK.release()
		time.sleep(3)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		return tryConnect(s, addr, myAddr)

class FIFOChannel:
	
	msgCheckInterval = 1 #check every n seconds for new messages in queue
	
	def __init__(self, addrs, i):
		self.myAddr = addrs[i]
		del addrs[i] #remove own address once port is read.
		self.addrs = addrs
		self.DONE_EVENT = threading.Event()
	
	def connect(self):
	
		self.txs = {addr: [] for addr in self.addrs}
		self.rcvx = {addr: [] for addr in self.addrs}
		self.rcvi = {addr: 0 for addr in self.addrs} #which message should be retrieved next?
		self.rcvLock = threading.Lock()
		self.txLock = threading.Lock()
			
		#start server to receive msgs
		serve = Server(self.myAddr[1], len(self.addrs))
		self.serveThread = threading.Thread(target = serve.go, args = (self.myAddr, self.serverRead))
		self.serveThread.start()
		self.alive = True
		
		#start clients to send msgs to other addresses
		self.clientThreads = set()
		for addr in self.addrs:
			clientThread = threading.Thread(target = self.clientWrite, args = (self.myAddr, addr))
			self.clientThreads.add(clientThread)
			clientThread.start()
			
	
	def incomingConnected(self):
		return not self.serveThread.isAlive()
	
	def serverRead(self, myAddress, connection, address):
		PRINT_LOCK.acquire()
		#print "server at", myAddress, "received connection from", address
		PRINT_LOCK.release()
		previous = ""
		while not self.DONE_EVENT.is_set():
			val = connection.recv(MSG_SIZE)
			addr, msg, previous = receive(previous, val)
			if msg:
				self.rcvLock.acquire()
				self.rcvx[addr].append(msg)
				#print msg
				self.rcvLock.release()
			if val == "":
				PRINT_LOCK.acquire()
				#print "server at", myAddress, "incoming stream from", address, "broken."
				PRINT_LOCK.release()
				break
		PRINT_LOCK.acquire()
		#print "connection at", myAddress, "to", address, "is closing."
		PRINT_LOCK.release()
		connection.close()
		
	def clientWrite(self, myAddress, address):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s = tryConnect(s, address, myAddress) 
		#will try to connect at intervals until successful.
		msgI = 0
		while not self.DONE_EVENT.is_set():
			msg = None
			self.txLock.acquire()
			if len(self.txs[address]) > msgI:
				msg = self.txs[address][msgI]
				msgI += 1
			self.txLock.release()
			if msg:
				send(s, msg, myAddress)
			else:
				time.sleep(self.msgCheckInterval)
		PRINT_LOCK.acquire()
		print "connection at", myAddress, "to", address, "is closing."
		PRINT_LOCK.release()
		s.close()
	
	def sendMsg(self, address, msg):
		self.txLock.acquire()
		self.txs[address].append(msg)
		self.txLock.release()
	
	def sendAll(self, msg):
		for addr in self.addrs:
			self.sendMsg(addr, msg)
	
	def getMsg(self, address):
		'''
		returns next message (if any) from given address.
		'''
		msg = None
		self.rcvLock.acquire()
		if len(self.rcvx[address]) > self.rcvi[address]:
			msg = self.rcvx[address][self.rcvi[address]]
			self.rcvi[address] += 1
		self.rcvLock.release()
		return msg
	
	def getAnyMsg(self):
		'''
		Returns some message and its sender, if there is one from any address. This method will favor messages that come from addresses python arbitrarily puts first in the map iterator. However, who cares?
		'''
		for addr in self.addrs:
			msg = self.getMsg(addr)
			if msg:
				return (msg, addr)
		return None
	
	def stop(self):
		self.DONE_EVENT.set()
	
def test():
	addrs = [('Matthews-MacBook-Pro-2.local', 20003), ('Matthews-MacBook-Pro-2.local', 30003), ('Matthews-MacBook-Pro-2.local', 40003)]
	channel1 = FIFOChannel(list(addrs), 0)
	channel2 = FIFOChannel(list(addrs), 1)
	channel3 = FIFOChannel(list(addrs), 2)
	channel1.connect()
	channel2.connect()
	channel3.connect()
	time.sleep(1)
	channel1.sendAll("hello")
	channel2.sendAll("goodbye")
	acked1 = False
	acked2 = False
	while not (acked1 and acked2): 
		msg1 = channel1.getAnyMsg()
		if msg1:
			msg, addr = msg1
			if msg == "ackhello":
				PRINT_LOCK.acquire()
				#print "received ack at addr 1 from", addr
				PRINT_LOCK.release()
				acked1 = True
		msg2 = channel2.getAnyMsg()
		if msg2:
			msg, addr = msg2
			if msg == "ackgoodbye":
				PRINT_LOCK.acquire()
				#print "received ack at addr 2 from", addr
				PRINT_LOCK.release()
				acked2 = True
		msg3 = channel3.getAnyMsg()
		if msg3:
			msg, addr = msg3
			PRINT_LOCK.acquire()
			#print "received", msg, "at address 3 from", addr, "Sending ack."
			PRINT_LOCK.release()
			channel3.sendAll("ack" + msg)
		time.sleep(2)
	channel1.stop()
	channel2.stop()
	channel3.stop()

#test()