#!/usr/bin/env python

import socket
import string
import time
import sys

from datetime import datetime

from chafon_rfid.base import CommandRunner, ReaderCommand, ReaderInfoFrame, ReaderResponseFrame, ReaderType
from chafon_rfid.command import G2_TAG_INVENTORY, CF_GET_READER_INFO, CF_SET_RF_POWER, CF_SET_WORK_MODE_18, CF_SET_WORK_MODE_288M
from chafon_rfid.response import G2_TAG_INVENTORY_STATUS_MORE_FRAMES
from chafon_rfid.transport import TcpTransport
from chafon_rfid.transport_serial import SerialTransport
from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as G2InventoryResponseFrame18
from chafon_rfid.uhfreader288m import G2InventoryCommand, G2InventoryResponseFrame

TCP_PORT = 6000
DELAY = 0.00

valid_chars = string.digits + string.ascii_letters


def is_marathon_tag(tag):
    tag_data = tag.epc
    return len(tag_data) == 4 and all([chr(tag_byte) in valid_chars for tag_byte in tag_data.lstrip(bytearray([0]))])


def set_power(transport, power_db):
    set_power = ReaderCommand(CF_SET_RF_POWER, data=[power_db])
    transport.write(set_power.serialize())
    status = ReaderResponseFrame(transport.read_frame()).result_status
    return status


def get_reader_type(runner):
    get_reader_info = ReaderCommand(CF_GET_READER_INFO)
    reader_info = ReaderInfoFrame(runner.run(get_reader_info))
    return reader_info.type


def read_tags(reader_addr, appender):

    # transport = TcpTransport(reader_addr=reader_addr, reader_port=TCP_PORT)
    # transport = SerialTransport(device='/dev/ttyS0')
    # transport = SerialTransport(device='/dev/ttyAMA0')
    # transport = SerialTransport(device='/dev/ttyUSB0')
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr)
    else:
        transport = TcpTransport(reader_addr)
    set_power(transport, 27)

    runner = CommandRunner(transport)
    reader_type = get_reader_type(runner)
    if reader_type == ReaderType.UHFReader18:
        get_inventory_cmd = ReaderCommand(G2_TAG_INVENTORY)
        frame_type = G2InventoryResponseFrame18
    elif reader_type == ReaderType.UHFReader288M:
        get_inventory_cmd = G2InventoryCommand(q_value=4, antenna=0x80)
        frame_type = G2InventoryResponseFrame
    else:
        print('Unknown reader type {}'.format(reader_type))
        sys.exit(1)

    running = True
    while running:
        start = time.time()
        try:
            now = datetime.now().time()
            transport.write(get_inventory_cmd.serialize())
            inventory_status = None
            while inventory_status is None or inventory_status == G2_TAG_INVENTORY_STATUS_MORE_FRAMES:
                resp = frame_type(transport.read_frame())
                inventory_status = resp.result_status
                for tag in resp.get_tag():
                    if is_marathon_tag(tag):
                        boat_num = (tag.epc.lstrip(bytearray([0]))).decode('ascii')
                        boat_time = str(now)[:12]
                        print('{0} {1}'.format(boat_num, boat_time))
                        if appender is not None:
                            appender.add_row([boat_num, boat_time, '', ''])
                    else:
                        print("Non-marathon tag 0x%s" % (tag.epc.hex()))
                #print "received %s tags" % (resp.num_tags)
        except KeyboardInterrupt:
            running = False
            print("KeyboardInterrupt")
        except socket.error:
            print('Unable to connect to reader')
            continue
        end = time.time()
        #print("elapsed time %.2f" % (end - start))
        try:
            time.sleep(DELAY)
        except KeyboardInterrupt:
            running = False
            print("KeyboardInterrupt")
    transport.close()


if __name__ == "__main__":

    if len(sys.argv) >= 2:

        appender_thread = None
        if len(sys.argv) >= 3:
            from sheets import GoogleSheetAppender
            appender_thread = GoogleSheetAppender(sys.argv[2])
            appender_thread.start()

        read_tags(sys.argv[1], appender_thread)

        if appender_thread is not None:
            appender_thread.running = False
            appender_thread.join()
    else:
        print('Usage: {0} <reader-ip> [<spreadsheet-id>]'.format(sys.argv[0]))
