import serial

from chafon_rfid.transport import BaseTransport


class SerialTransport(BaseTransport):

    def __init__(self, device='/dev/ttyUSB0', baud_rate=57600, timeout=5):
        self.serial = serial.Serial(device, baud_rate, timeout=timeout)

    def read_bytes(self, length):
        return bytearray(self.serial.read(length))

    def write_bytes(self, byte_array):
        self.serial.write(byte_array)

    def close(self):
        self.serial.close()
