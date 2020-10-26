#!/usr/bin/env python

import sys

from math import floor

from chafon_rfid.base import CommandRunner, ReaderCommand, ReaderResponseFrame
from chafon_rfid.command import G2_WRITE_EPC
from chafon_rfid.transport import TcpTransport
from chafon_rfid.transport_serial import SerialTransport

TCP_PORT = 6000


def write_epc(runner, value):
    if len(value) % 2 > 0:
        raise ValueError('Value must be a whole number of words, i.e. multiple of two bytes')
    password = [0, 0, 0, 0]
    write_data = [floor(len(value) / 2)] + password + value
    write_cmd = ReaderCommand(G2_WRITE_EPC, data=write_data)
    write_resp = ReaderResponseFrame(runner.run(write_cmd))
    return write_resp.result_status


def write_tag_value(reader_addr, tag_value):

    # transport = TcpTransport(reader_addr=reader_addr, reader_port=TCP_PORT)
    # transport = SerialTransport(device='/dev/ttyS0')
    # transport = SerialTransport(device='/dev/ttyAMA0')
    # transport = SerialTransport(device='/dev/ttyUSB0')
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr)
    else:
        transport = TcpTransport(reader_addr, reader_port=TCP_PORT)

    runner = CommandRunner(transport)
    try:
        write_tag_status = write_epc(runner, tag_value)
        if write_tag_status == 0:
            print('Tag written successfully')
        elif write_tag_status == 0xFA:
            print('Error: Poor communication, try repositioning the tag')
        elif write_tag_status == 0xFB:
            print('Error: No tags found, is a tag in place?')
    except ValueError as e:
        print('Could not write value: {}'.format(e))
        sys.exit(1)

    transport.close()


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        write_tag_value(sys.argv[1], list('1234'.encode('ascii')))
    else:
        print('Usage: {0} <reader-address>'.format(sys.argv[0]))
