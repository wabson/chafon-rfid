import binascii

from chafon_rfid.base import CommandRunner, ReaderCommand, ReaderInfoFrame
from chafon_rfid.command import CF_GET_READER_INFO, G2_TAG_INVENTORY
from chafon_rfid.response import G2_TAG_INVENTORY_STATUS_MORE_FRAMES
from chafon_rfid.transport import TcpTransport, MockTransport
from chafon_rfid.transport_serial import SerialTransport
from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as G2InventoryResponseFrame18
from chafon_rfid.uhfreader288m import G2InventoryCommand, G2InventoryResponseFrame as G2InventoryResponseFrame288

get_reader_info = ReaderCommand(CF_GET_READER_INFO)
get_inventory_288 = G2InventoryCommand(q_value=4)
get_inventory_uhfreader18 = ReaderCommand(G2_TAG_INVENTORY)

#transport = MockTransport(bytearray.fromhex('1100210000160c034e001e0a01000000e651' + '1500010301010c0000000000000000000003136bb1a51500010301010c3039606303c74380001a055940f93e1500010301010c49440000000000000a0003346457660d000103010104003230386da3d20700010101001e4b'))
#transport = SerialTransport(auto_connect=True)
#transport = TcpTransport(reader_addr='192.168.0.250', reader_port=27011)
transport = TcpTransport(reader_addr='192.168.1.190', reader_port=6000)
runner = CommandRunner(transport)

reader_info = ReaderInfoFrame(runner.run(get_reader_info))
print('Reader info: type %s version %d.%d, power %d dB ' % (reader_info.type.name, reader_info.firmware_version[0], reader_info.firmware_version[1], reader_info.power))
print('Frequency info: region %s, %.1f-%.1f MHz' % (reader_info.frequency_band.name, reader_info.get_min_frequency(), reader_info.get_max_frequency()))

#transport.write(get_inventory_288.serialize())
transport.write(get_inventory_uhfreader18.serialize())
inventory_status = None
while inventory_status is None or inventory_status == G2_TAG_INVENTORY_STATUS_MORE_FRAMES:
    #g2_response = G2InventoryResponseFrame288(transport.read_frame())
    g2_response = G2InventoryResponseFrame18(transport.read_frame())
    inventory_status = g2_response.result_status
    for tag in g2_response.get_tag():
        print('Antenna %d: EPC %s, RSSI %s' % (tag.antenna_num, binascii.hexlify(tag.epc), tag.rssi))

transport.close()
