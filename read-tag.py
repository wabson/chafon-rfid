#!/usr/bin/env python

import binascii
import socket
import string
import threading
import time
import sys

TCP_PORT = 6000
BUFFER_SIZE = 1024
CONNECT_MESSAGE_1 = bytearray([ 0x04, 0xff, 0x21, 0x19, 0x95 ])
CONNECT_MESSAGE_2 = bytearray([ 0x04, 0x00, 0x21, 0xd9, 0x6a ])
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

from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib import HTTPException
from httplib2 import Http, ServerNotFoundError
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
TIMES_RANGE_NAME = 'Chip Finishes!A1:D1'

class GoogleSheetAppender(threading.Thread):

    def __init__(self, spreadsheet_id):
        threading.Thread.__init__(self)
        self.__row_data = []
        self.__spreadsheet_id = spreadsheet_id
        self.__commit_count = 0
        self.running = True

    def run(self):
        while(self.running):
            self.__append_spreadsheet_values()
            time.sleep(5)

    def add_row(self, row_values):
        self.__row_data.append(row_values)

    def __append_spreadsheet_values(self):

        spreadsheet_values = self.__row_data[self.__commit_count:]
        if len(spreadsheet_values) == 0:
            return

        store = file.Storage('google-token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('google-credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        try:
            service = build('sheets', 'v4', http=creds.authorize(Http()))
            sheet = service.spreadsheets()
            value_input_option = 'USER_ENTERED'
            insert_data_option = 'INSERT_ROWS'
            value_range_body = {
                    'range': TIMES_RANGE_NAME,
                    'majorDimension': 'ROWS',
                    'values': spreadsheet_values
                    }
            request = service.spreadsheets().values().append(spreadsheetId=self.__spreadsheet_id, range=TIMES_RANGE_NAME, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
            response = request.execute()
            rows_added = response.get('updates').get('updatedRows')
            self.__commit_count += rows_added
            print('{0} rows updated'.format(rows_added))
        except HttpError as err:
            if err.resp.status in [403, 404, 500, 503]:
                print 'Error appending spreadsheet values: %s' % (err.resp.status,)
            else:
                raise
        except (HTTPException, ServerNotFoundError, socket.error) as err:
            print 'Could not append spreadsheet values'

def read_tags(reader_addr, appender):

    # s.sendall(CONNECT_MESSAGE_1)
    # data = s.recv(BUFFER_SIZE)
    # print "received data:", len(data)

    # s.sendall(CONNECT_MESSAGE_2)
    # data = s.recv(BUFFER_SIZE)
    # print "received data:", len(data)

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
            #data = bytearray.fromhex("10 00 01 01 02 04 00 35 31 37 04 00 32 30 38 c8 07")
            #print "received data:", len(data), binascii.hexlify(bytearray(data))
            resp = G2InventoryResponse(data)
            for tag in resp.get_tag():
                if (is_marathon_tag(tag)):
                    boat_num = str(tag.lstrip('\0'))
                    boat_time = str(now)[:12]
                    print '{0} {1}'.format(boat_num, boat_time)
                    if appender is not None:
                        appender.add_row([ boat_num, boat_time, '', '' ])
                else:
                    print "Non-marathon tag 0x%s" % (binascii.hexlify(tag))
            print "received %s tags" % (resp.num_tags)
        except KeyboardInterrupt:
            running = False
            print "KeyboardInterrupt"
        end = time.time()
        s.close()
        print "elapsed time %.2f" % (end - start)
        try:
            time.sleep(1)
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
