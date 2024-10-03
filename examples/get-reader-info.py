#!/usr/bin/env python

import sys

from chafon_rfid.base import CommandRunner, ReaderCommand, ReaderInfoFrame
from chafon_rfid.command import CF_GET_READER_INFO
from chafon_rfid.transport import TcpTransport
from chafon_rfid.transport_serial import SerialTransport

TCP_PORT = 6000


def get_reader_info(runner):
    get_reader_info = ReaderCommand(CF_GET_READER_INFO)
    reader_info = ReaderInfoFrame(runner.run(get_reader_info))
    return reader_info


def print_reader_info(reader_addr):

    # transport = TcpTransport(reader_addr=reader_addr, reader_port=TCP_PORT)
    # transport = SerialTransport(device='/dev/ttyS0')
    # transport = SerialTransport(device='/dev/ttyAMA0')
    # transport = SerialTransport(device='/dev/ttyUSB0')
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr)
    else:
        transport = TcpTransport(reader_addr, reader_port=TCP_PORT)

    transport.connect()
    runner = CommandRunner(transport)
    try:
        reader_info = get_reader_info(runner)
        print('Reader info: type %s version %d.%d' % (reader_info.type.name, reader_info.firmware_version[0], reader_info.firmware_version[1]))
        print('RF info: power %d dB ' % (reader_info.power))
        print('Frequency info: region %s, %.1f-%.1f MHz' % (reader_info.frequency_band.name, reader_info.get_min_frequency(), reader_info.get_max_frequency()))
    except ValueError as e:
        print('Unknown reader type: {}'.format(e))
        sys.exit(1)

    transport.close()


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        print_reader_info(sys.argv[1])
    else:
        print('Usage: {0} <reader-address>'.format(sys.argv[0]))
