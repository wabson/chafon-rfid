#!/usr/bin/env python

# Basic example to verify tags have the expected EPC code, as written by write-tag.py. Takes the
# same EPC text or range arguments, and checks each tag in turn by performing an inventory.

import argparse
import itertools
import re
import time

from chafon_rfid.base import CommandRunner, ReaderCommand
from chafon_rfid.command import G2_TAG_INVENTORY
from chafon_rfid.response import G2_TAG_INVENTORY_STATUS_MORE_FRAMES
from chafon_rfid.transport import TcpTransport
from chafon_rfid.transport_serial import SerialTransport
from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as G2InventoryResponseFrame18

TCP_PORT = 6000
DEFAULT_DELAY = 3
RETRY_DELAY = 1
RANGE_PATTERN = re.compile(r'(\d+)[:-](\d*)')

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
    """Returns True if the tag matches, False if it does not, or None if the tag could not be
    read reliably (no tag, or more than one tag) and the check should be retried."""
    expected = expected_epc_bytes(tag_value)
    epcs = read_epcs(transport)
    if not epcs:
        print('Error: No tags found, is a tag in place?')
        return None
    if len(epcs) > 1:
        print('Error: {} tags found, place only one tag near the reader: {}'.format(
            len(epcs), ', '.join(e.hex() for e in epcs)))
        return None
    if epcs[0] == expected:
        print('OK: tag EPC matches {}'.format(tag_value))
        return True
    print('MISMATCH: expected {} ({}), found {}'.format(expected.hex(), tag_value, epcs[0].hex()))
    return False


def verify_tag_with_confirm(transport, tag_text):
    print('Verify EPC data: {}'.format(tag_text))
    while True:
        input('Press Enter to continue')
        result = verify_tag_value(transport, tag_text)
        if result is not None:
            return result


def verify_tag_with_delay(transport, tag_text, delay):
    print('Place tag {} on the reader, verifying in {:g}s...'.format(tag_text, delay))
    time.sleep(delay)
    while True:
        result = verify_tag_value(transport, tag_text)
        if result is not None:
            return result
        print('Retrying tag {} in {:g}s...'.format(tag_text, RETRY_DELAY))
        time.sleep(RETRY_DELAY)


def verify_tag_text_or_range(transport, text_value, failed, confirm=False, delay=DEFAULT_DELAY):
    range_match = RANGE_PATTERN.fullmatch(text_value)
    if range_match:
        start_number = int(range_match.group(1))
        # Keep any leading zeros typed in the range start, e.g. 001: gives 001, 002, ...
        number_width = len(range_match.group(1))
        if range_match.group(2) == '':
            # Open range such as 101: or 101- - keep counting up until interrupted
            end_number = None
            tag_numbers = itertools.count(start_number)
            print('Verifying tags from {} onwards, press Ctrl+C to stop'.format(start_number))
        else:
            end_number = int(range_match.group(2))
            tag_numbers = range(start_number, end_number + 1)
        for tag_number in tag_numbers:
            tag_text = str(tag_number).zfill(number_width)
            if confirm:
                ok = verify_tag_with_confirm(transport, tag_text)
            else:
                ok = verify_tag_with_delay(transport, tag_text, delay)
            if not ok:
                failed.append(tag_text)
        print('Finished verifying tags {} to {}'.format(start_number, end_number))
    elif not verify_tag_value(transport, text_value):
        failed.append(text_value)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Verify the EPC of tags')
    parser.add_argument('reader_address', help='Reader address (IP or serial port)')
    parser.add_argument('epc_text', nargs='+', help='Expected EPC text, or a range such as 1:10 or 1-10, or an open range such as 101: or 101- which counts up until Ctrl+C is pressed (multiple values allowed)')
    parser.add_argument('--tcp-port', type=int, default=TCP_PORT, help='TCP port for reader connection (default: 6000)')
    parser.add_argument('--baud-rate', type=int, default=57600, help='Baud rate for serial connection (default: 57600)')
    parser.add_argument('--confirm', action='store_true', help='When verifying a range, wait for Enter to be pressed before checking each tag')
    parser.add_argument('--delay', type=float, default=DEFAULT_DELAY, help='When verifying a range without --confirm, seconds to wait before checking each tag (default: {})'.format(DEFAULT_DELAY))
    args = parser.parse_args()

    reader_addr = args.reader_address
    if reader_addr.startswith('/') or reader_addr.startswith('COM'):
        transport = SerialTransport(device=reader_addr, baud_rate=args.baud_rate)
    else:
        transport = TcpTransport(reader_addr, reader_port=args.tcp_port)

    transport.connect()
    runner = CommandRunner(transport)

    failed = []
    try:
        for tag_value in args.epc_text:
            verify_tag_text_or_range(transport, tag_value, failed, confirm=args.confirm, delay=args.delay)
    except KeyboardInterrupt:
        print('\nStopped')
    finally:
        transport.close()

    if failed:
        print('Failed to verify: {}'.format(', '.join(failed)))
        raise SystemExit(1)
    print('All tags verified')
