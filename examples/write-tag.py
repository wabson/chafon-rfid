#!/usr/bin/env python

# Basic example to write a single tag with an EPC code, which must be a multiple of two bytes

import argparse
import itertools
import time

from math import floor

from chafon_rfid.base import CommandRunner, ReaderCommand, ReaderResponseFrame
from chafon_rfid.command import G2_WRITE_EPC
from chafon_rfid.transport import TcpTransport
from chafon_rfid.transport_serial import SerialTransport

TCP_PORT = 6000
DEFAULT_DELAY = 3
RETRY_DELAY = 1


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


def write_tag_with_confirm(runner, tag_text):
    print('Write EPC data: {}'.format(tag_text))
    while True:
        input('Press Enter to continue')
        if write_tag_value(runner, tag_text) is True:
            break


def write_tag_with_delay(runner, tag_text, delay):
    print('Place tag {} on the reader, writing in {:g}s...'.format(tag_text, delay))
    time.sleep(delay)
    while write_tag_value(runner, tag_text) is not True:
        print('Retrying tag {} in {:g}s...'.format(tag_text, RETRY_DELAY))
        time.sleep(RETRY_DELAY)


def write_tag_text_or_range(runner, text_value, confirm=False, delay=DEFAULT_DELAY):
    if ':' in text_value:
        range_parts = text_value.split(':')
        start_number = int(range_parts[0])
        if range_parts[1] == '':
            # Open range such as 101: - keep counting up until interrupted
            end_number = None
            tag_numbers = itertools.count(start_number)
            print('Writing tags from {} onwards, press Ctrl+C to stop'.format(start_number))
        else:
            end_number = int(range_parts[1])
            tag_numbers = range(start_number, end_number + 1)
        for tag_number in tag_numbers:
            tag_text = str(tag_number)
            if confirm:
                write_tag_with_confirm(runner, tag_text)
            else:
                write_tag_with_delay(runner, tag_text, delay)
        print('Finished writing tags {} to {}'.format(start_number, end_number))
    else:
        write_tag_value(runner, text_value)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Write EPC to a tag')
    parser.add_argument('reader_address', help='Reader address (IP or serial port)')
    parser.add_argument('epc_text', nargs='+', help='EPC text to write to the tag, or a range such as 1:10, or an open range such as 101: which counts up until Ctrl+C is pressed (multiple values allowed)')
    parser.add_argument('--tcp-port', type=int, default=TCP_PORT, help='TCP port for reader connection (default: 6000)')
    parser.add_argument('--baud-rate', type=int, default=57600, help='Baud rate for serial connection (default: 57600)')
    parser.add_argument('--confirm', action='store_true', help='When writing a range, wait for Enter to be pressed before writing each tag')
    parser.add_argument('--delay', type=float, default=DEFAULT_DELAY, help='When writing a range without --confirm, seconds to wait before writing each tag (default: {})'.format(DEFAULT_DELAY))
    args = parser.parse_args()

    reader_addr = args.reader_address
    # transport = TcpTransport(reader_addr=reader_addr, reader_port=TCP_PORT)
    # transport = SerialTransport(device='/dev/ttyS0')
    # transport = SerialTransport(device='/dev/ttyAMA0')
    # transport = SerialTransport(device='/dev/ttyUSB0')
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr, baud_rate=args.baud_rate)
    else:
        transport = TcpTransport(reader_addr, reader_port=args.tcp_port)

    runner = CommandRunner(transport)

    try:
        for tag_value in args.epc_text:
            write_tag_text_or_range(runner, tag_value, confirm=args.confirm, delay=args.delay)
    except KeyboardInterrupt:
        print('\nStopped')
    finally:
        transport.close()
