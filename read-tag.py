#!/usr/bin/env python

import binascii
import socket
import time

TCP_IP = '192.168.1.190'
TCP_PORT = 6000
BUFFER_SIZE = 1024
CONNECT_MESSAGE_1 = bytearray([ 0x04, 0xff, 0x21, 0x19, 0x95 ])
CONNECT_MESSAGE_2 = bytearray([ 0x04, 0x00, 0x21, 0xd9, 0xba ])
READ_MESSAGE = bytearray([ 0x04, 0x00, 0x01, 0xdb, 0x4b ])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((TCP_IP, TCP_PORT))

start = time.time()

# s.sendall(CONNECT_MESSAGE_1)
# data = s.recv(BUFFER_SIZE)
# print "received data:", len(data)

# s.sendall(CONNECT_MESSAGE_2)
# data = s.recv(BUFFER_SIZE)
# print "received data:", len(data)

s.sendall(READ_MESSAGE)
data = s.recv(BUFFER_SIZE)
print "received data:", len(data), binascii.hexlify(bytearray(data))
print "received %s tags" % (ord(data[4]))

end = time.time()

s.close()

print "elapsed time %.2f" % (end - start)