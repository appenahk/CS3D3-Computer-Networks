#!/usr/bin/python
import socket
import threading
import signal
import sys
import Queue

blacklist =[]
myqueue = Queue.Queue(maxsize=0)

class Management:

	def __init__(self):
		signal.signal(signal.SIGINT, self.signal_handler)
		self.managementSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.managementSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.managementSocket.bind(('', 12000))
		self.managementSocket.listen(1)
		self.__clients = {}
		print 'The management console is ready to receive'
	
	def listener(self):
		while True:
			connectionSocket, addr = self.managementSocket.accept()
			m = threading.Thread(target=self.management_thread, args=(connectionSocket, addr))
 			m.setDaemon(True)
            		m.start()			
		self.signal_handler(0,0)
	
	def management_thread(self, conn, _addr):		
		requests = conn.recv(1024)         
		print ('From Proxy:', requests[0:20])
			
		if not myqueue.empty():
			blacklist.append(myqueue.get())

		check = requests.decode()
		if any (substring in check for substring in blacklist):
        		conn.send('blacklist')

	def signal_handler(self, signum, frame):
		self.managementSocket.close()
		sys.exit(0)

if __name__ == '__main__':
		
	while 1:
		inp = raw_input('Blacklist: yes/no')
		if (inp == 'yes'):
			myqueue.put(raw_input('Blacklist site: '))
		else :
			break
	console = Management()
	console.listener()
