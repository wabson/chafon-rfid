#!/usr/bin/env python

import serial
import socket

class SerialTransport(object):

    read_bytecount = 0x100

    def __init__(self, device='/dev/ttyUSB0', baud_rate=57600, timeout=0.5):
        self.serial = serial.Serial(device, baud_rate, timeout=timeout)

    def write(self, byte_array):
        self.serial.write(byte_array)

    def read(self):
        #return bytearray(self.serial.read(self.read_bytecount))
        length_bytes = self.serial.read(1)
        length = ord(length_bytes[0])
        data = bytearray(length_bytes + self.serial.read(self.read_bytecount))
        print binascii.hexlify(data)
        return data

    def close(self):
        self.serial.close()

class TcpTransport(object):

    buffer_size = 0xFF

    def __init__(self, reader_addr, reader_port, timeout=5):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((reader_addr, reader_port))

    def write(self, byte_array):
        self.socket.sendall(byte_array)

    def read(self):
        return bytearray(self.socket.recv(self.buffer_size))

    def close(self):
        self.socket.close()