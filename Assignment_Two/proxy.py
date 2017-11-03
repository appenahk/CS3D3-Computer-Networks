#!/usr/bin/python

import socket
import threading
import signal
import sys
       
class Proxy:
    #initialise server socket
    def __init__(self):  
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        self.serverSocket.bind(('', 1700)) 
        self.serverSocket.listen(1)    
        self.__clients = {}
    
    #proxy thread to handle requests
    def proxy_thread(self, conn, client_addr):

        request = conn.recv(1024)       # get the request from browser
    	line = request.split('\n')[0]                   # parse the first line
        url = line.split(' ')[1] 

    	mName = 'localhost'
    	mPort = 12000
    	proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	proxySocket.connect((mName,mPort))
    	proxySocket.send(url)
        
        #blacklist from proxy side
	
	response = proxySocket.recv(1024)
	if "blacklist" in response:
		conn.send('403: Forbidden')
		conn.close()
		return
	else:	
	    #get the host and port out the url path
	    	self.path = url[7:]
		i = self.path.find('/')
		host = self.path[:i]
	    	i = host.find(':')
		if i!=-1:
		    port = int(host[i+1:]) 
		    host = host[:i]
		else:
		    port = 80

		try:
		    # create a socket to connect to the web server
		    webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		    webSocket.settimeout(5)
		    webSocket.connect((host, port))
		    webSocket.sendall(request)                           # send request to webserver

		    while 1:
		        data = webSocket.recv(1024)          # receive data from web server
		        if (len(data) > 0):
		            conn.send(data)                               # send to browser
		        else:
		            break
		    webSocket.close()
		    conn.close()

		except socket.error as error_msg:
		    if webSocket:
		        webSocket.close()
		    if conn:
		        conn.close() 

    #listen for web client to send request
    def client(self):
        while True:
            (clientSocket, client_address) = self.serverSocket.accept()   # Establish the connection
            p = threading.Thread(name=self._getClientName(client_address), target=self.proxy_thread, args=(clientSocket, client_address))
            p.setDaemon(True)
            p.start()

    def _getClientName(self, cli_addr):
        return "Client"

if __name__ == '__main__':	
	proxy = Proxy()
	proxy.client()
	
