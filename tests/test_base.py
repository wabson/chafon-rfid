import pytest

from chafon_rfid.base import CommandRunner, ReaderCommand, ReaderInfoFrame, \
    ReaderResponseFrame, ReaderFrequencyBand
from chafon_rfid.transport import MockTransport

from chafon_rfid.command import CF_GET_READER_INFO, G2_TAG_INVENTORY

RESP_READER_INFO = '1100210000160c034e001e0a01000000e651'
RESP_TAGS_BAD_CHECKSUM = '1500010301010c0000000000000000000003136bb1a6'
RESP_TAGS_BAD_RETURN_COMMAND = '1500020301010c0000000000000000000003136b89a4'


def test_reader_info_frame():
    transport = MockTransport(bytearray.fromhex(RESP_READER_INFO))
    get_reader_info = ReaderCommand(CF_GET_READER_INFO)
    runner = CommandRunner(transport)
    reader_info = ReaderInfoFrame(runner.run(get_reader_info))
    assert reader_info.result_status == 0
    assert reader_info.resp_cmd == 0x21
    assert reader_info.reader_addr == 0
    assert reader_info.data == bytearray.fromhex('00160c034e001e0a01000000')
    assert reader_info.firmware_version == bytearray([0, 22])
    # 0x4E = 0b 01 00 1110 Max
    # 0x00 = 0b0 Min
    assert reader_info.frequency_band == ReaderFrequencyBand.EU
    assert reader_info.get_max_frequency() == 865.1 + 0.2*14
    assert reader_info.get_min_frequency() == 865.1


def test_reader_frame_bad_checksum():
    transport = MockTransport(bytearray.fromhex(RESP_TAGS_BAD_CHECKSUM))
    get_reader_info = ReaderCommand(G2_TAG_INVENTORY)
    runner = CommandRunner(transport)
    with pytest.raises(ValueError):
        assert ReaderResponseFrame(runner.run(get_reader_info))


# def test_command_runner_bad_return_command():
#     transport = MockTransport(bytearray.fromhex(RESP_TAGS_BAD_RETURN_COMMAND))
#     get_reader_info = ReaderCommand(G2_TAG_INVENTORY)
#     runner = CommandRunner(transport)
#     with pytest.raises(ValueError):
#         ReaderResponseFrame(runner.run(get_reader_info))
