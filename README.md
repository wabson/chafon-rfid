Chafon RFID reader
==================

This project provides a script which can be used to connect to a Chafon RFID reader
via TCP/IP or serial and upload the times recorded to a Google Sheet.

Installation
------------

Optionally, install pyserial (for serial communication) and Google client (for writing results to a spreadsheet) libs,
via `pip`

    pip install --upgrade google-api-python-client oauth2client pyserial

Follow the steps in the [Google Sheets API Python
Quickstart](https://developers.google.com/sheets/api/quickstart/python),
to allow times to be added to a spreadsheet (optional)

Usage
-----

to install the package into your own project use `pip`

    pip install wabson.chafon-rfid

Examples of how to to use the provided modules are provided in the `examples` directory.

To keep attempting to read tags continuously until Ctrl-C is pressed, run
`continuous-read.py` providing the IP of the reader and optionally the ID of the 
Google Sheet

    PYTHONPATH="${PYTHONPATH}:$(pwd)/chafon-rfid" \
        python examples/continuous-read.py 192.168.1.190 [spreadsheet_id]

A second script `single-read.py` shows how to connect to different types of Chafon 
reader via serial or TCP/IP and obtain information about the reader as well as to 
perform a read.
