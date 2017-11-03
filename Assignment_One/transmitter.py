#!/usr/bin/python
import random
import string
import struct
import binascii
import time
# TCP Client

from socket import *

#calculate checkSum
def computeCheckSum(data):
	sum = 0
	for i in range(0, len(data), 2):
		if i+1 < len(data):
			data16 = ord(data[i]) + (ord(data[i+1]) << 8)		
			interSum = sum + data16
			sum = (interSum & 0xffff) + (interSum >> 16)		
	return ~sum & 0xffff	

#gremlin
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



def main():

	#define and connect sockets
	serverName = 'localhost'
	serverPort = 12000
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((serverName,serverPort))
	#generate random file
	filename = open("input.txt", "w");
	filename.write(''.join(random.choice(string.ascii_letters) for _ in range(1024)))
	filename.close()

	filename = open("input.txt",'r')
	frame = struct.Struct('2H 8s H')
	ACKNAK = struct.Struct('2I')
	currSeq = 1
	end = 0
	
	while end == 0:
			
		time.sleep(0.005)
		data_sending = filename.read(8)

		if data_sending == "":
			end = 1
		#calculate checksum, gremlin and build frame
		checksum = computeCheckSum(data_sending)
		gremSum = gremlinFunction(checksum)
		values = (currSeq, 8, data_sending.encode('utf-8'), gremSum)
		frame_out = frame.pack(*values)

		#send frames
		clientSocket.send(frame_out)
		print('To Receiver:', currSeq)
		ack_received = clientSocket.recv(1024) #receive acknowledgement
		sequenceNum , ack = ACKNAK.unpack(ack_received)
		print('From Receiver:', sequenceNum, 'Acknowledgement =', ack)
		#if ack is NAK resend the frame
		while ack == 0:
			checksum = computeCheckSum(data_sending)
			gremSum = gremlinFunction(checksum)
			values = (currSeq, 8, data_sending.encode('utf-8'), gremSum)
			frame_out = frame.pack(*values)

			clientSocket.send(frame_out)
			print('To Receiver:', currSeq)
			ack_received = clientSocket.recv(1024)
			sequenceNum, ack = ACKNAK.unpack(ack_received)
			print('From Receiver:', sequenceNum, 'Acknowledgement =', ack)


		if ack == 1:
			currSeq += 1
		
	#send NULL to terminate file
	data_sent = b'\00\00\00\00\00\00\00\00'
	final_values = (currSeq, 4, data_sent.encode('utf-8'), checksum)
	frame_out = frame.pack(*final_values)
	clientSocket.send(frame_out)
	maxSeqNum = currSeq
	filename.close()
	clientSocket.close()

if __name__ == '__main__':	
	main()

