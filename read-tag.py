#!/usr/bin/env python

import binascii
import socket
import string
import time

TCP_IP = '192.168.1.190'
TCP_PORT = 6000
BUFFER_SIZE = 1024
CONNECT_MESSAGE_1 = bytearray([ 0x04, 0xff, 0x21, 0x19, 0x95 ])
CONNECT_MESSAGE_2 = bytearray([ 0x04, 0x00, 0x21, 0xd9, 0xba ])
READ_MESSAGE = bytearray([ 0x04, 0x00, 0x01, 0xdb, 0x4b ])

valid_chars = string.digits + string.ascii_letters

class ReaderResponse(object):

    def __init__(self, resp_bytes):
        if len(resp_bytes) < 5:
            raise ValueError('Response must be at least 5 bytes');
        self.len = resp_bytes[0]
        if self.len != len(resp_bytes) - 1:
            raise ValueError('Response is longer than stated length (expected %d, got %d)' % (self.len, len(resp_bytes)));
        self.reader_addr = resp_bytes[1]
        self.resp_cmd = resp_bytes[2]
        self.result_status = resp_bytes[3]
        self.data = resp_bytes[4:self.len-1]

class G2InventoryResponse(ReaderResponse):

    def __init__(self, resp_bytes):
        super(G2InventoryResponse, self).__init__(resp_bytes)
        if len(self.data) > 0:
            self.num_tags = self.data[0]

    def get_tag(self):
        n = 0
        pointer = 1
        while n < self.num_tags:
            tag_len = int(self.data[pointer])
            tag_start = pointer + 1
            next_tag_start = tag_start + tag_len
            yield self.data[tag_start:next_tag_start]
            pointer = next_tag_start
            n += 1

def is_marathon_tag(tag_data):
    return len(tag_data) == 4 and all([ chr(tag_byte) in valid_chars for tag_byte in tag_data.lstrip('\0') ])


# s.sendall(CONNECT_MESSAGE_1)
# data = s.recv(BUFFER_SIZE)
# print "received data:", len(data)

# s.sendall(CONNECT_MESSAGE_2)
# data = s.recv(BUFFER_SIZE)
# print "received data:", len(data)

running = True
while running:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    start = time.time()
    try:
        s.sendall(READ_MESSAGE)
        data = s.recv(BUFFER_SIZE)
        #print "received data:", len(data), binascii.hexlify(bytearray(data))
        resp = G2InventoryResponse(bytearray(data))
        for tag in resp.get_tag():
            if (is_marathon_tag(tag)):
                print str(tag.lstrip('\0'))
            else:
                print "Non-marathon tag 0x%s" % (binascii.hexlify(tag))
        print "received %s tags" % (ord(data[4]))
    except KeyboardInterrupt:
        running = False
        print "KeyboardInterrupt"
    end = time.time()
    s.close()
    print "elapsed time %.2f" % (end - start)
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        running = False
        print "KeyboardInterrupt"
