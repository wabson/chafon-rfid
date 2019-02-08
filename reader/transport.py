#!/usr/bin/env python

import abc
import serial
import socket

class BaseTransport(object):

    __metaclass__=abc.ABCMeta
    read_bytecount = 0x100

    def __init__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def read_bytes(self, length):
        raise NotImplementedError

    @abc.abstractmethod
    def write_bytes(self, byte_array):
        raise NotImplementedError

    def read(self):
        return self.read_bytes(self.read_bytecount)

    def read_frame(self):
        length_bytes = self.read_bytes(1)
        frame_length = ord(length_bytes[0])
        data = length_bytes + self.read_bytes(frame_length)
        return bytearray(data)

    def write(self, byte_array):
        self.write_bytes(byte_array)

class SerialTransport(BaseTransport):

    def __init__(self, device='/dev/ttyUSB0', baud_rate=57600, timeout=5):
        self.serial = serial.Serial(device, baud_rate, timeout=timeout)

    def read_bytes(self, length):
        return self.serial.read(length)

    def write_bytes(self, byte_array):
        self.serial.write(byte_array)

    def close(self):
        self.serial.close()

class TcpTransport(BaseTransport):

    buffer_size = 0xFF

    def __init__(self, reader_addr, reader_port, timeout=5, auto_connect=False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.reader_addr = reader_addr
        self.reader_port = reader_port
        if auto_connect:
            self.connect()

    def connect(self):
        self.socket.connect((self.reader_addr, self.reader_port))

    def read_bytes(self, length):
        return self.socket.recv(length)

    def write_bytes(self, byte_array):
        self.socket.sendall(byte_array)

    def close(self):
        self.socket.close()

class MockTransport(BaseTransport):

    def __init__(self, data):
        self.pointer = 0
        self.data = bytes(data)

    def read_bytes(self, length):
        data = self.data[self.pointer:self.pointer+length]
        self.pointer += length
        return data

    def write_bytes(self, byte_array):
        pass

    def close(self):
        pass