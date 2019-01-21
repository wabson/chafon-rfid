import binascii

from reader.base import CommandRunner, ReaderCommand, ReaderInfoFrame
from reader.command import CF_GET_READER_INFO
from reader.transport import SerialTransport, TcpTransport
from reader.uhfreader288m import G2InventoryCommand, G2InventoryResponse

get_reader_info = ReaderCommand(CF_GET_READER_INFO)
get_inventory_288 = G2InventoryCommand(q_value=4)

#transport = SerialTransport()
transport = TcpTransport(reader_addr=192.168.0.250, reader_port=27011)
runner = CommandRunner(transport)

reader_info = ReaderInfoFrame(runner.run(get_reader_info))
print 'Reader info: type %s version %d.%d, power %d dB ' % (reader_info.type.name, reader_info.firmware_version[0], reader_info.firmware_version[1], reader_info.power)
print 'Frequency info: %.1f-%.1f MHz region %s' % (reader_info.get_min_frequency(), reader_info.get_max_frequency(), reader_info.frequency_band.name)

g2_response = G2InventoryResponse(runner.run(get_inventory_288))
for tag in g2_response.get_tag():
    print 'Antenna %d: EPC %s, RSSI %d' % (tag.antenna_num, binascii.hexlify(tag.epc), tag.rssi)

transport.close()
