#!/usr/bin/env python

import binascii
import socket
import string
import time
import sys

from datetime import datetime

from reader.uhfreader18 import G2InventoryResponseFrame
from sheets import GoogleSheetAppender

TCP_PORT = 6000
BUFFER_SIZE = 1024
READ_MESSAGE = bytearray([ 0x04, 0x00, 0x01, 0xdb, 0x4b ])

valid_chars = string.digits + string.ascii_letters

def is_marathon_tag(tag_data):
    return len(tag_data) == 4 and all([ chr(tag_byte) in valid_chars for tag_byte in tag_data.lstrip('\0') ])

def read_tags(reader_addr, appender):

    running = True
    while running:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((reader_addr, TCP_PORT))
        except socket.error as err:
            print 'Unable to connect to reader'
            continue
        start = time.time()
        try:
            now = datetime.now().time()
            s.sendall(READ_MESSAGE)
            data = bytearray(s.recv(BUFFER_SIZE))
            resp = G2InventoryResponseFrame(data)
            for tag in resp.get_tag():
                if (is_marathon_tag(tag)):
                    boat_num = str(tag.lstrip('\0'))
                    boat_time = str(now)[:12]
                    print '{0} {1}'.format(boat_num, boat_time)
                    if appender is not None:
                        appender.add_row([ boat_num, boat_time, '', '' ])
                else:
                    print "Non-marathon tag 0x%s" % (binascii.hexlify(tag))
            #print "received %s tags" % (resp.num_tags)
        except KeyboardInterrupt:
            running = False
            print "KeyboardInterrupt"
        except socket.error as err:
            pass
        end = time.time()
        s.close()
        #print "elapsed time %.2f" % (end - start)
        try:
            time.sleep(0.05)
        except KeyboardInterrupt:
            running = False
            print "KeyboardInterrupt"

if __name__ == "__main__":

    if len(sys.argv) >= 2:

        appender_thread = None
        if len(sys.argv) >= 3:
            appender_thread = GoogleSheetAppender(sys.argv[2])
            appender_thread.start()

        read_tags(sys.argv[1], appender_thread)

        if appender_thread is not None:
            appender_thread.running = False
            appender_thread.join()
    else:
        print 'Usage: {0} <reader-ip> [<spreadsheet-id>]'.format(sys.argv[0])
