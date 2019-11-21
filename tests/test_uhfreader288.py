from chafon_rfid.base import CommandRunner, ReaderCommand
from chafon_rfid.transport import MockTransport
from chafon_rfid.uhfreader288m import G2InventoryCommand, G2InventoryResponse, G2InventoryResponseFrame

from chafon_rfid.command import CF_GET_READER_INFO, G2_TAG_INVENTORY

RESP_TAGS_1 = '1500010301010c0000000000000000000003136bb1a5'
RESP_TAGS_2 = '1500010301010c3039606303c74380001a055940f93e'
RESP_TAGS_3 = '1500010304010c49440000000000000a0003346425c0'
RESP_TAGS_4 = '0d000103010104003230386da3d2'
RESP_NO_TAGS = '0700010101001e4b'
RESP_MULTIPLE_TAGS = '2300010301020c0000000000000000000003136b0c0000000000000000000003146c70f2'


def test_tag_inventory():
    transport = MockTransport(bytearray.fromhex(RESP_TAGS_1))
    command = ReaderCommand(G2_TAG_INVENTORY)
    runner = CommandRunner(transport)
    frame = G2InventoryResponseFrame(runner.run(command))
    assert frame.result_status == 3
    assert frame.resp_cmd == 0x01
    assert frame.reader_addr == 0
    assert frame.antenna == 1
    assert frame.num_tags == 1
    tag = next(frame.get_tag())
    assert tag.epc == bytearray.fromhex('000000000000000000000313')
    assert tag.rssi == 0x6b
    assert tag.antenna_num == 1


def test_tag_inventory_ant3():
    transport = MockTransport(bytearray.fromhex(RESP_TAGS_3))
    command = ReaderCommand(G2_TAG_INVENTORY)
    runner = CommandRunner(transport)
    frame = G2InventoryResponseFrame(runner.run(command))
    assert frame.result_status == 3
    assert frame.resp_cmd == 0x01
    assert frame.reader_addr == 0
    assert frame.antenna == 3
    assert frame.num_tags == 1
    tag = next(frame.get_tag())
    assert tag.epc == bytearray.fromhex('49440000000000000a000334')
    assert tag.rssi == 0x64
    assert tag.antenna_num == 3


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
    assert frame.antenna == 1
    assert frame.num_tags == 2
    tag_generator = frame.get_tag()
    tag1 = next(tag_generator)
    assert tag1.epc == bytearray.fromhex('000000000000000000000313')
    assert tag1.rssi == 0x6b
    assert tag1.antenna_num == 1
    tag2 = next(tag_generator)
    assert tag2.epc == bytearray.fromhex('000000000000000000000314')
    assert tag2.rssi == 0x6c
    assert tag2.antenna_num == 1


def test_inventory_command_defaults():

    command = G2InventoryCommand()
    assert command.data == list(bytearray.fromhex('0f0001000000008014'))


def test_inventory_command():

    command = G2InventoryCommand(q_value=2, session=1, mask_source=2, target=1, scan_time=3)
    assert command.data == list(bytearray.fromhex('020102000000018003'))
