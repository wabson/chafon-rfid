from chafon_rfid.base import CommandRunner, ReaderCommand
from chafon_rfid.transport import MockTransport
from chafon_rfid.uhfreader18 import G2InventoryResponse, G2InventoryResponseFrame

from chafon_rfid.command import G2_TAG_INVENTORY

RESP_TAGS_1 = '13000103010c0000000000000000000003133f39'
RESP_TAGS_3 = '13000103010c49440000000000000a000334a5fb'
RESP_MULTIPLE_TAGS = '20000103020c0000000000000000000003130c0000000000000000000003149ac9'


def test_tag_inventory():
    transport = MockTransport(bytearray.fromhex(RESP_TAGS_1))
    command = ReaderCommand(G2_TAG_INVENTORY)
    runner = CommandRunner(transport)
    frame = G2InventoryResponseFrame(runner.run(command))
    assert frame.result_status == 3
    assert frame.resp_cmd == 0x01
    assert frame.reader_addr == 0
    assert frame.num_tags == 1
    tag = next(frame.get_tag())
    assert tag.epc == bytearray.fromhex('000000000000000000000313')
    assert tag.rssi is None
    assert tag.antenna_num == 1


def test_multiple_tags():
    transport = MockTransport(bytearray.fromhex(RESP_MULTIPLE_TAGS))
    command = ReaderCommand(G2_TAG_INVENTORY)
    runner = CommandRunner(transport)
    response = G2InventoryResponse(runner.run(command))
    frame_generator = response.get_frame()
    frame = next(frame_generator)
    assert frame.result_status == 3
    assert frame.resp_cmd == 0x01
    assert frame.reader_addr == 0
    assert frame.num_tags == 2
    tag_generator = frame.get_tag()
    tag1 = next(tag_generator)
    assert tag1.epc == bytearray.fromhex('000000000000000000000313')
    assert tag1.rssi is None
    assert tag1.antenna_num == 1
    tag2 = next(tag_generator)
    assert tag2.epc == bytearray.fromhex('000000000000000000000314')
    assert tag2.rssi is None
    assert tag2.antenna_num == 1
