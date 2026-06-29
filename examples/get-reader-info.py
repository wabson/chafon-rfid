#!/usr/bin/env python

import argparse
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


def print_reader_info(reader_addr, tcp_port, baud_rate):

    # transport = TcpTransport(reader_addr=reader_addr, reader_port=TCP_PORT)
    # transport = SerialTransport(device='/dev/ttyS0')
    # transport = SerialTransport(device='/dev/ttyAMA0')
    # transport = SerialTransport(device='/dev/ttyUSB0')
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr, baud_rate=baud_rate)
    else:
        transport = TcpTransport(reader_addr, reader_port=tcp_port)

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

    parser = argparse.ArgumentParser(description='Get reader info')
    parser.add_argument('reader_address', help='Reader address (IP or serial port)')
    parser.add_argument('--tcp-port', type=int, default=TCP_PORT, help='TCP port for reader connection (default: 6000)')
    parser.add_argument('--baud-rate', type=int, default=57600, help='Baud rate for serial connection (default: 57600)')
    args = parser.parse_args()

    print_reader_info(args.reader_address, args.tcp_port, args.baud_rate)
