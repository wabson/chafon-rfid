Chafon RFID reader
==================

[![Build Status](https://travis-ci.org/wabson/chafon-rfid.svg?branch=master)](https://travis-ci.org/wabson/chafon-rfid)
[![codecov](https://codecov.io/gh/wabson/chafon-rfid/branch/master/graph/badge.svg)](https://codecov.io/gh/wabson/chafon-rfid)

Read and write RFID tags using the popular Chafon UHF-based readers and writers. Originally
written to read race timing chips on a finish line, a range of hardware is now supported from
small desktop USB devices to long-range fixed readers, including the following,

* [CF-RU5102 desktop UHF reader/writer](http://www.chafon.com/productdetails.aspx?pid=384) (not HID version)
* [CF-RU5106](http://www.chafon.com/productdetails.aspx?pid=382) / [CF-RU5112](http://www.chafon.com/productdetails.aspx?pid=383) UHF integrated reader with antenna
* [CF-RU5202 desktop UHF reader/writer](http://www.chafon.com/productdetails.aspx?pid=535)
* CF-RU6402 fixed UHF reader (Impinj R2000, 4-port)
* [CF-MU801](http://chafon.com/productdetails.aspx?pid=667) / [CF-MU804](http://chafon.com/productdetails.aspx?pid=669) (Impinj R2000, 1-port or 4-port) UHF module
* [CF-MU904 UHF module](http://www.chafon.com/productdetails.aspx?pid=565) (own brand, 1-port)

You can connect to the reader/writer via the following standard connections

* USB (recommended)
* Direct serial connection
* Ethernet connection

The library supports a basic set of commands to perform tag inventories, write tag EPC values
and get and set reader parameters. Helpers are provided to allow you to implement any other
documented commands, which automatically take care of constructing commands, generating and
verifying checksums and connecting to the reader/writer.

See the [examples](examples/) folder for details of how to connect, send commands and read
responses.

Requirements
------------

This module requires *Python 3.4+* but should work under any OS.

For serial communication using the built-in transport class, [pyserial](https://pyserial.readthedocs.io/) is required. Other implementations are possible for MicroPython/CircuitPython environments.

Some examples may have additional requirements, see comments in the individual files.

Installation
------------

To install the package into your own project, use `pip`

    pip install --upgrade wabson.chafon-rfid

Usage
-----

Examples of how to to use the provided module are provided in the [examples](examples/) directory.
