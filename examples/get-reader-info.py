#!/usr/bin/env python

import sys

from chafon_rfid.base import CommandRunner, ReaderCommand, ReaderInfoFrame
from chafon_rfid.command import CF_GET_READER_INFO
from chafon_rfid.transport import TcpTransport
from chafon_rfid.transport_serial import SerialTransport

def get_reader_info(runner):
    get_reader_info = ReaderCommand(CF_GET_READER_INFO)
    reader_info = ReaderInfoFrame(runner.run(get_reader_info))
    return reader_info

def print_reader_info(reader_addr, baud_rate=None, tcp_port=None):
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr, baud_rate=baud_rate)
    else:
        transport = TcpTransport(reader_addr, reader_port=tcp_port, auto_connect=True)

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

def print_usage_instruction():
    print('Usage: {0} <connection_type> <reader-address> <baud-rate> OR <tcp-port>'.format(sys.argv[0]))


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        if sys.argv[1] == 'com':
            print_reader_info(sys.argv[2], baud_rate=sys.argv[3])
        elif sys.argv[1] == 'tcp':
            print_reader_info(sys.argv[2], tcp_port=int(sys.argv[3]))
        else:
            print_usage_instruction()
    else:
        print_usage_instruction()

