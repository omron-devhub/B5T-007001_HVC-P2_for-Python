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

from p2def import *
from struct import *
from hvc_result import HVCResult
from serial_connector import SerialConnector
from hvc_result import HVCResult
from grayscale_image import GrayscaleImage

RESPONSE_HEADER_SIZE = 6
SYNC_CODE = 0xFE

# UART baudrate definition.  : for set_uart_baudrate()
HVC_UART_BAUD_9600   = 0x00  #   9600 baud
HVC_UART_BAUD_38400  = 0x01  #  38400 baud
HVC_UART_BAUD_115200 = 0x02  # 115200 baud
HVC_UART_BAUD_230400 = 0x03  # 230400 baud
HVC_UART_BAUD_460800 = 0x04  # 460800 baud
HVC_UART_BAUD_921600 = 0x05  # 921600 baud

# HVC command header fixed part definition
HVC_CMD_HDR_GETVERSION          = b'\xFE\x00\x00\x00'
HVC_CMD_HDR_SET_CAMERA_ANGLE    = b'\xFE\x01\x01\x00'
HVC_CMD_HDR_GET_CAMERA_ANGLE    = b'\xFE\x02\x00\x00'
HVC_CMD_HDR_EXECUTE             = b'\xFE\x04\x03\x00'
HVC_CMD_HDR_SET_THRESHOLD       = b'\xFE\x05\x08\x00'
HVC_CMD_HDR_GET_THRESHOLD       = b'\xFE\x06\x00\x00'
HVC_CMD_HDR_SET_DETECTION_SIZE  = b'\xFE\x07\x0C\x00'
HVC_CMD_HDR_GET_DETECTION_SIZE  = b'\xFE\x08\x00\x00'
HVC_CMD_HDR_SET_FACE_ANGLE      = b'\xFE\x09\x02\x00'
HVC_CMD_HDR_GET_FACE_ANGLE      = b'\xFE\x0A\x00\x00'
HVC_CMD_HDR_SET_UART_BAUDRATE   = b'\xFE\x0E\x01\x00'
HVC_CMD_HDR_REGISTER_DATA       = b'\xFE\x10\x03\x00'
HVC_CMD_HDR_DELETE_DATA         = b'\xFE\x11\x03\x00'
HVC_CMD_HDR_DELETE_USER         = b'\xFE\x12\x02\x00'
HVC_CMD_HDR_DELETE_ALL_DATA     = b'\xFE\x13\x00\x00'
HVC_CMD_HDR_USER_DATA           = b'\xFE\x15\x02\x00'
HVC_CMD_HDR_SAVE_ALBUM          = b'\xFE\x20\x00\x00'
HVC_CMD_HDR_LOAD_ALBUM          = b'\xFE\x21\x04\x00'
HVC_CMD_HDR_SAVE_ALBUM_ON_FLASH = b'\xFE\x22\x00\x00'
HVC_CMD_HDR_REFORMAT_FLASH      = b'\xFE\x30\x00\x00'


