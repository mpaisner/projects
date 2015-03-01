1) Overview: 

The server.py file implements a FIFO channel. It does so by opening a server which listens for incoming messages and numAddrs - 1 clients which send messages to other addresses.

The td2.py file implements (more or less) a termination detection service. In the original version, it completely implemented this service, but when I wanted to create a higher-level app that reported on the methods that were called, more of the lower-level functions of the td system had to be controlled by the higher level system (e.g., if the td automatically sends an ack when it gets a message, then the ack may reach its destination and be reported before the higher level system can report having done a read). So, it is more accurate to say that the td2.py file implements this service in conjunction with the tester2.py file.

The Tester2.py file defines 3 main classes:
	
	1) RandomMessager - this class reads incoming messages, uses td2.py to appropriately respond with acks/set engager/etc. as defined by the Termination Detecton service, and will randomly send messages and go inactive. It sends messages with a constant probability each second (if active), and goes inactive with a probability that increases with each sent message (again, only if active). The latter condition is intended to cause the system to terminate in a reasonable amount of time. 
	
	RandomMessager will also report each action it takes to the Tester, which sits at the source address.
	
	2) SrcRandomMessager - this class operates the same as above (inherits several methods), but instead of reporting to the Tester across a channel, it does so locally.
	
	3) Tester - this class receives reports from all addresses, and maintains a state (actually, it maintains a list of all states) which encodes the information needed to determine if the program is running according to the service. In conjunction with the RandomMessagers, it implements a version of the service inverse, as it checks the safety conditions against its state each time it receives a report. It also checks each time to make sure that all active addresses are nodes in an out-tree from the source (implemented in the state.isOutTree() method in tester2.py).

2) Running:
	
	-to run on any machine or set of machines, several variables must be set at the bottom of tester2.py (just above the main method)
		-'addrs' must be set to a list of tuples (machineName, port) corresponding to the addresses at which communication will take place
		-ids must be set to a list of names for these addresses; it must be the same length as addrs, and each name must be some string
		-srci defines the index in the addrs list corresponding to the source node for td as well as the location at which reports are sent to the tester.
	
	*important: the tester uses a separate channel with ports 5 higher than the main channel. So, do not use ports on the same machine that are exactly 5 apart or 5 below a reserved port.
	
	*I have tested this on both my local machine and on two machines from my research group's cluster (erewhon and metacog from mcl cluster), but for some reason my grace login doesn't seem to be working so I have not tested it on grace. I don't think there should be any problems, though.

3) Output
	
	-Each time a message is received by the tester, it will print out a description of the message in red. note that these printouts will go back and forth between the literal address (e.g. ('erewhon', 30000)) and the ids defined in tester2.py. This is a bit confusing but not too bad as long as you're aware each address has two names.
	
	-Every ten steps (a step is roughly when the tester gets a message), it will print out the current state information in blue. It will also print out the current state as it terminates.
	
	-when the engager for a node changes, it will locally print that out in blue.
	
	-some other information from the server will print out at the beginning and end as connections are created/terminated. The last relevant message will be the final state information.
	
	-if there is a violation of the service or the active addresses do not form an out-tree at any step, a warning will print in yellow. This should not happen, since the program implements the service.