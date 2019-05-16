# ---------------------------------------------------------------------------
# Copyright 2017-2018  OMRON Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import serial
from connector import Connector

DEFALUT_TIMEOUT = 3

class SerialConnector(Connector):
    """Serial connector class"""
    __slots__ = ['is_connected', 'com_port', 'baudrate', 'timeout']

    def __init__(self):
        self._ser = serial.Serial()
        self._is_connected = False

    def connect(self, com_port, baudrate, timeout):
        self._ser.port = com_port
        self._ser.baudrate = baudrate
        self._ser.timeout = timeout
        self._ser.open()
        self._is_connected = True
        return True

    def disconnect(self):
        self._ser.close()
        self._is_connected = False

    def clear_recieve_buffer(self):
        self._ser.flushInput()

    def send_data(self, data):
        if self._is_connected == False:
            raise Exception('Serial port has not connected yet!')

        self._ser.write(data)
        return True

    def receive_data(self, read_byte_size):
        if self._is_connected == False :
            raise Exception('Serial port has not connected yet!')

        return self._ser.read(read_byte_size)

if __name__ == '__main__':
    main()

