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

from ctypes import *

# STB Tracking status
STB_STATUS_NO_DATA     =-1
STB_STATUS_CALCULATING = 0
STB_STATUS_COMPLETE    = 1
STB_STATUS_FIXED       = 2

STB_TRID_NOT_TRACKED = -1



class C_RES(Structure):
    """General purpose stabilization result structure"""
    _fields_ = [("status", c_int),  # STATUS
                ("conf", c_int),
                ("value", c_int)]


class C_GAZE(Structure):
    """Result of Gaze estimation"""
    _fields_ = [("status", c_int),  # STATUS
                ("conf", c_int),
                ("UD", c_int),
                ("LR", c_int)]


class C_DIRECTION(Structure):
    """Result of Face direction estimation"""
    _fields_ = [("status", c_int),  # STATUS
                ("conf", c_int),
                ("yaw", c_int),
                ("pitch", c_int),
                ("roll", c_int)]


class C_BLINK(Structure):
    """Result of Blink estimation"""
    _fields_ = [("status", c_int),  # STATUS
                ("ratioL", c_int),
                ("ratioR", c_int)]


class C_POS(Structure):
    """Detection position structure"""
    _fields_ = [("x", c_uint),
                ("y", c_uint)]



class C_FACE(Structure):
    """Face stabilization result structure"""
    _fields_ = [("nDetectID", c_int),
                ("nTrackingID", c_int),
                ("center", C_POS),
                ("nSize", c_uint),
                ("conf", c_int),
                ("direction", C_DIRECTION),
                ("age", C_RES),
                ("gender", C_RES),
                ("gaze", C_GAZE),
                ("blink", C_BLINK),
                ("expression", C_RES),
                ("recognition", C_RES)]

C_FACE_RES35 = C_FACE * 35


class C_BODY(Structure):
    """Human body stabilization result structure"""
    _fields_ = [("nDetectID", c_int),
                ("nTrackingID", c_int),
                ("center", C_POS),
                ("nSize", c_uint),
                ("conf", c_int)]

C_BODY_RES35 = C_BODY * 35