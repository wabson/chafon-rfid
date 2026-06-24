#!/usr/bin/env python

# Basic example to write a single tag with an EPC code, which must be a multiple of two bytes

import sys

from math import floor

from chafon_rfid.base import CommandRunner, ReaderCommand, ReaderResponseFrame
from chafon_rfid.command import G2_WRITE_EPC
from chafon_rfid.transport import TcpTransport
from chafon_rfid.transport_serial import SerialTransport

TCP_PORT = 6000


def write_epc_bytes(runner, value):
    password = [0, 0, 0, 0]
    write_data = [floor(len(value) / 2)] + password + value
    write_cmd = ReaderCommand(G2_WRITE_EPC, data=write_data)
    write_resp = ReaderResponseFrame(runner.run(write_cmd))
    return write_resp.result_status


def write_tag_value(runner, tag_value):
    print(tag_value)
    ascii_byes = list(tag_value.encode('ascii'))
    if len(ascii_byes) % 2 > 0:
        ascii_byes.insert(0, 0)
    write_tag_status = write_epc_bytes(runner, ascii_byes)
    if write_tag_status == 0:
        print('Tag written successfully')
        return True
    elif write_tag_status == 0xFA:
        print('Error: Poor communication, try repositioning the tag')
        return False
    elif write_tag_status == 0xFB:
        print('Error: No tags found, is a tag in place?')
        return False
    return None


def write_tag_text_or_range(runner, text_value):
    if ':' in text_value:
        range_parts = text_value.split(':')
        start_number = int(range_parts[0])
        end_number = int(range_parts[1])
        for tag_number in range(start_number, end_number + 1):
            tag_text = str(tag_number)
            print('Write EPC data: {}'.format(tag_text))
            while True:
                input('Press Enter to continue')
                write_result = write_tag_value(runner, tag_text)
                if write_result is True:
                    break
    else:
        write_tag_value(runner, text_value)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print('Usage: {0} <reader-address> <epc-text>'.format(sys.argv[0]))
        sys.exit(1)

    reader_addr = sys.argv[1]
    # transport = TcpTransport(reader_addr=reader_addr, reader_port=TCP_PORT)
    # transport = SerialTransport(device='/dev/ttyS0')
    # transport = SerialTransport(device='/dev/ttyAMA0')
    # transport = SerialTransport(device='/dev/ttyUSB0')
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr)
    else:
        transport = TcpTransport(reader_addr, reader_port=TCP_PORT)

    runner = CommandRunner(transport)

    for tag_value in sys.argv[2:]:
        write_tag_text_or_range(runner, tag_value)

    transport.close()
