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

import os.path
import sys
import time
import p2def
from serial_connector import SerialConnector
from hvc_p2_api import HVCP2Api
from hvc_tracking_result import HVCTrackingResult
from grayscale_image import GrayscaleImage

###############################################################################
#  User Config. Please edit here if you need.
###############################################################################
# Output image file name.
img_fname = 'registerd_img.jpg'

# Read timeout value in seconds for serial communication.
# If you use UART slow baudrate, please edit here.
timeout = 30

# Album file name.
album_fname = 'Album.dat'

# HVC Camera Angle setting
hvc_camera_angle = p2def.HVC_CAM_ANGLE_0
                       # HVC_CAM_ANGLE_90
                       # HVC_CAM_ANGLE_180
                       # HVC_CAM_ANGLE_270

# Threshold value settings
body_thresh = 500        # Threshold for Human body detection [1 to 1000]
hand_thresh = 500        # Threshold for Hand detection       [1 to 1000]
face_thresh = 500        # Threshold for Face detection       [1 to 1000]
recognition_thresh = 500  # Threshold for Face recognition    [0 to 1000]

# Detection Size setings
min_body_size = 30      # Mininum Human body detection size [20 to 8192]
max_body_size = 8192    # Maximum Human body detection size [20 to 8192]
min_hand_size = 40      # Mininum Hand detection size       [20 to 8192]
max_hand_size = 8192    # Maximum Hand detection size       [20 to 8192]
min_face_size = 64      # Mininum Face detection size       [20 to 8192]
max_face_size = 8192    # Maximum Face detection size       [20 to 8192]

# Execute functions
exec_func = p2def.EX_FACE\
          | p2def.EX_DIRECTION\
          | p2def.EX_RECOGNITION

# Detection face angle settings
face_angle_yaw  = p2def.HVC_FACE_ANGLE_YAW_30
face_angle_roll = p2def.HVC_FACE_ANGLE_ROLL_15
                      # HVC_FACE_ANGLE_ROLL_45
###############################################################################

def _parse_arg(argv):
    if len(argv) == 3:
        # Gets port infomation
        portinfo = argv[1]
        # Gets baudrate
        baudrate = int(argv[2])
        if baudrate not in p2def.AVAILABLE_BAUD:
            print "Error: Invalid baudrate."
            sys.exit()
    else:
        print "Error: Invalid argument."
        sys.exit()
    return (portinfo, baudrate)

def _check_connection(hvc_p2_api):
    (res_code, hvc_type, major, minor, release, rev) = hvc_p2_api.get_version()
    if res_code == 0 and hvc_type.startswith('B5T-007001'):
        pass
    else:
        raise IOError("Error: connection failure.")

def _set_hvc_p2_parameters(hvc_p2_api):
    # Sets camera angle
    res_code = hvc_p2_api.set_camera_angle(hvc_camera_angle)
    if res_code is not p2def.RESPONSE_CODE_NORMAL:
        raise ValueError("Error: Invalid camera angle.")

    # Sets threshold
    res_code = hvc_p2_api.set_threshold(body_thresh, hand_thresh,\
                                        face_thresh, recognition_thresh)
    if res_code is not p2def.RESPONSE_CODE_NORMAL:
        raise ValueError("Error: Invalid threshold.")

    # Sets detection size
    res_code = hvc_p2_api.set_detection_size(min_body_size, max_body_size,\
                                             min_hand_size, max_hand_size,\
                                             min_face_size, max_face_size)
    if res_code is not p2def.RESPONSE_CODE_NORMAL:
        raise ValueError("Error: Invalid detection size.")

    # Sets face angle
    res_code = hvc_p2_api.set_face_angle(face_angle_yaw, face_angle_roll)
    if res_code is not p2def.RESPONSE_CODE_NORMAL:
        raise ValueError("Error: Invalid face angle.")

