#!/usr/bin/python
import struct
import binascii
import random

from socket import *

#computing checkSum
def computeCheckSum(data):
	sum = 0
	for i in range(0, len(data), 2):
		if i+1 < len(data):
			data16 = ord(data[i]) + (ord(data[i+1]) << 8)		
			interSum = sum + data16
			sum = (interSum & 0xffff) + (interSum >> 16)		
	return ~sum & 0xffff	

#gremlin function to corrupt or drop packets
def gremlinFunction(checkSum):
	gremmlife = random.randint(0, 10);
	if gremmlife == 2:
		print("Packet dropped.")
		return (checkSum*4)/5
	elif gremmlife == 8:
		print("Packet corrupted.")
		return (checkSum*4)/5
	else:
		return checkSum

#checkSum comparison
def compareCheckSum(data, checkSum):
	
	sum = 0
	for i in range(0, len(data), 2):
		if i+1 < len(data):
			data16 = ord(data[i]) + (ord(data[i+1]) << 8)		
			interSum = sum + data16
			sum = (interSum & 0xffff) + (interSum >> 16)		
	current= sum & 0xffff 
	result = current & checkSum
	
	if result == 0:
		return True
	else:
		return False

#ACK/NAK configurer
def acknowledgement(seqNum, data, checksum):
	
	global prev
	checksum_rec = computeCheckSum(data)
	checksum_grem = gremlinFunction(checksum_rec)
	if checksum == checksum_grem:
		prev = seqNum + 1
		ack = 1
	else:
		ack = 0
	return ack


def main():
	#structs for packing/unpacking
	frame = struct.Struct('2H 8s H')
	acknowledged= struct.Struct('2I')	
	flag = True
	curr = 1
	prev = 0
	#defining the server socket
	serverPort = 12000
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	serverSocket.bind(('', serverPort))
	serverSocket.listen(1)
	
	print 'The server is ready to receive'
	connectionSocket, addr = serverSocket.accept()
	#open file to write received data
	filename = open("output.txt","a") 
	while flag:
		if prev == curr:
			curr += 1
		#frame from client socket
		frameReceived= connectionSocket.recv(1024)
		sequenceNum,  length, data, checksum = frame.unpack(frameReceived)

		unpacked_data = data.decode('UTF-8')
		print('From Transmitter:', sequenceNum, unpacked_data)
		verification = compareCheckSum(unpacked_data, checksum)
		ACKNAK = acknowledgement(sequenceNum, unpacked_data, checksum)
		if verification == True and ACKNAK == 1: #check to see frames are correct
			if unpacked_data != b'\00\00\00\00\00\00\00\00':
				filename.write(unpacked_data)	
				curr += 1
			if unpacked_data == b'\00\00\00\00\00\00\00\00':
				flag = False
		
		frameSent = acknowledged.pack(curr, ACKNAK)#sending acknowledgement to proceed
		connectionSocket.send(frameSent)

	filename.close()
	connectionSocket.close()

if __name__ == '__main__':	
	main()
