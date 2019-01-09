Chafon RFID reader
==================

This project provides a script which can be used to connect to a Chafon RFID reader
via TCP/IP and upload the times recorded to a Google Sheet.

Installation
------------

Install Google client libs via `pip`

    pip install --upgrade google-api-python-client oauth2client

Usage
-----

Run the script providing the IP of the reader and the ID of the Google Sheet

    python read-tags.py 192.168.1.190 <SPREADSHEET_ID>