def main():
    # Parses arguments
    (portinfo, baudrate) = _parse_arg(sys.argv)

    connector = SerialConnector()
    hvc_p2_api = HVCP2Api(connector, exec_func, p2def.USE_STB_OFF)

    # The 1st connection
    hvc_p2_api.connect(portinfo, p2def.DEFAULT_BAUD, 10) # 1st connection should be 9600 baud.
    _check_connection(hvc_p2_api)
    hvc_p2_api.set_uart_baudrate(baudrate) # Changing to the specified baud rate
    hvc_p2_api.disconnect()

    # The 2nd connection in specified baudrate
    hvc_p2_api.connect(portinfo, baudrate, timeout)
    _check_connection(hvc_p2_api)

    try:
        # Sets HVC-P2 parameters
        _set_hvc_p2_parameters(hvc_p2_api)

        img = GrayscaleImage()

        # Main loop
        while True:
            str = "\n"\
                + "Please select the command.\n"\
                + "   r : registration.\n"\
                + "   g : get user data.\n"\
                + "   s : save album.\n"\
                + "   l : load album.\n"\
                + "   d : delete all album data.\n"\
                + "   x : exit.\n"\
                + "  >>"
            operation_str = raw_input(str)
            if operation_str == 'x':
                break

            if operation_str == 'r':
                while True:
                    str_uid = raw_input('user id [0-99] ')
                    if str_uid >= '0' and str_uid <= '99':
                        user_id = int(str_uid)
                        break
                while True:
                    str_did = raw_input('data id [0-9] ')
                    if str_did >= '0' and str_did <= '9':
                        data_id = int(str_did)
                        break
                raw_input('Press Enter key to register.')
                res_code = hvc_p2_api.register_data(user_id, data_id, img)
                if res_code < p2def.RESPONSE_CODE_NORMAL: # error
                    print "Error: Invalid register album."
                    break
                if res_code == p2def.RESPONSE_CODE_NO_FACE:
                    print "\nNumber of faces that can be registered is 0."
                if res_code == p2def.RESPONSE_CODE_PLURAL_FACE:
                    print "\nNumber of detected faces is 2 or more."
                if res_code == p2def.RESPONSE_CODE_NORMAL: # success
                    img.save(img_fname)
                    print"Success to register. user_id=" + str_uid \
                          + "  data_id=" + str_did

            if operation_str == 'g':
                while True:
                    str_uid = raw_input('user id [0-99] ')
                    if str_uid >= '0' and str_uid <= '99':
                        user_id = int(str_uid)
                        break
                print "uid[{0}]: ".format(user_id),
                (res_code, data_list) = hvc_p2_api.get_user_data(user_id)
                if res_code < p2def.RESPONSE_CODE_NORMAL: # error
                    print "Error: Invalid register album."
                    break
                print data_list

            if operation_str == 's':
                # Saves album to flash ROM on B5T-007001.
                res_code = hvc_p2_api.save_album_to_flash()
                if res_code is not p2def.RESPONSE_CODE_NORMAL:
                    print "Error: Invalid save album to flash."
                    break
                # Saves album to the file.
                res_code, save_album = hvc_p2_api.save_album()
                if res_code is not p2def.RESPONSE_CODE_NORMAL:
                    print "Error: Invalid save album."
                    break
                with open(album_fname, "wb") as file:
                    file.write(save_album)

                print ("Success to save album.")

            if operation_str == 'l':
                # Loads album from file
                if os.path.isfile(album_fname):
                    with open(album_fname, "rb") as file:
                      load_album = file.read()

                res_code = hvc_p2_api.load_album(load_album)
                if res_code is not p2def.RESPONSE_CODE_NORMAL:
                    print "Error: Invalid load album."
                    break
                print "Success to load album."

            if operation_str == 'd':
                # Deletes all album data
                res_code = hvc_p2_api.delete_all_data()
                if res_code is not p2def.RESPONSE_CODE_NORMAL:
                    print "Error: Invalid save album to flash."
                    break
                # Saves album to flash ROM on B5T-007001.
                res_code = hvc_p2_api.save_album_to_flash()
                if res_code is not p2def.RESPONSE_CODE_NORMAL:
                    print "Error: Invalid save album to flash."
                    break
                print ("Success to delete album.")

    except KeyboardInterrupt:
        time.sleep(1)

    finally:
        hvc_p2_api.set_uart_baudrate(p2def.DEFAULT_BAUD)
        hvc_p2_api.disconnect()

if __name__ == '__main__':
    main()

