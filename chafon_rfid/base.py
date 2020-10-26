from .checksum import checksum
from enum import Enum


class ReaderCommand(object):

    def __init__(self, cmd, addr=0xFF, data=[]):
        self.addr = addr
        self.cmd = cmd
        self.data = data

    def serialize(self):
        frame_length = 4 + len(self.data)
        base_data = bytearray([ frame_length, self.addr, self.cmd ]) + bytearray(self.data)
        base_data.extend(bytearray(self.checksum_bytes(base_data)))
        return base_data

    def checksum_bytes(self, data_bytes):
        crc = checksum(data_bytes)
        crc_msb = crc >> 8
        crc_lsb = crc & 0xFF
        return bytearray([ crc_lsb, crc_msb ])


class CommandRunner(object):

    def __init__(self, transport):
        self.transport = transport

    def run(self, command):
        self.transport.write(command.serialize())
        return self.transport.read_frame()


class ReaderResponseFrame(object):

    def __init__(self, resp_bytes, offset=0):
        if len(resp_bytes) < 5:
            raise ValueError('Response must be at least 5 bytes')
        self.len = resp_bytes[offset]
        if self.len + offset > len(resp_bytes) - 1:
            raise ValueError('Response does not contain enough bytes for frame (expected %d bytes after offset %d, actual length %d)' % (self.len, offset, len(resp_bytes)))
        self.reader_addr = resp_bytes[offset+1]
        self.resp_cmd = resp_bytes[offset+2]
        self.result_status = resp_bytes[offset+3]
        self.data = resp_bytes[offset+4:offset+self.len-1]
        cs_status = self.verify_checksum(resp_bytes[offset:offset+self.len-1], resp_bytes[offset+self.len-1:offset+self.len+1])
        if cs_status is not True:
            raise(ValueError('Checksum does not match'))

    def verify_checksum(self, data_bytes, checksum_bytes):
        data_crc = checksum(bytearray(data_bytes))
        crc_msb = data_crc >> 8
        crc_lsb = data_crc & 0xFF
        return checksum_bytes[0] == crc_lsb and checksum_bytes[1] == crc_msb

    def __len__(self):
        return self.len

    def get_data(self):
        return self.data


class ReaderFrequencyBand(Enum):

    China2  = 0b0001
    US      = 0b0010
    Korea   = 0b0011
    EU      = 0b0100
    Ukraine = 0b0110
    Peru    = 0b0111
    China1  = 0b1000
    EU3     = 0b1001
    Taiwan  = 0b1010
    US3     = 0b1100


class ReaderType(Enum):

    RRU9803M      = 0x03 # CF-RU5102 (desktop USB reader/writer, as specified)
    RRU9803M_1    = 0x08 # CF-RU5102 (desktop USB reader/writer, actual)
    UHFReader18   = 0x09
    UHFReader288M = 0x0c
    UHFReader86   = 0x0f # CF-MU903/CF-MU904 (as documented)
    UHFReader86_1 = 0x10 # CF-MU903/CF-MU904 (actual)
    RRU9883M      = 0x16 # CF-MU902
    UHFReader288MP = 0x20 # CF-MU804


class ReaderInfoFrame(ReaderResponseFrame):

    def __init__(self, resp_bytes):
        super(ReaderInfoFrame, self).__init__(resp_bytes)
        if len(self.data) >= 8:
            self.firmware_version = self.data[0:2]
            self.type = ReaderType(self.data[2])
            self.supports_6b = (self.data[3] & 0b01) > 0
            self.supports_6c = (self.data[3] & 0b10) > 0
            dmaxfre = self.data[4]
            dminfre = self.data[5]
            self.max_frequency = dmaxfre & 0b00111111
            self.min_frequency = dminfre & 0b00111111
            self.frequency_band = ReaderFrequencyBand(((dmaxfre & 0b11000000 ) >> 4) + ((dminfre & 0b11000000 ) >> 6))
            self.power = self.data[6]
            self.scan_time = self.data[7]
        else:
            raise ValueError('Data must be at least 8 characters')

    def get_regional_frequency(self, fnum):
        if self.frequency_band is ReaderFrequencyBand.EU:
            return 865.1 + fnum * 0.2
        elif self.frequency_band is ReaderFrequencyBand.China2:
            return 920.125 + fnum * 0.25
        elif self.frequency_band is ReaderFrequencyBand.US:
            return 902.75 + fnum * 0.5
        elif self.frequency_band is ReaderFrequencyBand.Korea:
            return 917.1 + fnum * 0.2
        elif self.frequency_band is ReaderFrequencyBand.Ukraine:
            return 868.0 + fnum * 0.1
        elif self.frequency_band is ReaderFrequencyBand.Peru:
            return 916.2 + fnum * 0.9
        elif self.frequency_band is ReaderFrequencyBand.China1:
            return 840.125 + fnum * 0.25
        elif self.frequency_band is ReaderFrequencyBand.EU3:
            return 865.7 + fnum * 0.6
        elif self.frequency_band is ReaderFrequencyBand.US3:
            return 902 + fnum * 0.5
        elif self.frequency_band is ReaderFrequencyBand.Taiwan:
            return 922.25 + fnum * 0.5
        else:
            return fnum

    def get_min_frequency(self):
        return self.get_regional_frequency(self.min_frequency)

    def get_max_frequency(self):
        return self.get_regional_frequency(self.max_frequency)


class G2InventoryResponse(object):

    frame_class = None

    def __init__(self, resp_bytes):
        self.resp_bytes = resp_bytes

    def get_frame(self):
        offset = 0
        while offset < len(self.resp_bytes):
            next_frame = self.frame_class(self.resp_bytes, offset=offset)
            offset += len(next_frame) + 1 # For a frame with stated length N there are N+1 bytes
            yield next_frame

    def get_tag(self):
        for response_frame in self.get_frame():
            for tag in response_frame.get_tag():
                yield tag


class TagData(object):

    def __init__(self, resp_bytes, prefix_bytes=0, suffix_bytes=0):
        self.prefix_bytes = prefix_bytes
        self.suffix_bytes = suffix_bytes
        self.data = resp_bytes
        self.num_tags = resp_bytes[0]

    def get_tag_data(self):
        n = 0
        pointer = 1
        while n < self.num_tags:
            tag_len = int(self.data[pointer])
            tag_data_start = pointer + 1
            tag_main_start = tag_data_start + self.prefix_bytes
            tag_main_end = tag_main_start + tag_len
            next_tag_start = tag_main_end + self.suffix_bytes
            yield (self.data[tag_data_start:tag_main_start], self.data[tag_main_start:tag_main_end], self.data[tag_main_end:next_tag_start])
            pointer = next_tag_start
            n += 1


class Tag(object):

    def __init__(self, epc, antenna_num=1, rssi=None):
        self.epc = epc
        self.antenna_num = antenna_num
        self.rssi = rssi
