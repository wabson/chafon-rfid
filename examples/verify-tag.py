#!/usr/bin/env python

# Basic example to verify tags have the expected EPC code, as written by write-tag.py. Takes the
# same EPC text or range arguments, and checks each tag in turn by performing an inventory.

import argparse

from chafon_rfid.base import CommandRunner, ReaderCommand
from chafon_rfid.command import G2_TAG_INVENTORY
from chafon_rfid.response import G2_TAG_INVENTORY_STATUS_MORE_FRAMES
from chafon_rfid.transport import TcpTransport
from chafon_rfid.transport_serial import SerialTransport
from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as G2InventoryResponseFrame18

TCP_PORT = 6000

get_inventory = ReaderCommand(G2_TAG_INVENTORY)


def expected_epc_bytes(tag_value):
    # Must match the encoding used by write-tag.py
    epc_bytes = list(tag_value.encode('ascii'))
    if len(epc_bytes) % 2 > 0:
        epc_bytes.insert(0, 0)
    return bytes(epc_bytes)


def read_epcs(transport):
    transport.write(get_inventory.serialize())
    epcs = []
    inventory_status = None
    while inventory_status is None or inventory_status == G2_TAG_INVENTORY_STATUS_MORE_FRAMES:
        g2_response = G2InventoryResponseFrame18(transport.read_frame())
        inventory_status = g2_response.result_status
        for tag in g2_response.get_tag():
            epcs.append(bytes(tag.epc))
    return epcs


def verify_tag_value(transport, tag_value):
    expected = expected_epc_bytes(tag_value)
    epcs = read_epcs(transport)
    if not epcs:
        print('Error: No tags found, is a tag in place?')
        return False
    if len(epcs) > 1:
        print('Error: {} tags found, place only one tag near the reader: {}'.format(
            len(epcs), ', '.join(e.hex() for e in epcs)))
        return False
    if epcs[0] == expected:
        print('OK: tag EPC matches {}'.format(tag_value))
        return True
    print('MISMATCH: expected {} ({}), found {}'.format(expected.hex(), tag_value, epcs[0].hex()))
    return False


def expand_values(text_value):
    if ':' in text_value:
        start_number, end_number = (int(p) for p in text_value.split(':'))
        return [str(n) for n in range(start_number, end_number + 1)]
    return [text_value]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Verify the EPC of tags')
    parser.add_argument('reader_address', help='Reader address (IP or serial port)')
    parser.add_argument('epc_text', nargs='+', help='Expected EPC text, or a range such as 1:10 (multiple values allowed)')
    parser.add_argument('--tcp-port', type=int, default=TCP_PORT, help='TCP port for reader connection (default: 6000)')
    parser.add_argument('--baud-rate', type=int, default=57600, help='Baud rate for serial connection (default: 57600)')
    args = parser.parse_args()

    reader_addr = args.reader_address
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr, baud_rate=args.baud_rate)
    else:
        transport = TcpTransport(reader_addr, reader_port=args.tcp_port)

    transport.connect()
    runner = CommandRunner(transport)

    failed = []
    for arg in args.epc_text:
        for tag_value in expand_values(arg):
            print('Verify EPC data: {}'.format(tag_value))
            input('Press Enter to continue')
            if not verify_tag_value(transport, tag_value):
                failed.append(tag_value)

    transport.close()

    if failed:
        print('Failed to verify: {}'.format(', '.join(failed)))
        raise SystemExit(1)
    print('All tags verified')