class HVCP2Wrapper(object):
    """HVC-P2(B5T-007001) command wrapper class.

    This class provides all commands of HVC-P2.
    """
    __slots__ = ['_connector']
    def __init__(self, connector):
        self._connector = connector

    def connect(self, com_port, baudrate, timeout):
        """Connects to HVC-P2 by COM port via USB or UART interface."""
        if baudrate not in AVAILABLE_BAUD:
            raise ValueError("Invalid baudrate:{0!r}".format(baudrate))

        return self._connector.connect(com_port, baudrate, timeout)

    def disconnect(self):
        """Disconnects to HVC-P2."""
        return self._connector.disconnect()

    def get_version(self):
        """Gets the device's model name, version and revision."""
        cmd = HVC_CMD_HDR_GETVERSION
        (response_code, data_len, data) = self._send_command(cmd)
        if response_code == 0x00: #Success
            hvc_type = data[:12]
            (major, minor, release,) = unpack_from('<BBB', data ,12)
            (revision,) = unpack_from('<I', data ,15)
        else: #error
            (hvc_type, major, minor, release, revision) = None, None, None, None, None
        return (response_code, hvc_type, major, minor, release, revision)

    def set_camera_angle(self, camera_angle):
        """Sets camera angle."""
        cmd = HVC_CMD_HDR_SET_CAMERA_ANGLE + pack('<B', camera_angle)
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def get_camera_angle(self):
        """Gets camera angle."""
        cmd = HVC_CMD_HDR_GET_CAMERA_ANGLE
        (response_code, data_len, data) = self._send_command(cmd)

        if response_code == 0x00: # Success
            (camera_angle,) = unpack('<B', data)
        else: #error
            camera_angle = None
        return (response_code, camera_angle)

    def execute(self, exec_func, out_img_type, frame_result, img):
        """Executes specified functions. e.g. Face detection, Age estimation, etc"""

        # Adds face flag if using facial estimation function
        if exec_func & (EX_DIRECTION|EX_AGE|EX_GENDER|EX_GAZE|EX_BLINK|EX_EXPRESSION):
            exec_func |= EX_FACE + EX_DIRECTION

        cmd = HVC_CMD_HDR_EXECUTE + pack('<H', exec_func) + pack('<B', out_img_type)
        (response_code, data_len, data) = self._send_command(cmd)

        if response_code == 0x00: #Success
            rc = frame_result.read_from_buffer(exec_func, data_len, data)
            if out_img_type != OUT_IMG_TYPE_NONE:
                (width, height) = unpack_from('<HH', data, rc)
                img.width = width
                img.height = height
                img.data = data[rc + 4:]
        return response_code

    def set_threshold(self, body_thresh, hand_thresh, face_thresh,\
                            recognition_thresh):
        """Sets the thresholds value for Human body detection, Hand detection,
           Face detection and/or Recongnition.
        """
        cmd = HVC_CMD_HDR_SET_THRESHOLD\
            + pack('<HHHH',body_thresh, hand_thresh, face_thresh, recognition_thresh)

        response_code, data_len, data = self._send_command(cmd)
        return response_code

    def get_threshold(self):
        """Gets the thresholds value for Human body detection, Hand detection,
           Face detection and/or Recongnition.
        """
        cmd = HVC_CMD_HDR_GET_THRESHOLD
        (response_code, data_len, data) = self._send_command(cmd)

        if response_code == 0x00: # Success
            (body_thresh, hand_thresh, face_thresh, recognition_thresh)\
             = unpack_from('<HHHH', data)
        else: #error
            (body_thresh, hand_thresh, face_thresh, recognition_thresh)\
             = None, None, None, None
        return (response_code,\
                body_thresh, hand_thresh, face_thresh, recognition_thresh)


    def set_detection_size(self, min_body, max_body, min_hand, max_hand,\
                           min_face, max_face):
        """Sets the detection size for Human body detection, Hand detection
           and/or Face detection
        """
        cmd = HVC_CMD_HDR_SET_DETECTION_SIZE +\
            pack('<HHHHHH', min_body, max_body,\
                            min_hand, max_hand,\
                            min_face, max_face)
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def get_detection_size(self):
        """Gets the detection size for Human body detection, Hand detection
           and/or Face detection
        """
        cmd = HVC_CMD_HDR_GET_DETECTION_SIZE
        (response_code, data_len, data) = self._send_command(cmd)

        if response_code == 0x00: # Success
             (min_body, max_body,\
              min_hand, max_hand,\
              min_face, max_face) = unpack_from('<HHHHHH', data)
        else: #error
             (min_body, max_body,\
              min_hand, max_hand,\
              min_face, max_face) = None, None, None, None, None, None
        return (response_code, min_body, max_body,\
                               min_hand, max_hand,\
                               min_face, max_face)


    def set_face_angle(self, yaw_angle, roll_angle):
        """Sets the face angle, i.e. the yaw angle range and the roll angle
           range for Face detection.
        """
        cmd = HVC_CMD_HDR_SET_FACE_ANGLE + pack('<BB', yaw_angle, roll_angle)
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def get_face_angle(self):
        """Gets the face angle range for Face detection."""
        cmd = HVC_CMD_HDR_GET_FACE_ANGLE
        (response_code, data_len, data) = self._send_command(cmd)

        if response_code == 0x00: # Success
             (yaw_angle, roll_angle) = unpack_from('<BB', data)
        else: #error
             (yaw_angle, roll_angle) = None, None
        return (response_code, yaw_angle, roll_angle)

    def set_uart_baudrate(self, baudrate):
        """Sets the UART baudrate."""
        if baudrate not in AVAILABLE_BAUD:
            raise ValueError("Invalid baudrate:{0!r}".format(baudrate))

        baud_index = AVAILABLE_BAUD.index(baudrate)
        cmd = HVC_CMD_HDR_SET_UART_BAUDRATE + pack('<B', baud_index)
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def register_data(self, user_id, data_id, img):
        """Registers data for Recognition and gets a normalized image."""
        cmd = HVC_CMD_HDR_REGISTER_DATA + pack('<HB', user_id, data_id)
        (response_code, data_len, data) = self._send_command(cmd)
        if response_code == 0x00: #Success
            (width, height) = unpack_from('<HH', data)
            img.width = width
            img.height = height
            img.data = data[4:]
        return response_code

    def delete_data(self, user_id, data_id):
        """Deletes a specified registered data. """
        cmd = HVC_CMD_HDR_DELETE_DATA + pack('<HB', user_id, data_id)
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def delete_user(self, user_id):
        """Deletes a specified registered user. """
        cmd = HVC_CMD_HDR_DELETE_USER + pack('<H', user_id)
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def delete_all_data(self):
        """Deletes all the registered data."""
        cmd = HVC_CMD_HDR_DELETE_ALL_DATA
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def get_user_data(self, user_id):
        """Gets the registration info of a specified user."""
        cmd = HVC_CMD_HDR_USER_DATA + pack('<H', user_id)
        (response_code, data_len, data) = self._send_command(cmd)
        if response_code == 0x00: #Success
            (registration_info,) = unpack_from('<H', data)
            data_list = []
            for i in range(10):
