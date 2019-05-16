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

class C_POINT(Structure):
    _fields_ = [("nX", c_int),
                ("nY", c_int)]


class C_FRAME_RESULT_DIRECTION(Structure):
    """Face direction estimation"""
    _fields_ = [("nLR", c_int),
                ("nUD", c_int),
                ("nRoll", c_int),
                ("nConfidence", c_int)]


class C_FRAME_RESULT_AGE(Structure):
    """Age estimation"""
    _fields_ = [("nAge", c_int),
                ("nConfidence", c_int)]


class C_FRAME_RESULT_GENDER(Structure):
    """Gender estimation"""
    _fields_ = [("nGender", c_int),
                ("nConfidence", c_int)]


class C_FRAME_RESULT_GAZE(Structure):
    """Gaze estimation"""
    _fields_ = [("nLR", c_int),
                ("nUD", c_int)]


class C_FRAME_RESULT_BLINK(Structure):
    """ Blink estimation"""
    _fields_ = [("nLeftEye", c_int),
                ("nRightEye", c_int)]


class C_FRAME_RESULT_EXPRESSION(Structure):
    """Facial expression estimation"""
    _fields_ = [("anScore", c_int*5),
                ("nDegree", c_int)]


class C_FRAME_RESULT_RECOGNITION(Structure):
    """Face recognition"""
    _fields_ = [("nUID", c_int),
                ("nScore", c_int)]


class C_FRAME_RESULT_DETECTION(Structure):
    """One detection result"""
    _fields_ = [("center", C_POINT),
                ("nSize", c_int),
                ("nConfidence", c_int)]


class C_FRAME_RESULT_FACE(Structure):
    """Face detection and post-processing result (1 person)"""
    _fields_ = [("center", C_POINT),
                ("nSize", c_int),
                ("nConfidence", c_int),
                ("direction", C_FRAME_RESULT_DIRECTION),
                ("age", C_FRAME_RESULT_AGE),
                ("gender", C_FRAME_RESULT_GENDER),
                ("gaze", C_FRAME_RESULT_GAZE),
                ("blink", C_FRAME_RESULT_BLINK),
                ("expression", C_FRAME_RESULT_EXPRESSION),
                ("recognition", C_FRAME_RESULT_RECOGNITION)]


class C_FRAME_RESULT_BODYS(Structure):
    """One Human body detection result"""
    _fields_ = [("nCount", c_int),
                ("body", C_FRAME_RESULT_DETECTION * 35)]


class C_FRAME_RESULT_FACES(Structure):
    """Face detection and post-processing result (1 frame)"""
    _fields_ = [("nCount", c_int),
                ("face", C_FRAME_RESULT_FACE * 35)]


class C_FRAME_RESULT(Structure):
    """FRAME result (1 frame)"""
    _fields_ = [("bodys", C_FRAME_RESULT_BODYS),
                ("faces", C_FRAME_RESULT_FACES)]
