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

# Exceute function flag definition
EX_NONE        =  0x00
EX_BODY        =  0x01
EX_HAND        =  0x02
EX_FACE        =  0x04
EX_DIRECTION   =  0x08
EX_AGE         =  0x10
EX_GENDER      =  0x20
EX_GAZE        =  0x40
EX_BLINK       =  0x80
EX_EXPRESSION  = 0x100
EX_RECOGNITION = 0x200
EX_ALL = EX_BODY + EX_HAND + EX_FACE + EX_DIRECTION + EX_AGE + EX_GENDER\
       + EX_GAZE + EX_BLINK + EX_EXPRESSION + EX_RECOGNITION

# STB library ON/OFF flag
USE_STB_ON  = True
USE_STB_OFF = False

# output image type definition
OUT_IMG_TYPE_NONE  = 0x00
OUT_IMG_TYPE_QVGA  = 0x01
OUT_IMG_TYPE_QQVGA = 0x02

# HVC camera angle definition.
HVC_CAM_ANGLE_0   = 0x00
HVC_CAM_ANGLE_90  = 0x01
HVC_CAM_ANGLE_180 = 0x02
HVC_CAM_ANGLE_270 = 0x03

# Face angel definitions.
HVC_FACE_ANGLE_YAW_30  = 0x00  # Yaw angle:-30 to +30 degree (Frontal face)
HVC_FACE_ANGLE_YAW_60  = 0x01  # Yaw angle:-60 to +60 degree (Half-Profile face)
HVC_FACE_ANGLE_YAW_90  = 0x02  # Yaw angle:-90 to +90 degree (Profile face)
HVC_FACE_ANGLE_ROLL_15 = 0x00  # Roll angle:-15 to +15 degree
HVC_FACE_ANGLE_ROLL_45 = 0x01  # Roll angle:-45 to +45 degree

# Available serial baudrate sets
AVAILABLE_BAUD = (9600, 38400, 115200, 230400, 460800, 921600)

DEFAULT_BAUD = 9600

# Response code
RESPONSE_CODE_PLURAL_FACE = 0x02  # Number of faces that can be registerd is 0
RESPONSE_CODE_NO_FACE     = 0x01  # Number of detected faces is 2 or more
RESPONSE_CODE_NORMAL      = 0x00  # Normal end
RESPONSE_CODE_UNDEFINED   = 0xFF  # Undefined error
RESPONSE_CODE_INTERNAL    = 0xFE  # Intenal error
RESPONSE_CODE_INVALID_CMD = 0xFD  # Improper command

# Estimation common result status
EST_NOT_POSSIBLE = -128

# Expression result
EXP_UNKNOWN   =-1
EXP_NEUTRAL   = 0
EXP_HAPPINESS = 1
EXP_SURPRISE  = 2
EXP_ANGER     = 3
EXP_SADNESS   = 4

# Gender result
GENDER_UNKNOWN = -1
GENDER_FEMALE = 0
GENDER_MALE = 1

# Recognition result
RECOG_NOT_POSSIBLE = -128
RECOG_NO_DATA_IN_ALBUM = -127