#                data_list.append((registration_info and (1 << i))==1)
                data_list.append((registration_info & (1 << i))>>i)
        else: #error
            data_list = None
        return (response_code, data_list)

    def save_album(self):
        """Saves the album on the host side. """
        cmd = HVC_CMD_HDR_SAVE_ALBUM
        (response_code, data_len, data) = self._send_command(cmd)
        return (response_code, data)

    def load_album(self, album):
        """Loads the album from the host side to the device."""
        cmd = HVC_CMD_HDR_LOAD_ALBUM + pack('<I', len(album)) + album
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def save_album_to_flash(self):
        """Saves the album on the flash ROM"""
        cmd = HVC_CMD_HDR_SAVE_ALBUM_ON_FLASH
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def reformat_flash(self):
        """Reformats the album save area on the flash ROM."""
        cmd = HVC_CMD_HDR_REFORMAT_FLASH
        (response_code, data_len, data) = self._send_command(cmd)
        return response_code

    def _send_command(self, data):
        def _receive_header():
            buf = self._connector.receive_data(RESPONSE_HEADER_SIZE)
            if len(buf) != RESPONSE_HEADER_SIZE:
                raise Exception("Response header size is not enough.")

            (sync_code,) = unpack_from('<B', buf, 0)
            if sync_code != SYNC_CODE:
                raise Exception("Invalid Sync code.")

            (response_code,) = unpack_from('<B', buf, 1)
            (data_len,)      = unpack_from('<I', buf, 2)
            return (response_code, data_len)

        def _receive_data(data_len):
            buf = self._connector.receive_data(data_len)
            if len(buf) != data_len:
                raise Exception("Response data size is not enough.")
            return buf

        self._connector.clear_recieve_buffer()
        self._connector.send_data(data)
        (response_code, data_len) = _receive_header()
        if response_code == 0x00 : # Success
            data = _receive_data(data_len)
        else: # error
            data = None
        return (response_code, data_len, data)

if __name__ == '__main__':
    pass